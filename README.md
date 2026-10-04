# German Vocabulary Tracker (DTZ B1)
![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)

## Live Progress
![Vocabulary Progress](progress-chart.png)

A fully automated, local-first data pipeline and visualization dashboard built to track my progression in learning German vocabulary for the DTZ B1 examination. 

This project bridges language acquisition with data engineering, transforming daily study habits into structured data, automated visual reports, and a version-controlled portfolio.

## System Architecture & Tech Stack

The system utilizes a decoupled architecture, relying on local microservices, a separated data layer, and automated bash scripting to extract, transform, load (ETL), visualize data, and manage versions.

1. **Frontend (User Interface):** Vanilla `HTML5`, `CSS3`, and `JavaScript`. Operating as a Single Page Application (SPA), it dynamically generates interactive tables and DOM elements on the fly by reading the decoupled data layer.
2. **Data Layer (Database):** `vocab.js`. Acts as the local offline database containing over 400 vocabulary entries. It utilizes the "JS Data Variable" pattern to bypass local browser CORS restrictions, allowing the app to run completely offline without a local web server.
3. **Backend & API:** `n8n` (running in a local Docker container). Acts as the webhook listener and data router.
4. **Metrics Database:** `n8n Data Tables`. A local SQLite-backed table (`current_progress`) that stores the latest integer counts for each vocabulary category.
5. **Data Visualization:** `Python 3` (`Pandas`, `Matplotlib`). Fetches the live JSON payload from the n8n API, cleans the data, appends it to a historical `progress.csv` ledger, and renders a multi-line time-series graph.
6. **Deployment & CI/CD Automation:** `Bash` + `Python` + macOS `cron`. The `update.sh` pipeline acts as a CI/CD runner. It detects changes in the vocabulary database, automatically triggers a custom Python Semantic Versioning script (`bump_version.py`) to apply PATCH updates, generates new chart artifacts, tags the release, and pushes to GitHub.

## How It Works (The Workflow)

1. **Vocabulary Expansion:** I add new German words directly to the `vocab.js` data dictionary.
2. **Auto-Release:** Running `./update.sh` detects the new data, automatically rolls the semantic version (e.g., v2.0.1 -> v2.0.2), tags the Git commit, and pushes the release to GitHub.
3. **Data Entry:** I open `index.html` locally in my browser (double-click, no server required) and check off newly memorized words.
4. **Event Trigger:** The JavaScript listens for checkbox state changes, computes the true total from the underlying JSON array, and fires a `POST` request to the local n8n webhook.
5. **Data Storage:** The n8n Upsert node overwrites the single row in the `current_progress` data table with the fresh counts.
6. **Scheduled Execution & Charting:** On a cron schedule, the pipeline retrieves the latest numbers via a `GET` webhook, updates the CSV ledger, generates `progress-chart.png`, and commits the visual timeline.
7. **Version Control:** The bash script automatically stages, commits with a timestamp, and pushes the updates to GitHub, keeping the visual timeline on this README permanently up to date.

## System Analysis

### Advantages
* **Decoupled Architecture:** Separating the presentation layer (`index.html`) from the database (`vocab.js`) ensures UI bugs do not impact data integrity and eliminates DOM-counting state errors.
* **Zero Cloud Costs:** By running n8n and the database locally via Docker, the entire infrastructure is free.
* **Complete Data Ownership:** The historical ledger (`progress.csv`), the vocabulary database, and the raw application state are entirely contained on my local machine.
* **Frictionless Routine:** The CI/CD Bash automation and cron jobs remove the need to manually execute scripts or manage minor Git tags. I simply study or add words, and the reporting handles itself.

### Disadvantages & Compromises
* **Device Dependency (The Cron Trap):** The automation relies on macOS `cron`. If the laptop lid is closed on the scheduled day, the execution is skipped entirely until the next cycle.
* **Resource Overhead:** Docker Desktop must be running in the background to capture the webhook events, which consumes RAM and impacts laptop battery life.
* **Single-Device State:** Because the app relies on the browser's local `localStorage` to map UI checkmarks to the offline `vocab.js` IDs, cross-device syncing (e.g., studying on a phone) is not supported without migrating to a cloud database.

## Key Learnings
* **API Payload Mapping:** I learned how to structure JSON payloads in frontend `fetch()` requests and map them accurately into database columns using n8n expressions (`{{ $json.body.nomen }}`).
* **State Management:** I discovered the pitfalls of tying logic to the DOM (visual row counting) which broke when UI filters were applied. Migrating to an SPA pattern that computes totals strictly from the underlying data arrays permanently solved state mismatch bugs.
* **Data Sanitization in Python:** I implemented robust error handling in `generate_chart.py` to intercept `Null` or empty payloads, forcing fallback values (`0`) and generating CSV headers dynamically if the file is wiped.

## Version History & Progression

* **`v2.1.0`** - **Offline-First SPA:** Transitioned the data layer from `vocab.json` to `vocab.js`, resolving CORS security blocks and enabling serverless, double-click offline execution.
* **`v2.0.1`** - **CI/CD Pipeline:** Upgraded `update.sh` to auto-detect vocabulary additions, bundle automatic PATCH releases, and expanded the database from ~~285~~ -> 400 B1 words.
* **`v2.0.0`** - **Decoupled Architecture (Major):** Migrated the static HTML monolith into a dynamic Single Page Application (SPA), isolating data into a dedicated JSON database to fix DOM-counting state bugs.
* **`v1.0.1`** - **State Patch:** Resolved local browser cache mismatches crashing the Python Matplotlib generator.
* **`v1.0.0`** - **Initial Launch:** Static HTML vocabulary tracker connected to local n8n Docker webhooks with automated Python chron-job visualizations.

## Future Roadmap

* ~~**Automated Semantic Versioning:** Implement a script to detect modifications in `index.html` (e.g., adding new vocabulary words) and automatically bump the patch version (e.g., `v1.0.1` -> `v1.0.2`), applying Git Tags to track vocabulary expansion over time.~~ *(Completed in v2.0.1)*
* **Cloud Database Migration:** Replace local n8n Data Tables with a cloud solution (like Supabase or Firebase) to decouple the system from Docker and enable cross-device studying.
* **GitHub Pages Hosting:** Deploy the frontend to GitHub Pages so the tracker can be accessed and used via mobile while commuting.
* **Power BI Integration:** Connect the n8n API endpoint directly to Microsoft Power BI to build an interactive, drill-down dashboard of my learning habits.
