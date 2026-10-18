#!/usr/bin/env bash
# Daily pipeline: refresh chart data, cut a patch release when vocab.js changed, push to GitHub.
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

# Helper function to push safely without crashing when offline
safe_push() {
    local target="${1:-$BRANCH}"
    if git push origin "$target"; then
        echo "Push to GitHub succeeded ($target)."
    else
        echo "WARNING: Push failed (likely offline/no internet). Changes remain safely committed locally and will push when online."
    fi
}

# 1. Data pipeline: (only run if invoked with --chart) fetch counts from n8n, append to progress.csv, redraw the chart
if [ "${1:-}" = "--chart" ]; then
    echo "Chart update requested via --chart flag..."
    "$PY" scripts/generate_chart.py
else
    echo "No --chart flag provided. Skipping chart generation to preserve the 1st/15th schedule."
fi

# 2. Release when the vocabulary changed
if [ -n "$(git status --porcelain -- vocab.js)" ]; then
    echo "vocab.js changed: validating and automating a PATCH release..."
    "$PY" scripts/validate_vocab.py --assign-ids
    "$PY" scripts/bump_version.py patch
    NEW_VERSION="$(tr -d '[:space:]' < version.txt)"

    git add vocab.js version.txt README.md index.html
    git commit -m "Add new vocabulary (Auto-Release v${NEW_VERSION})"
    git tag -a "v${NEW_VERSION}" -m "Vocabulary Update v${NEW_VERSION}"
    safe_push "$BRANCH"
    safe_push "v${NEW_VERSION}"
else
    echo "No vocabulary changes detected."
fi

# 3. Chart/ledger updates
if [ -n "$(git status --porcelain -- data/progress.csv data/progress-chart.png)" ]; then
    git add data/progress.csv data/progress-chart.png
    git commit -m "Repository sync: $(date +%Y-%m-%d)"
fi

# 4. Push any unpushed local commits (catches up if a previous run was offline)
UNPUSHED="$(git log "origin/${BRANCH}..${BRANCH}" --oneline 2>/dev/null || true)"
if [ -n "$UNPUSHED" ]; then
    echo "Unpushed commits detected. Attempting sync..."
    safe_push "$BRANCH"
fi

echo "=== done ==="