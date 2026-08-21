#!/usr/bin/env python3
"""
Collection CSV Exporter
-----------------------
Launches Chrome, logs you in (first run only), then downloads every
collection as a CSV to the folder you choose.

Usage:
    python export_collections.py                  # uses config.py settings
    python export_collections.py --out ~/Desktop  # override output folder
    python export_collections.py --reset-login    # clear saved session & re-login
"""

import argparse
import json
import sys
import time
from pathlib import Path

# ── Config (edit these or use config.py) ──────────────────────────────────────
PAGE_URL    = "https://www.libib.com/settings"   # URL of the settings/export page
# OUTPUT_DIR  = Path.home() / "Downloads" / "collections"
OUTPUT_DIR  = "/Users/aphilosopher30/Downloads/collections"
SESSION_FILE = Path(__file__).parent / ".session.json"
# ─────────────────────────────────────────────────────────────────────────────

try:
    import config as cfg
    PAGE_URL    = getattr(cfg, "PAGE_URL",    PAGE_URL)
    OUTPUT_DIR  = Path(getattr(cfg, "OUTPUT_DIR",  OUTPUT_DIR))
    SESSION_FILE = Path(getattr(cfg, "SESSION_FILE", SESSION_FILE))
except ImportError:
    pass  # config.py is optional


def parse_args():
    # print("parse_args")
    p = argparse.ArgumentParser(description="Export all collections as CSV files.")
    p.add_argument("--out", metavar="DIR", help="Output folder (overrides config)")
    p.add_argument("--url", metavar="URL", help="Settings page URL (overrides config)")
    p.add_argument("--reset-login", action="store_true",
                   help="Delete saved session and force a fresh login")
    return p.parse_args()


def load_session(context, session_file: Path):
    """Restore cookies + localStorage from a saved session file."""
    if not session_file.exists():
        return False
    try:
        state = json.loads(session_file.read_text())
        context.add_cookies(state.get("cookies", []))
        print(f"  ✔ Loaded saved session from {session_file}")
        return True
    except Exception as e:
        print(f"  ⚠ Could not load session: {e}")
        return False


def save_session(context, session_file: Path):

    """Persist cookies so the next run skips login."""
    try:
        cookies = context.cookies()
        session_file.write_text(json.dumps({"cookies": cookies}, indent=2))
        print(f"  ✔ Session saved to {session_file}")
    except Exception as e:
        print(f"  ⚠ Could not save session: {e}")


def wait_for_login(page, url: str):
    """
    Open the target page. If we land on a login/redirect page, pause and
    wait for the user to log in manually. Continues once the settings page loads.
    """
    print("\n  Opening page…")
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)

    # Check if we're on the right page already
    if page.query_selector("#settings-export-library-form"):
        print("  ✔ Already on the export page.")
        return

    print("\n" + "═" * 60)
    print("  ACTION REQUIRED")
    print("  Please log in to the site in the browser window.")
    print("  The script will continue automatically once you're")
    print(f"  on (or near) this page: {url}")
    print("═" * 60 + "\n")

    # Wait up to 5 minutes for the user to log in
    try:
        page.wait_for_selector("#settings-export-library-form", timeout=300_000)
        print("  ✔ Login detected, continuing…")
    except Exception:
        print("  ❌ Timed out waiting for login. Exiting.")
        sys.exit(1)


def scrape_collections(page) -> tuple[str, str, list[dict]]:
    """Return (form_action, maisc_token, list of {value, label})."""
    form = page.query_selector("#settings-export-library-form")
    if not form:
        raise RuntimeError("Export form not found on the page.")

    action = form.get_attribute("action") or ""
    # Make action absolute if it's a relative path
    if action.startswith("/"):
        origin = page.evaluate("window.location.origin")
        action = origin + action

    maisc = page.input_value("#export-library-maisc")
    options = page.query_selector_all("select[name='settings-library-export-id'] option")
    collections = [
        {"value": o.get_attribute("value"), "label": o.inner_text().strip()}
        for o in options
    ]
    return action, maisc, collections


