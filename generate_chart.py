import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib.request
import json
import os
from datetime import datetime

# 1. Fetch live score from n8n Data Table
try:
    url = "http://localhost:5678/webhook/current-score"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode())
    
    # Safely get data; if n8n sends Null (None), default to 0
    nomen = data.get('nomen') or 0
    adjektive = data.get('adjektive') or 0
    verben = data.get('verben') or 0
    praep = data.get('praepositionen') or 0
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create the CSV with headers if it doesn't exist OR if it is empty (0 bytes)
    if not os.path.isfile('progress.csv') or os.path.getsize('progress.csv') == 0:
        with open('progress.csv', 'w') as f:
            f.write("Date,Nomen,Adjektive,Verben,Praepositionen\n")
            
    df_new = pd.DataFrame({'Date': [today], 'Nomen': [nomen], 'Adjektive': [adjektive], 'Verben': [verben], 'Praepositionen': [praep]})
    df_new.to_csv('progress.csv', mode='a', header=False, index=False)
    print(f"Successfully fetched live data - Nomen: {nomen}, Adjektive: {adjektive}, Verben: {verben}, Präp: {praep}")
except Exception as e:
    print(f"Could not fetch live score from n8n. Error: {e}")

# 2. Read, clean, and chronologically sort the data
try:
    df = pd.read_csv('progress.csv')
    df = df.drop_duplicates(subset=['Date'], keep='last')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df.to_csv('progress.csv', index=False, date_format='%Y-%m-%d')

    # 3. Draw the multi-line chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['Date'], df['Nomen'], marker='o', color='#3498db', linewidth=2.5, label='Nomen')
    ax.plot(df['Date'], df['Adjektive'], marker='o', color='#e67e22', linewidth=2.5, label='Adjektive')
    ax.plot(df['Date'], df['Verben'], marker='o', color='#2ecc71', linewidth=2.5, label='Verben')
    ax.plot(df['Date'], df['Praepositionen'], marker='o', color='#9b59b6', linewidth=2.5, label='Verben m. Präp.')

    # 4. Auto-format X-axis to prevent overlapping dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=45)

    # 5. Styling
    ax.set_title('DTZ B1 Vocabulary Progress by Category', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Words Learned', fontsize=11)
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 6. Save image
    plt.savefig('progress-chart.png')
    print("Success: Multi-line chart generated!")
except Exception as e:
    print(f"Chart generation failed. Check if progress.csv is formatted correctly. Error: {e}")