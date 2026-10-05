#!/usr/bin/env python3
"""Fetch the current learning counts from n8n, append them to progress.csv and redraw the chart.

Usage:
    python3 generate_chart.py             # fetch, append today's row, redraw
    python3 generate_chart.py --no-fetch  # only redraw from progress.csv

Configuration (environment variables, or a git-ignored .env file next to this script):
    N8N_SCORE_URL   GET webhook URL   (default http://localhost:5678/webhook/current-score)
    N8N_TOKEN       value for the X-Api-Key header (needed if the webhook uses Header Auth)
"""
import csv
import json
import math
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless: works under cron/launchd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # Points to project root
CSV_PATH = ROOT / "data/progress.csv"
PNG_PATH = ROOT / "data/progress-chart.png"
FIELDS = ["Nomen", "Adjektive", "Verben", "Praepositionen"]
API_KEYS = ["nomen", "adjektive", "verben", "praepositionen"]   # JSON keys sent by n8n
HEADER = ["Date"] + FIELDS


def load_env_file():
    env = ROOT / ".env"  # Looks for .env in the project root
    if not env.exists():
        return
    for line in env.read_text(encoding="utf8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fetch_counts():
    """Return a list of 4 ints, or None (with a message) if the data is missing or invalid."""
    url = os.environ.get("N8N_SCORE_URL", "http://localhost:5678/webhook/current-score")
    req = urllib.request.Request(url)
    if os.environ.get("N8N_TOKEN"):
        req.add_header("X-Api-Key", os.environ["N8N_TOKEN"])
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"WARNING: could not fetch live score from n8n ({e}). Chart redrawn from existing CSV only.")
        return None
    values = []
    for key in API_KEYS:
        v = data.get(key) if isinstance(data, dict) else None
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or int(v) != v:
            print(f"WARNING: n8n returned {key!r}={v!r} (missing/invalid). No row appended; "
                  "a made-up 0 would corrupt the history.")
            return None
        values.append(int(v))
    return values


def append_row(values):
    today = datetime.now().strftime("%Y-%m-%d")
    new_file = not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0
    with open(CSV_PATH, "a", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(HEADER)
        w.writerow([today] + values)
    print("Fetched live data - " + ", ".join(f"{k}: {v}" for k, v in zip(FIELDS, values)))


def clean_ledger():
    df = pd.read_csv(CSV_PATH)
    for col in FIELDS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=FIELDS)
    df[FIELDS] = df[FIELDS].astype(int)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.drop_duplicates(subset=["Date"], keep="last").sort_values("Date").reset_index(drop=True)
    df.to_csv(CSV_PATH, index=False, date_format="%Y-%m-%d")
    # Early-warning for the "browser with empty storage overwrote n8n" failure mode
    if len(df) >= 2:
        prev, last = df.iloc[-2], df.iloc[-1]
        dropped = [f for f in FIELDS if last[f] < prev[f]]
        if dropped:
            print(f"WARNING: counts dropped since {prev['Date']:%Y-%m-%d} for {', '.join(dropped)}. "
                  "If that was not intentional, check the browser/profile you tick words in.")
    return df


def draw(df):
    fig, ax = plt.subplots(figsize=(11, 6))
    series = [
        ("Nomen", "#3498db", "Nomen"), 
        ("Adjektive", "#e67e22", "Adjektive"),
        ("Verben", "#2ecc71", "Verben"), 
        ("Praepositionen", "#9b59b6", "Verben m. Präp.")
    ]
    
    for col, color, label in series:
        ax.plot(df["Date"], df[col], marker="o", color=color, linewidth=2.5, label=label)
        
        # Annotate each data point with its exact word count value
        for x, y in zip(df["Date"], df[col]):
            ax.annotate(
                str(int(y)),
                (x, y),
                textcoords="offset points",
                xytext=(0, 7),  # Shifts the number 7 points above the dot
                ha='center',
                fontsize=8,
                fontweight='semibold',
                color='#2c3e50'
            )

    span_days = max((df["Date"].max() - df["Date"].min()).days, 1)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, math.ceil(span_days / 8))))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate(rotation=45)
    ax.set_title("DTZ B1 Vocabulary Progress by Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Words Learned", fontsize=11)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close(fig)
    print("Success: multi-line chart generated with data labels.")


def main():
    load_env_file()
    if "--no-fetch" not in sys.argv:
        values = fetch_counts()
        if values is not None:
            append_row(values)
    if not CSV_PATH.exists():
        sys.exit("progress.csv does not exist yet and no data could be fetched.")
    try:
        draw(clean_ledger())
    except Exception as e:
        sys.exit(f"Chart generation failed. Check that progress.csv is well-formed. Error: {e}")


if __name__ == "__main__":
    main()
