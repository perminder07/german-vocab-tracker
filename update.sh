#!/bin/bash

# 1. Get the current day of the month (e.g., "01", "15", "30")
DAY=$(date +%d)

# 2. Only run the Python script if today is exactly the 1st or 15th
if [ "$DAY" = "01" ] || [ "$DAY" = "15" ]; then
    echo "Scheduled date detected. Generating new vocabulary chart..."
    python3 generate_chart.py
else
    echo "Off-schedule run. Skipping chart generation to protect the 15-day timeline."
fi

# 3. Stage and commit any modified files
git add .
git commit -m "Repository sync: $(date +'%Y-%m-%d')"

# 4. Push to GitHub
git push origin main