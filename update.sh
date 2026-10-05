#!/usr/bin/env bash
# Daily pipeline: refresh chart data, cut a patch release when vocab.js changed, push to GitHub.
# Safe to run from cron/launchd: it cd's into its own folder, logs to logs/update.log,
# takes a lock, and stops at the first error instead of carrying on half-finished.
set -euo pipefail

cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

mkdir -p logs
if [ -t 1 ]; then exec > >(tee -a logs/update.log) 2>&1; else exec >>logs/update.log 2>&1; fi
echo "=== $(date '+%Y-%m-%d %H:%M:%S') update.sh start ==="

LOCKDIR="logs/.update.lock"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "Another run is active (remove $LOCKDIR if that is stale). Exiting."
    exit 0
fi
trap 'rmdir "$LOCKDIR"' EXIT

if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# 1. Data pipeline: fetch counts from n8n, append to progress.csv, redraw the chart
"$PY" generate_chart.py

# 2. Release when the vocabulary changed
if [ -n "$(git status --porcelain -- vocab.js)" ]; then
    echo "vocab.js changed: validating and automating a PATCH release..."
    "$PY" validate_vocab.py --assign-ids      # aborts the run on any error
    "$PY" bump_version.py patch
    NEW_VERSION="$(tr -d '[:space:]' < version.txt)"

    git add vocab.js version.txt README.md index.html
    git commit -m "Add new vocabulary (Auto-Release v${NEW_VERSION})"
    git tag -a "v${NEW_VERSION}" -m "Vocabulary Update v${NEW_VERSION}"
    git push origin "$BRANCH" "v${NEW_VERSION}"      # only this tag, not every local tag
else
    echo "No vocabulary changes detected."
fi

# 3. Chart/ledger updates
if [ -n "$(git status --porcelain -- progress.csv progress-chart.png)" ]; then
    git add progress.csv progress-chart.png
    git commit -m "Repository sync: $(date +%Y-%m-%d)"
    git push origin "$BRANCH"
fi

echo "=== done ==="
