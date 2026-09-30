# German Vocabulary Tracker (DTZ B1)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

## Live Progress
![Vocabulary Progress](progress-chart.png)

A fully automated, local-first data pipeline and visualization dashboard built to track my progression in learning German vocabulary for the DTZ B1 examination. 

This project bridges language acquisition with data engineering, transforming daily study habits into structured data, automated visual reports, and a version-controlled portfolio.

## 🏗 System Architecture & Tech Stack

The system utilizes a decoupled architecture, relying on local microservices and automated bash scripting to extract, transform, load (ETL), and visualize data.

1. **Frontend (User Interface):** Vanilla `HTML5`, `CSS3`, and `JavaScript`. Serves as the interactive dashboard where vocabulary is categorized (Nomen, Adjektive, Verben, Verben mit Präpositionen) and checked off as "learned."
2. **Backend & API:** `n8n` (running in a local Docker container). Acts as the webhook listener and data router.
3. **Database:** `n8n Data Tables`. A local SQLite-backed table (`current_progress`) that stores the latest integer counts for each vocabulary category.
4. **Data Visualization:** `Python 3` (`Pandas`, `Matplotlib`). Fetches the live JSON payload from the n8n API, cleans the data, appends it to a historical `progress.csv` ledger, and renders a multi-line time-series graph.
5. **Deployment & Automation:** `Bash` + macOS `cron` + `Git/GitHub`. A scheduled cron job silently executes the pipeline bi-weekly, commits the updated CSV and PNG artifacts, and pushes them to this repository.

## ⚙️ How It Works (The Workflow)

1. **Data Entry:** I open `index.html` locally in my browser and check off newly memorized words.
2. **Event Trigger:** The JavaScript listens for checkbox state changes and immediately fires a `POST` request to the local n8n webhook containing the aggregate counts for all four categories.
3. **Data Storage:** The n8n Upsert node overwrites the single row in the `current_progress` data table with the fresh counts.
4. **Scheduled Execution:** On the 1st and 15th of the month, macOS `cron` triggers `update.sh` in the background (provided the machine is awake and Docker is running).
5. **Chart Generation:** The bash script triggers `generate_chart.py`, which hits a `GET` webhook in n8n, retrieves the current numbers, updates the local CSV ledger, and overwrites `progress-chart.png`.
6. **Version Control:** The bash script automatically stages, commits with a timestamp, and pushes the updates to GitHub, keeping the visual timeline on this README permanently up to date.

## ⚖️ System Analysis

### Advantages
* **Zero Cloud Costs:** By running n8n and the database locally via Docker, the entire infrastructure is free.
* **Complete Data Ownership:** The historical ledger (`progress.csv`) and the raw application state are entirely contained on my local machine.
* **Modular Design:** The Python visualization engine and the n8n database are loosely coupled via an API, meaning I can easily swap out the frontend or the database without breaking the chart generator.
* **Frictionless Routine:** The `cron` automation removes the need to manually execute scripts. I simply study, and the reporting handles itself.

### Disadvantages & Compromises
* **Device Dependency (The Cron Trap):** The automation relies on macOS `cron`. If the laptop lid is closed on the 1st or 15th, the execution is skipped entirely until the next cycle.
* **Resource Overhead:** Docker Desktop must be running in the background to capture the webhook events, which consumes RAM and impacts laptop battery life.
* **Local-Only State:** Because `index.html` relies on the browser's `localStorage` for visual state (keeping boxes checked upon refresh) and n8n for numerical state, I cannot seamlessly switch to my phone or another computer to study without losing sync.

## 🧠 Key Learnings
* **API Payload Mapping:** I learned how to structure JSON payloads in frontend `fetch()` requests and map them accurately into database columns using n8n expressions (`{{ $json.body.nomen }}`).
* **Browser Caching Pitfalls:** I encountered and resolved an issue where Chrome cached an older version of the JavaScript payload, sending mismatched data schemas to the database, which resulted in `Null` values crashing the Matplotlib timeline.
* **Data Sanitization in Python:** I implemented robust error handling in `generate_chart.py` to intercept `Null` or empty payloads, forcing fallback values (`0`) and generating CSV headers dynamically if the file is wiped.

## 🚀 Future Roadmap

* **Automated Semantic Versioning:** Implement a script to detect modifications in `index.html` (e.g., adding new vocabulary words) and automatically bump the patch version (e.g., `v1.0.1` -> `v1.0.2`), applying Git Tags to track vocabulary expansion over time.
* **Cloud Database Migration:** Replace local n8n Data Tables with a cloud solution (like Supabase or Firebase) to decouple the system from Docker and enable cross-device studying.
* **GitHub Pages Hosting:** Deploy the frontend to GitHub Pages so the tracker can be accessed and used via mobile while commuting.
* **Power BI Integration:** Connect the n8n API endpoint directly to Microsoft Power BI to build an interactive, drill-down dashboard of my learning habits.
