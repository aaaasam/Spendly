Spendly — Expense Tracker

A sleek, dark-themed expense tracker built with Flask + SQLite + Chart.js.

## Features
- ✅ Add expenses with title, amount, category, date, note
- ✅ Category filters (Food, Transport, Housing, Entertainment, Health, Shopping, Education, Other)
- ✅ Month filter
- ✅ Monthly bar chart (trend over last 12 months)
- ✅ Category donut chart
- ✅ Live stats: monthly total, all-time total, top category, daily average
- ✅ Export to CSV (respects active filters)
- ✅ SQLite persistence — data survives restarts
- ✅ Demo data pre-loaded

## Setup

```bash
cd expense-tracker
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5000

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (via built-in `sqlite3`)
- **Charts**: Chart.js 4.4
- **Fonts**: Syne + DM Mono (Google Fonts)

