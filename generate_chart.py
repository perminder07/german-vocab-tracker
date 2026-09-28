import pandas as pd
import matplotlib.pyplot as plt

# 1. Read the historical progress data
df = pd.read_csv('progress.csv')

# 2. Configure and draw a clean line chart
plt.figure(figsize=(10, 5))
plt.plot(df['Date'], df['Score'], marker='o', linestyle='-', color='#5bcc6b', linewidth=2.5)

# 3. Add styling, labels, and gridlines
plt.title('DTZ B1 Vocabulary Progress', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=11)
plt.ylabel('Words Learned', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# 4. Save the chart as an image file for GitHub
plt.savefig('progress-chart.png')
print("Success: progress-chart.png has been generated!")