def export_collection(page, action: str, collection_id: str, maisc: str,
                      label: str, output_dir: Path) -> Path:
    """POST the export form for one collection and save the response as CSV."""
    import urllib.request
    import urllib.parse
    import http.cookiejar

    # Grab current cookies from Playwright and build a cookiejar for urllib
    pw_cookies = page.context.cookies()
    cj = http.cookiejar.CookieJar()

    # Build the POST body
    body = urllib.parse.urlencode({
        "settings-library-export-id": collection_id,
        "maisc": maisc,
        "settings-export-library-submit": "Export",
    }).encode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": page.evaluate("navigator.userAgent"),
        "Cookie": "; ".join(f"{c['name']}={c['value']}" for c in pw_cookies),
        "Referer": page.url,
    }

    req = urllib.request.Request(action, data=body, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=60) as resp:
        # Try to get a filename from Content-Disposition
        # col["label"]

        cd = resp.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in cd:
            # print("AAA")
            filename =  label + "_" + cd.split("filename=")[-1].strip().strip('"').strip("'")

        if not filename:
            # print("BBB")

            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)
            filename = label + "_" + f"{safe}.csv"

        dest = output_dir / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.read())

    return dest


def main():
    args = parse_args()

    url        = args.url or PAGE_URL

    output_dir = Path(args.out) if args.out else OUTPUT_DIR

    if url == "https://www.example.com/settings":
        print("❌ Please set PAGE_URL in config.py (or pass --url) before running.")
        sys.exit(1)

    if args.reset_login and SESSION_FILE.exists():
        SESSION_FILE.unlink()
        print(f"  Session cleared ({SESSION_FILE})")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright is not installed. Run:  pip install playwright  then:  playwright install chrome")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📦 Collection CSV Exporter")
    print(f"   Page   : {url}")
    print(f"   Saving : {output_dir}\n")

    with sync_playwright() as pw:
        # Launch your real Chrome install (channel="chrome")
        if SESSION_FILE.exists():
            # is_headless = True
            #  Activate this if you have trouble loging in.
            is_headless = False
        else:
            is_headless = False

        browser = pw.chromium.launch(
            channel="chrome",
            headless=is_headless ,         # visible window — needed for manual login
        )
        context = browser.new_context()
        page = context.new_page()

        # ── Login ──────────────────────────────────────────────────────────────
        session_loaded = load_session(context, SESSION_FILE)
        wait_for_login(page, url)
        save_session(context, SESSION_FILE)   # refresh/persist after load

        # ── Scrape collections ─────────────────────────────────────────────────
        print("\n  Scanning for collections…")
        action, maisc, collections = scrape_collections(page)

        if not collections:
            print("  ❌ No collections found in the dropdown.")
            browser.close()
            sys.exit(1)

        print(f"  ✔ Found {len(collections)} collection(s):\n")
        for c in collections:
            print(f"     • {c['label']}  (id={c['value']})")

        # ── Export each collection ─────────────────────────────────────────────
        print(f"\n  Exporting to: {output_dir}\n")
        success, failed = [], []

        for i, col in enumerate(collections, 1):
            label = col["label"]
            print(f"  [{i}/{len(collections)}] {label}… ", end="", flush=True)
            try:
                dest = export_collection(page, action, col["value"], maisc,
                                         label, output_dir)
                print(f"✔  →  {dest.name}")
                success.append(dest)
            except Exception as e:
                print(f"✘  {e}")
                failed.append((label, str(e)))

        browser.close()

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print(f"  Done.  {len(success)} saved,  {len(failed)} failed.")
    if success:
        print(f"  Folder: {output_dir}")
    if failed:
        print("\n  Failed:")
        for label, err in failed:
            print(f"    ✘ {label}: {err}")
    print()


if __name__ == "__main__":
    main()
