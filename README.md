# Collection CSV Exporter — Standalone Script

Downloads every collection from the site's export form as a CSV file.
No browser extension needed — runs directly from your terminal.

---

## Quick Setup (do this once)

### 1. Install Python
Make sure Python 3 is installed: https://python.org/downloads

### 2. Install dependencies
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
playwright install chrome
```

### 3. Edit config.py
Open `config.py` and set:
- `PAGE_URL` — the URL of the page with the export form
- `OUTPUT_DIR` — where you want the CSV files saved

---

## Running the script

**Normal run:**
```bash
python export_collections.py
```

**Save to a specific folder:**
```bash
python export_collections.py --out ~/Desktop/my-exports
```

**Use a different URL:**
```bash
python export_collections.py --url https://example.com/settings
```

**Re-login (clear saved session):**
```bash
python export_collections.py --reset-login
```

---

## How it works

1. **First run** — Chrome opens and shows the site. Log in normally.
   The script detects when you're on the right page and continues automatically.
   Your session (cookies) is saved to `.session.json` so you won't need to log in again.

2. **Future runs** — The saved session is loaded and Chrome goes straight to the
   export page without requiring a login.

3. The script finds all collections in the dropdown, POSTs the export form for each
   one, and saves the resulting CSV files to your chosen folder.

---

## Files

| File | Purpose |
|------|---------|
| `export_collections.py` | Main script |
| `config.py` | Your settings (URL, output folder) |
| `requirements.txt` | Python dependencies |
| `.session.json` | Saved login session (auto-created, don't share this) |

---

## Troubleshooting

**"Export form not found on the page"**
The URL in `config.py` is wrong, or the site's HTML has changed.
Navigate manually to the page with the export accordion and copy that URL.

**Chrome opens but immediately closes**
Your saved session expired. Run with `--reset-login` to log in fresh.

**"playwright install chrome" fails**
Try: `python -m playwright install chrome`
