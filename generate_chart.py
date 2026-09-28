import pandas as pd
import matplotlib.pyplot as plt
import urllib.request
import json
from datetime import datetime

# 1. Fetch live score from n8n Data Table
try:
    url = "http://localhost:5678/webhook/current-score"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode())
    live_score = data['score']  # Extracts the number from the n8n JSON
    
    # 2. Append today's date and live score to the CSV
    today = datetime.now().strftime('%Y-%m-%d')
    df_new = pd.DataFrame({'Date': [today], 'Score': [live_score]})
    df_new.to_csv('progress.csv', mode='a', header=False, index=False)
    print(f"Successfully fetched live score: {live_score}")
except Exception as e:
    print("Could not fetch live score from n8n. Using existing CSV data.")

# 3. Read the CSV and clean up any duplicate entries for the same day
df = pd.read_csv('progress.csv')
df = df.drop_duplicates(subset=['Date'], keep='last')
df.to_csv('progress.csv', index=False)

# 4. Draw the chart
plt.figure(figsize=(10, 5))
plt.plot(df['Date'], df['Score'], marker='o', linestyle='-', color='#5bcc6b', linewidth=2.5)

# 5. Styling
plt.title('DTZ B1 Vocabulary Progress', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=11)
plt.ylabel('Words Learned', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 6. Save image
plt.savefig('progress-chart.png')
print("Success: progress-chart.png has been generated!")