#!/bin/bash

# 1. Run your background data pipeline
python3 generate_chart.py

# 2. Check if vocabulary data was modified
if git status --porcelain | grep -q "vocab.json"; then
    echo "New vocabulary detected. Automating PATCH release..."
    
    # Run the version bumper
    python3 bump_version.py patch
    
    # Read the newly generated version number
    NEW_VERSION=$(cat version.txt)
    
    # Stage and commit the vocabulary and version files
    git add vocab.json version.txt README.md index.html
    git commit -m "Add new vocabulary (Auto-Release v${NEW_VERSION})"
    
    # Attach the tag
    git tag -a "v${NEW_VERSION}" -m "Vocabulary Update v${NEW_VERSION}"
    
    # Push the changes AND the new tag to GitHub
    git push origin main --tags
else
    echo "No vocabulary changes detected."
fi

# 3. Handle standard chart updates (if any)
if git status --porcelain | grep -q "progress.csv"; then
    git add progress.csv progress-chart.png
    git commit -m "Repository sync: $(date +%Y-%m-%d)"
    git push origin main
fi