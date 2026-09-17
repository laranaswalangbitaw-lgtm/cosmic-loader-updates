#!/usr/bin/env python3
"""
COSMIC AUTO-UPDATER — Fetches updates/announcements from GitHub.
"""
import os
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
#  CONFIG — Change mo 'to sa GitHub repo mo
# ═══════════════════════════════════════════════════════════
UPDATE_URL = "https://raw.githubusercontent.com/laranaswalangbitaw-lgtm/cosmic-loader-updates/main/version.json"
ANNOUNCE_URL = "https://raw.githubusercontent.com/laranaswalangbitaw-lgtm/cosmic-loader-updates/main/announcement.txt"

# Local version file
VERSION_FILE = Path(__file__).parent / "version.json"
UPDATE_CACHE = Path(__file__).parent / ".update_cache"

# Current version — update mo 'to every release
CURRENT_VERSION = "4.3.0"

# Cache TTL (seconds) — huwag mag-check every run (para mabilis)
CACHE_TTL = 3600  # 1 hour


# ═══════════════════════════════════════════════════════════
#  Colors
# ═══════════════════════════════════════════════════════════
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[38;2;0;229;255m"
GREEN = "\033[38;2;100;255;180m"
YELLOW = "\033[38;2;255;200;100m"
RED = "\033[38;2;255;100;120m"
WHITE = "\033[38;2;230;240;255m"


def _is_newer(remote, local):
    """Compare semver strings."""
    try:
        r = tuple(int(x) for x in remote.split("."))
        l = tuple(int(x) for x in local.split("."))
        return r > l
    except Exception:
        return remote != local


def _should_check():
    """Rate-limit the update check."""
    if not UPDATE_CACHE.exists():
        return True
    try:
        age = time.time() - UPDATE_CACHE.stat().st_mtime
        return age > CACHE_TTL
    except Exception:
        return True


def _mark_checked():
    try:
        UPDATE_CACHE.write_text(str(time.time()))
    except Exception:
        pass


def check_updates(force=False):
    """
    Check for updates + announcements.
    Returns dict: {update_available, latest_version, changelog, announcement}
    """
    result = {
        "update_available": False,
        "latest_version": CURRENT_VERSION,
        "changelog": [],
        "announcement": "",
    }

    # Always check announcement (no rate limit)
    # Rate-limit only version check
    pass

    # ── Check version ─────────────────────────────────────
    try:
        r = requests.get(UPDATE_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            latest = data.get("version", CURRENT_VERSION)
            result["latest_version"] = latest
            result["changelog"] = data.get("changelog", [])
            if _is_newer(latest, CURRENT_VERSION):
                result["update_available"] = True
    except Exception:
        pass

    # ── Check announcement ────────────────────────────────
    try:
        r = requests.get(ANNOUNCE_URL, timeout=10)
        if r.status_code == 200:
            ann = r.text.strip()
            if ann:
                result["announcement"] = ann
    except Exception:
        pass

    return result


def show_update_banner(info):
    """Display update/announcement banner."""
    if not info.get("update_available") and not info.get("announcement"):
        return

    w = 66

    if info.get("update_available"):
        print()
        print(f"  {YELLOW}┏{'━' * w}┓{RESET}")
        print(f"  {YELLOW}┃{RESET}{BOLD}{WHITE}{'🚀 UPDATE AVAILABLE'.center(w)}{RESET}{YELLOW}┃{RESET}")
        print(f"  {YELLOW}┣{'━' * w}┫{RESET}")
        print(f"  {YELLOW}┃{RESET}  {DIM}Current :{RESET} {RED}{CURRENT_VERSION}{RESET}")
        print(f"  {YELLOW}┃{RESET}  {DIM}Latest  :{RESET} {GREEN}{info['latest_version']}{RESET}")
        print(f"  {YELLOW}┃{RESET}")
        if info.get("changelog"):
            print(f"  {YELLOW}┃{RESET}  {BOLD}{CYAN}What's new:{RESET}")
            for line in info["changelog"][:6]:
                print(f"  {YELLOW}┃{RESET}    {DIM}•{RESET} {WHITE}{line}{RESET}")
        print(f"  {YELLOW}┃{RESET}")
        print(f"  {YELLOW}┃{RESET}  {DIM}Contact @LEGITCosmicDev2nd for update.{RESET}")
        print(f"  {YELLOW}┗{'━' * w}┛{RESET}")

    if info.get("announcement"):
        print()
        print(f"  {CYAN}┏{'━' * w}┓{RESET}")
        print(f"  {CYAN}┃{RESET}{BOLD}{WHITE}{'📢 ANNOUNCEMENT'.center(w)}{RESET}{CYAN}┃{RESET}")
        print(f"  {CYAN}┣{'━' * w}┫{RESET}")
        for line in info["announcement"].split("\n"):
            line = line.strip()
            if line:
                print(f"  {CYAN}┃{RESET}  {WHITE}{line[:w-4]}{RESET}")
        print(f"  {CYAN}┗{'━' * w}┛{RESET}")

    print()


if __name__ == "__main__":
    info = check_updates(force=True)
    print(json.dumps(info, indent=2))
