# config.py — edit this file before running export_collections.py
# ─────────────────────────────────────────────────────────────────

# URL of the page that contains the export accordion/form.
# Example: "https://www.myanimelist.net/settings"
PAGE_URL = "https://www.libib.com/settings"

# Where to save the downloaded CSV files.
# Use a raw string (r"...") on Windows to avoid backslash issues.
# Examples:
#   "/Users/yourname/Documents/collections"      (Mac/Linux)
#   r"C:\Users\yourname\Documents\collections"   (Windows)
OUTPUT_DIR = "Tables/Raw_Downloads"
# OUTPUT_DIR = "/Users/aphilosopher30/Downloads/collections"

# Where to store the saved login session (so you only log in once).
# Default is a hidden file next to this script — you rarely need to change this.
# SESSION_FILE = ".session.json"
