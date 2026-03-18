# Kensite Breakdown Tracker

A Streamlit web application for logging and tracking breakdown callouts across Kensite's hire fleet. Data is persisted in a **JSON file stored directly in this GitHub repo** — the same approach used by the Kensite Prep Schedule.

---

## Features

- **Calendar view** — monthly grid showing daily WO counts at a glance
- **Day view** — detailed WO list with live progress indicator pills
- **Add / Edit WOs** — full form with all fields and checklist
- **Week summaries** — category breakdown and running charge totals per week
- **Month summary** — sidebar totals for WO count, chargeable jobs, and invoiced value

---

## How data persistence works

Every time a work order is saved or deleted, the app commits an updated `data/breakdowns.json` file to this repo via the GitHub API. Streamlit Cloud reads from the same file. This means data survives redeployments, container restarts, and sleeping apps — exactly like the Prep Schedule.

---

## One-time Setup: GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name (e.g. `kensite-breakdown-tracker`)
4. Set expiration to **No expiration** (or 1 year)
5. Tick the **`repo`** scope (full repo access)
6. Click **Generate token** — copy it immediately, you won't see it again

---

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → connect repo → set `app.py` as entry point
3. Click **Advanced settings** → **Secrets** and paste:

```toml
GITHUB_TOKEN  = "ghp_xxxxxxxxxxxxxxxxxxxx"
GITHUB_REPO   = "your-username/kensite-breakdown-tracker"
GITHUB_BRANCH = "main"
```

4. Deploy — the app will create `data/breakdowns.json` in your repo on first save

---

## Local Development

Create `.streamlit/secrets.toml` (already gitignored):

```toml
GITHUB_TOKEN  = "ghp_xxxxxxxxxxxxxxxxxxxx"
GITHUB_REPO   = "your-username/kensite-breakdown-tracker"
GITHUB_BRANCH = "main"
```

Then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Brand

Kensite Services Ltd — Complete Site Solutions  
Primary: #0d823b | Text: #40424a | Font: Figtree (Google Fonts)
