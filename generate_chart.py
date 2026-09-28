import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib.request
import json
from datetime import datetime

# 1. Fetch live score from n8n Data Table
try:
    url = "http://localhost:5678/webhook/current-score"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode())
    live_score = data['score']
    
    today = datetime.now().strftime('%Y-%m-%d')
    df_new = pd.DataFrame({'Date': [today], 'Score': [live_score]})
    df_new.to_csv('progress.csv', mode='a', header=False, index=False)
    print(f"Successfully fetched live score: {live_score}")
except Exception as e:
    print(f"Could not fetch live score from n8n. Error: {e}")

# 2. Read, clean, and chronologically sort the data
df = pd.read_csv('progress.csv')
df = df.drop_duplicates(subset=['Date'], keep='last')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df.to_csv('progress.csv', index=False, date_format='%Y-%m-%d')

# 3. Draw the chart with anti-compression formatting
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['Date'], df['Score'], marker='o', linestyle='-', color='#5bcc6b', linewidth=2.5)

# 4. Auto-format X-axis to prevent overlapping dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
fig.autofmt_xdate(rotation=45)

# 5. Styling
ax.set_title('DTZ B1 Vocabulary Progress', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Words Learned', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 6. Save image
plt.savefig('progress-chart.png')
print("Success: progress-chart.png has been generated!")