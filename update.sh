#!/bin/bash

# 1. Run the Python script to generate the latest chart
python3 generate_chart.py

# 2. Stage all modified files (CSV and PNG)
git add .

# 3. Commit the changes with an automated timestamp
git commit -m "Auto-update progress chart: $(date +'%Y-%m-%d')"

# 4. Push the changes live to GitHub
git push origin main

echo "Successfully updated and pushed progress to GitHub!"