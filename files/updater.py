#!/usr/bin/env python3
"""COSMIC AUTO-UPDATER v2.0 — Real code updates from GitHub."""
import os
import sys
import json
import time
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
import requests

GITHUB_USER = "laranaswalangbitaw-lgtm"
GITHUB_REPO = "cosmic-loader-updates"
GITHUB_BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
UPDATE_URL = f"{BASE_URL}/version.json"
ANNOUNCE_URL = f"{BASE_URL}/announcement.txt"
FILES_BASE = f"{BASE_URL}/files"

BASE_DIR = Path(__file__).parent.resolve()
BACKUP_DIR = BASE_DIR / ".backup"
CURRENT_VERSION = "4.0.0"

UPDATABLE_FILES = [
    "cosmicloaderFORSALE.py",
    "security.py",
    "updater.py",
    "tracking.py",
    "dns_fix.py",
    "decoder_encoder.py",
    "url_remover.py",
    "proxy_scraper.py",
    "sms_bomber.py",
    "separator.py",
    "Dev_Id_checker.py",
]


def _is_newer(remote, local):
    try:
        r = tuple(int(x) for x in remote.split("."))
        l = tuple(int(x) for x in local.split("."))
        return r > l
    except Exception:
        return False


def check_updates(force=False):
    result = {
        "update_available": False,
        "latest_version": CURRENT_VERSION,
        "changelog": [],
        "announcement": "",
        "files_to_update": [],
    }
    try:
        r = requests.get(UPDATE_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            latest = data.get("version", CURRENT_VERSION)
            result["latest_version"] = latest
            result["changelog"] = data.get("changelog", [])
            result["files_to_update"] = data.get("files", UPDATABLE_FILES)
            if _is_newer(latest, CURRENT_VERSION):
                result["update_available"] = True
    except Exception:
        pass
    try:
        r = requests.get(ANNOUNCE_URL, timeout=10)
        if r.status_code == 200:
            result["announcement"] = r.text.strip()
    except Exception:
        pass
    return result


def _download_file(fname):
    try:
        url = f"{FILES_BASE}/{fname}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


def apply_update(files_to_update=None):
    if files_to_update is None:
        files_to_update = UPDATABLE_FILES
    updated = []
    failed = []
    BACKUP_DIR.mkdir(exist_ok=True)
    for fname in files_to_update:
        content = _download_file(fname)
        if content is None:
            failed.append(fname)
            continue
        src = BASE_DIR / fname
        if src.exists():
            try:
                shutil.copy2(src, BACKUP_DIR / f"{fname}.bak")
            except Exception:
                pass
        try:
            with open(src, "w", encoding="utf-8") as f:
                f.write(content)
            updated.append(fname)
        except Exception:
            failed.append(fname)
    return (len(updated) > 0), updated, failed


def show_update_banner(info):
    w = 60
    RESET = "\033[0m"
    BOLD = "\033[1m"
    YELLOW = "\033[38;2;255;200;100m"
    CYAN = "\033[38;2;0;229;255m"
    WHITE = "\033[38;2;230;240;255m"
    DIM = "\033[2m"
    if info.get("update_available"):
        print()
        print(f"  {YELLOW}┏{'━' * w}┓{RESET}")
        print(f"  {YELLOW}┃{RESET}{BOLD}{WHITE}{'UPDATE AVAILABLE'.center(w)}{RESET}{YELLOW}┃{RESET}")
        print(f"  {YELLOW}┣{'━' * w}┫{RESET}")
        print(f"  {YELLOW}┃{RESET}  {DIM}Current :{RESET} {CURRENT_VERSION}")
        print(f"  {YELLOW}┃{RESET}  {DIM}Latest  :{RESET} {info['latest_version']}")
        for line in info.get("changelog", [])[:5]:
            print(f"  {YELLOW}┃{RESET}    • {WHITE}{line}{RESET}")
        print(f"  {YELLOW}┗{'━' * w}┛{RESET}")
    if info.get("announcement"):
        print()
        print(f"  {CYAN}┏{'━' * w}┓{RESET}")
        print(f"  {CYAN}┃{RESET}{BOLD}{WHITE}{'ANNOUNCEMENT'.center(w)}{RESET}{CYAN}┃{RESET}")
        print(f"  {CYAN}┣{'━' * w}┫{RESET}")
        for line in info["announcement"].split("\n"):
            if line.strip():
                print(f"  {CYAN}┃{RESET}  {WHITE}{line.strip()[:w-4]}{RESET}")
        print(f"  {CYAN}┗{'━' * w}┛{RESET}")
    print()


if __name__ == "__main__":
    info = check_updates(force=True)
    print(json.dumps(info, indent=2))
