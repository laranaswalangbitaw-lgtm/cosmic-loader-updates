#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║  COSMIC ADMIN BOT — Pre-Gen Input Flow                              ║
║  Powered by @LEGITCosmicDev2nd x @LEGITCosmicDev                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
# ══════════════════════════════════════════════════════════════════════
#  FORCE DNS FIX — before any network imports
# ══════════════════════════════════════════════════════════════════════
try:
    from dns_fix import fix_dns as _fix_dns
    _fix_dns()
except Exception as _e:
    print(f"⚠️  DNS fix failed: {_e}")


import asyncio
import json
import logging
import os
import secrets
import shutil
import string
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock

# ── Tracking import ──
try:
    import tracking as _tracking
    _TRACKING_AVAILABLE = True
except Exception:
    _TRACKING_AVAILABLE = False

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ══════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════
# ── Config from .env ──
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  pip install python-dotenv")
    import sys; sys.exit(1)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID  = int(os.getenv("ADMIN_ID", "0"))
SHOP_NAME   = os.getenv("SHOP_NAME", "COSMIC ADMIN")
CREDIT_LINE = os.getenv("CREDIT_LINE", "@LEGITCosmicDev2nd x @LEGITCosmicDev")

if not BOT_TOKEN or not ADMIN_ID:
    raise RuntimeError("❌ BOT_TOKEN and ADMIN_ID must be set in .env")

# ══════════════════════════════════════════════════════════════════════════
#  SETUP
# ══════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

BASE_DIR     = Path(__file__).resolve().parent

# ══════════════════════════════════════════════════════════════════════════
#  BOT OWNER LOCK — Only runs on owner's machine
# ══════════════════════════════════════════════════════════════════════════
import hashlib
import socket
import platform


def _get_bot_hwid():
    """Get stable HWID."""
    try:
        import uuid
        parts = [
            f"{uuid.getnode():012x}",
            socket.gethostname(),
            platform.machine(),
        ]
        combined = "|".join(p for p in parts if p)
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
    except Exception:
        return "unknown"


# Owner HWIDs (naka-lock sa device mo)
_BOT_OWNER_HWIDS = [
    "0c722d25b248",  # Stable HWID
    "a3607276ce52",  # MAC HWID
    "b9ec16770b92",  # Current HWID (from screenshot)
]

# Owner bypass file
_BOT_OWNER_FILE = BASE_DIR / ".bot_owner"


def _is_bot_owner():
    """Check kung owner machine."""
    # Bypass file
    if _BOT_OWNER_FILE.exists():
        try:
            if _BOT_OWNER_FILE.read_text().strip() == BOT_TOKEN[:20]:
                return True
        except Exception:
            pass
    
    # HWID match
    hwid = _get_bot_hwid()
    return hwid in _BOT_OWNER_HWIDS


# Enforce ownership before bot starts
def _enforce_bot_owner():
    """Exit if not owner."""
    if not _is_bot_owner():
        print()
        print("  ╔══════════════════════════════════════════════════════╗")
        print("  ║       ⚠  ADMIN BOT — DEVICE NOT AUTHORIZED          ║")
        print("  ╠══════════════════════════════════════════════════════╣")
        print("  ║  This bot only runs on the owner's device.          ║")
        print("  ║  Contact @LEGITCosmicDev2nd if you need help.       ║")
        print("  ╚══════════════════════════════════════════════════════╝")
        print()
        print(f"  Your HWID: {_get_bot_hwid()}")
        print()
        raise SystemExit(1)


KEYS_FILE    = Path("/storage/emulated/0/test_Tools2/keys.json")
USERS_FILE   = BASE_DIR / "users.json"
ADMINS_FILE  = BASE_DIR / "admins.json"
LOG_FILE     = BASE_DIR / "audit.log"
CONFIG_FILE  = BASE_DIR / "bot_config.json"
BACKUP_DIR   = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

KEYS_LOCK  = Lock()
USERS_LOCK = Lock()

DEFAULT_CONFIG = {
    "key_prefix": "COSMIC",
    "key_segments": 4,
    "key_segment_len": 4,
    "auto_cleanup_hours": 24,
    "notify_on_revoke": True,
}

KEY_DURATIONS = {
    "trial":     ("1 Hour Trial",  "hours", 1),
    "1h":        ("1 Hour",        "hours", 1),
    "6h":        ("6 Hours",       "hours", 6),
    "12h":       ("12 Hours",      "hours", 12),
    "1d":        ("1 Day",         "days",  1),
    "3d":        ("3 Days",        "days",  3),
    "7d":        ("7 Days",        "days",  7),
    "14d":       ("14 Days",       "days",  14),
    "30d":       ("30 Days",       "days",  30),
    "60d":       ("60 Days",       "days",  60),
    "90d":       ("90 Days",       "days",  90),
    "180d":      ("180 Days",      "days",  180),
    "365d":      ("365 Days",      "days",  365),
    "permanent": ("Permanent",     "never", 0),
}

USER_STATE = {}

# ── Rate limiting ──
_RATE_LIMIT = {}
_RATE_LOCK = Lock()
RATE_WINDOW = 60
RATE_MAX = 30


def _check_rate_limit(uid: int) -> bool:
    now = time.time()
    with _RATE_LOCK:
        times = _RATE_LIMIT.get(uid, [])
        times = [t for t in times if now - t < RATE_WINDOW]
        if len(times) >= RATE_MAX:
            return False
        times.append(now)
        _RATE_LIMIT[uid] = times
    return True




# ══════════════════════════════════════════════════════════════════════════
#  SAFE PARSER
# ══════════════════════════════════════════════════════════════════════════
def safe_split_payload(value: str, expected_parts: int = 3) -> tuple:
    if not value or not isinstance(value, str):
        return False, ""
    parts = value.split(":", expected_parts - 1)
    if len(parts) < expected_parts:
        return False, ""
    payload = parts[-1].strip()
    if not payload:
        return False, ""
    return True, payload


# ══════════════════════════════════════════════════════════════════════════
#  CONFIG MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════
def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> bool:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception as e:
        log.error(f"save_config: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════
#  ADMIN MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════
def load_admins() -> dict:
    if not ADMINS_FILE.exists():
        return {"admins": [str(ADMIN_ID)], "primary": str(ADMIN_ID)}
    try:
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        if "admins" not in d:
            d["admins"] = [str(ADMIN_ID)]
        if "primary" not in d:
            d["primary"] = str(ADMIN_ID)
        return d
    except Exception:
        return {"admins": [str(ADMIN_ID)], "primary": str(ADMIN_ID)}


def save_admins(d: dict) -> bool:
    try:
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
        return True
    except Exception:
        return False


def is_admin(uid: int) -> bool:
    return str(uid) in load_admins().get("admins", [])


def add_admin(uid: int) -> bool:
    d = load_admins()
    if str(uid) in d["admins"]:
        return False
    d["admins"].append(str(uid))
    return save_admins(d)


def remove_admin(uid: int) -> bool:
    d = load_admins()
    primary = d.get("primary", str(ADMIN_ID))
    if str(uid) == primary:
        return False
    if str(uid) not in d["admins"]:
        return False
    d["admins"].remove(str(uid))
    return save_admins(d)


# ══════════════════════════════════════════════════════════════════════════
#  AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════
def audit(uid: int, action: str, detail: str = ""):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {uid} | {action} | {detail}\n")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════
#  KEY STORAGE
# ══════════════════════════════════════════════════════════════════════════
def load_keys() -> dict:
    if not KEYS_FILE.exists():
        return {"keys": {}}
    try:
        with KEYS_LOCK:
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
        if "keys" not in d:
            d["keys"] = {}
        return d
    except Exception:
        return {"keys": {}}


def save_keys(d: dict) -> bool:
    try:
        with KEYS_LOCK:
            with open(KEYS_FILE, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
        try:
            os.chmod(KEYS_FILE, 0o600)
        except Exception:
            pass
        return True
    except Exception as e:
        log.error(f"save_keys: {e}")
        return False


def gen_key_str() -> str:
    cfg = load_config()
    prefix = cfg.get("key_prefix", "COSMIC")
    segs = cfg.get("key_segments", 4)
    length = cfg.get("key_segment_len", 4)
    parts = ["".join(secrets.choice(string.ascii_uppercase + string.digits)
                     for _ in range(length))
             for _ in range(segs)]
    return f"{prefix}-" + "-".join(parts)


def create_key(dc: str, note: str = "", price: str = None,
               created_by: int = None) -> dict:
    if dc not in KEY_DURATIONS:
        raise ValueError(f"bad duration: {dc}")
    label, unit, amount = KEY_DURATIONS[dc]
    data = load_keys()
    for _ in range(100):
        k = gen_key_str()
        if k not in data["keys"]:
            break
    else:
        raise RuntimeError("collision")

    now = datetime.now()
    if unit == "never":
        exp = None
    elif unit == "hours":
        exp = (now + timedelta(hours=amount)).isoformat()
    else:
        exp = (now + timedelta(days=amount)).isoformat()

    rec = {
        "key": k,
        "duration_code": dc,
        "duration_label": label,
        "created_at": now.isoformat(),
        "expires_at": exp,
        "uses": 0,
        "bound_to": None,
        "bound_at": None,
        "revoked": False,
        "note": note or "",
        "price": price or "",
        "created_by": created_by,
        "order_id": f"ORD-{now.strftime('%y%m%d')}-{k[-4:]}",
    }
    data["keys"][k] = rec
    save_keys(data)
    return rec


def revoke_key(k: str) -> bool:
    data = load_keys()
    k = k.strip().upper()
    if k not in data["keys"]:
        return False
    data["keys"][k]["revoked"] = True
    data["keys"][k]["revoked_at"] = datetime.now().isoformat()
    return save_keys(data)


def delete_key(k: str) -> bool:
    data = load_keys()
    k = k.strip().upper()
    if k not in data["keys"]:
        return False
    del data["keys"][k]
    return save_keys(data)


def unbind_key(k: str) -> bool:
    data = load_keys()
    k = k.strip().upper()
    if k not in data["keys"]:
        return False
    data["keys"][k]["bound_to"] = None
    data["keys"][k]["bound_at"] = None
    return save_keys(data)


def extend_key(k: str, dc: str) -> tuple:
    if dc not in KEY_DURATIONS:
        return False, "bad duration"
    label, unit, amount = KEY_DURATIONS[dc]
    data = load_keys()
    k = k.strip().upper()
    if k not in data["keys"]:
        return False, "not found"
    rec = data["keys"][k]
    if unit == "never":
        rec["expires_at"] = None
        rec["duration_label"] = "Permanent"
    else:
        base = datetime.now()
        if rec.get("expires_at"):
            try:
                cur = datetime.fromisoformat(rec["expires_at"])
                if cur > base:
                    base = cur
            except Exception:
                pass
        if unit == "hours":
            rec["expires_at"] = (base + timedelta(hours=amount)).isoformat()
        else:
            rec["expires_at"] = (base + timedelta(days=amount)).isoformat()
        rec["duration_label"] = label
    data["keys"][k] = rec
    save_keys(data)
    return True, "OK"


def cleanup_expired() -> int:
    data = load_keys()
    now = datetime.now()
    to_delete = []
    for k, r in data["keys"].items():
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
        save_keys(data)
    return len(to_delete)


def get_active_key_count() -> int:
    keys = load_keys()["keys"]
    now = datetime.now()
    count = 0
    for r in keys.values():
        if r.get("revoked"):
            continue
        if r.get("expires_at"):
            try:
                if datetime.fromisoformat(r["expires_at"]) < now:
                    continue
            except Exception:
                pass
        count += 1
    return count


def fmt_remaining(ea) -> str:
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


# ══════════════════════════════════════════════════════════════════════════
#  RECEIPT-STYLE FORMATTERS (NO BUYER NAME)
# ══════════════════════════════════════════════════════════════════════════
_ACCESS_MAP = {
    "trial": "Trial Access",
    "1h": "Hourly Access",
    "6h": "Half-Day Access",
    "12h": "Half-Day Access",
    "1d": "Daily Access",
    "3d": "3-Day Access",
    "7d": "Weekly Access",
    "14d": "2-Week Access",
    "30d": "Monthly Access",
    "60d": "2-Month Access",
    "90d": "3-Month Access",
    "180d": "6-Month Access",
    "365d": "Annual Access",
    "permanent": "Lifetime Access",
}


def format_key_receipt(rec: dict) -> str:
    """HTML receipt (no buyer name)."""
    key = rec.get("key", "—")
    dur_label = rec.get("duration_label", "—")
    dc = rec.get("duration_code", "")
    access_type = _ACCESS_MAP.get(dc, f"{dur_label} Access")

    now = datetime.now()
    created = rec.get("created_at", now.isoformat())
    try:
        dt_created = datetime.fromisoformat(created)
    except Exception:
        dt_created = now

    order_date = dt_created.strftime("%B %d, %Y | %I:%M %p")
    order_id = rec.get("order_id") or f"ORD-{dt_created.strftime('%y%m%d')}-{key[-4:]}"

    expiry = "Never (Permanent)" if rec.get("expires_at") is None else \
             fmt_remaining(rec.get("expires_at"))

    price_display = rec.get("price") or "—"
    note = rec.get("note") or ""
    note_line = f"📝 <b>Note</b> : {note}\n" if note else ""

    return (
        f"✅ <b>ORDER SUCCESSFUL</b>\n"
        f"\n"
        f"🔑 <b>Member Key</b> : <code>{key}</code>\n"
        f"🎮 <b>Access Type</b> : {access_type}\n"
        f"⏳ <b>Duration</b> : {dur_label}\n"
        f"💸 <b>Price</b> : ₱ {price_display}\n"
        f"📅 <b>Order Date</b> : {order_date}\n"
        f"🆔 <b>Order ID</b> : <code>{order_id}</code>\n"
        f"🔚 <b>Expiry</b> : {expiry}\n"
        f"{note_line}"
        f"🛍️ <b>Seller</b> : {CREDIT_LINE}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🙏 <b>THANK YOU FOR BUYING</b> ✅\n"
        f"🤝 <b>DONE DEAL</b> 🤝\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )


def format_key_receipt_plain(rec: dict) -> str:
    """Plain-text receipt (no buyer name)."""
    key = rec.get("key", "—")
    dur_label = rec.get("duration_label", "—")
    dc = rec.get("duration_code", "")
    access_type = _ACCESS_MAP.get(dc, f"{dur_label} Access")

    now = datetime.now()
    created = rec.get("created_at", now.isoformat())
    try:
        dt_created = datetime.fromisoformat(created)
    except Exception:
        dt_created = now

    order_date = dt_created.strftime("%B %d, %Y | %I:%M %p")
    order_id = rec.get("order_id") or f"ORD-{dt_created.strftime('%y%m%d')}-{key[-4:]}"

    expiry = "Never (Permanent)" if rec.get("expires_at") is None else \
             fmt_remaining(rec.get("expires_at"))

    price_display = rec.get("price") or "—"
    note = rec.get("note") or ""
    note_line = f"📝 Note : {note}\n" if note else ""

    return (
        f"✅ ORDER SUCCESSFUL\n"
        f"\n"
        f"🔑 Member Key : {key}\n"
        f"🎮 Access Type : {access_type}\n"
        f"⏳ Duration : {dur_label}\n"
        f"💸 Price : ₱ {price_display}\n"
        f"📅 Order Date : {order_date}\n"
        f"🆔 Order ID : {order_id}\n"
        f"🔚 Expiry : {expiry}\n"
        f"{note_line}"
        f"🛍️ Seller : {CREDIT_LINE}\n"
        f"\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🙏 THANK YOU FOR BUYING ✅\n"
        f"🤝 DONE DEAL 🤝\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )


# ══════════════════════════════════════════════════════════════════════════
#  USER TRACKING
# ══════════════════════════════════════════════════════════════════════════
def load_users() -> dict:
    if not USERS_FILE.exists():
        return {"users": {}}
    try:
        with USERS_LOCK:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
        if "users" not in d:
            d["users"] = {}
        return d
    except Exception:
        return {"users": {}}


def save_users(d: dict) -> bool:
    try:
        with USERS_LOCK:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
        return True
    except Exception:
        return False


def track_user(uid: int, username: str = None):
    d = load_users()
    u = d["users"].get(str(uid), {})
    u["uid"] = uid
    u["username"] = username or u.get("username", "—")
    u["last_seen"] = datetime.now().isoformat()
    if "joined" not in u:
        u["joined"] = datetime.now().isoformat()
    d["users"][str(uid)] = u
    save_users(d)


# ══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════
async def send(update: Update, text: str, **kw):
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                text, parse_mode=ParseMode.HTML, **kw)
        else:
            await update.effective_message.reply_text(
                text, parse_mode=ParseMode.HTML, **kw)
    except Exception:
        if update.callback_query:
            await update.callback_query.message.reply_text(text, **kw)
        else:
            await update.effective_message.reply_text(text, **kw)


async def edit(query, text: str, kb=None):
    try:
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    except Exception:
        try:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
        except Exception:
            pass


def main_menu(uid: int) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton("👑 Admin Panel")]]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def duration_kb(prefix: str, cols: int = 3) -> InlineKeyboardMarkup:
    rows = []
    items = list(KEY_DURATIONS.items())
    for i in range(0, len(items), cols):
        row = []
        for code, (label, _, _) in items[i:i + cols]:
            row.append(InlineKeyboardButton(label, callback_data=f"{prefix}:{code}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Cancel", callback_data="adm:panel")])
    return InlineKeyboardMarkup(rows)


def status_emoji(r: dict) -> str:
    if r.get("revoked"):
        return "🚫"
    if r.get("expires_at"):
        try:
            if datetime.fromisoformat(r["expires_at"]) < datetime.now():
                return "⏰"
        except Exception:
            pass
    return "✅"


# ══════════════════════════════════════════════════════════════════════════
#  COMMANDS
# ══════════════════════════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    track_user(u.id, u.username or u.first_name)

    if not is_admin(u.id):
        await send(update,
            f"❌ <b>Admin only.</b>\n\n"
            f"This bot generates keys for the CODM Checker.\n"
            f"Powered by <b>{CREDIT_LINE}</b>"
        )
        return

    cfg = load_config()
    keys = load_keys()["keys"]
    active = get_active_key_count()
    total = len(keys)
    users_count = len(load_users()["users"])

    await update.message.reply_text(
        f"👋 <b>Welcome, Admin!</b>\n\n"
        f"🆔 <code>{u.id}</code> ✅\n\n"
        f"📊 <b>Dashboard</b>\n"
        f"   🔑 Total Keys: <b>{total}</b>\n"
        f"   ✅ Active Keys: <b>{active}</b>\n"
        f"   👥 Tracked Users: <b>{users_count}</b>\n"
        f"   🎯 Prefix: <code>{cfg.get('key_prefix', 'COSMIC')}</code>\n\n"
        f"<i>{CREDIT_LINE}</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(u.id)
    )


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only.")
        return
    await show_panel(update, context)


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_STATE.pop(update.effective_user.id, None)
    await update.message.reply_text("✅ Cancelled.")


async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keys = load_keys()["keys"]
    total = len(keys)
    active = get_active_key_count()
    text = (
        f"👑 <b>COSMIC ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Total: <b>{total}</b>  ·  ✅ Active: <b>{active}</b>\n\n"
        f"<b>Choose action:</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Generate Key", callback_data="adm:genkey"),
         InlineKeyboardButton("⚡ Quick Keys", callback_data="adm:quickkeys")],
        [InlineKeyboardButton("📋 List Keys", callback_data="adm:listkeys"),
         InlineKeyboardButton("🎯 Filter", callback_data="adm:filter")],
        [InlineKeyboardButton("🔍 Search", callback_data="adm:search"),
         InlineKeyboardButton("🚫 Revoke", callback_data="adm:revoke")],
        [InlineKeyboardButton("🗑️ Delete", callback_data="adm:delete"),
         InlineKeyboardButton("🔓 Unbind", callback_data="adm:unbind")],
        [InlineKeyboardButton("⏰ Extend", callback_data="adm:extend"),
         InlineKeyboardButton("📤 Export", callback_data="adm:export")],
        [InlineKeyboardButton("💾 Backup", callback_data="adm:backup"),
         InlineKeyboardButton("📢 Broadcast", callback_data="adm:broadcast")],
        [InlineKeyboardButton("👥 Users", callback_data="adm:users"),
         InlineKeyboardButton("🚫 Suspended", callback_data="adm:suspended")],
        [InlineKeyboardButton("🧹 Cleanup", callback_data="adm:cleanup"),
         InlineKeyboardButton("📊 Tracking", callback_data="adm:tracking")],
        [InlineKeyboardButton("📈 Analytics", callback_data="adm:analytics"),
         InlineKeyboardButton("👤 Admins", callback_data="adm:admins")],
        [InlineKeyboardButton("⚙️ Config", callback_data="adm:config"),
         InlineKeyboardButton("📊 Stats", callback_data="adm:stats")],
        [InlineKeyboardButton("📜 Audit Log", callback_data="adm:audit")],
    ])
    if update.callback_query:
        await edit(update.callback_query, text, kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# ══════════════════════════════════════════════════════════════════════════
#  ADMIN CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════════════
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    if not is_admin(uid):
        await q.answer("❌ Admin only", show_alert=True)
        return
    await q.answer()
    data = q.data or ""
    cfg = load_config()

    # ── Panel ──
    if data == "adm:panel":
        await show_panel(update, context)
        return

    # ── Generate Key (STEP 1: choose duration) ──
    if data == "adm:genkey":
        await edit(q, "🔑 <b>Generate Key — Step 1/3</b>\n\n"
                      "Pick a duration:",
                   duration_kb("adm:gendur"))
        return

    # ── STEP 2: After picking duration, ASK FOR PRICE FIRST ──
    if data.startswith("adm:gendur:"):
        ok, code = safe_split_payload(data, 3)
        if not ok or code not in KEY_DURATIONS:
            await q.answer("❌ Invalid duration", show_alert=True)
            return
        # Save duration to user_data temporarily
        context.user_data["pending_duration"] = code
        USER_STATE[uid] = "adm_keygen_price"
        label, _, _ = KEY_DURATIONS[code]
        await edit(
            q,
            f"🔑 <b>Generate Key — Step 2/3</b>\n\n"
            f"📅 Duration: <b>{label}</b>\n\n"
            f"💰 Send the <b>Price</b> (e.g. <code>50</code>):\n"
            f"<i>Just the number — ₱ symbol auto-added.</i>"
        )
        return

    # ── Quick Keys ──
    if data == "adm:quickkeys":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ 1h Trial", callback_data="adm:qk:trial"),
             InlineKeyboardButton("⚡ 1 Day", callback_data="adm:qk:1d")],
            [InlineKeyboardButton("⚡ 1 Week", callback_data="adm:qk:7d"),
             InlineKeyboardButton("⚡ 1 Month", callback_data="adm:qk:30d")],
            [InlineKeyboardButton("⚡ 3 Months", callback_data="adm:qk:90d"),
             InlineKeyboardButton("⚡ Permanent", callback_data="adm:qk:permanent")],
            [InlineKeyboardButton("◀ Panel", callback_data="adm:panel")],
        ])
        await edit(q, "⚡ <b>Quick Keys</b>\n\n"
                      "Same 3-step flow as normal generate.\n\n"
                      "Pick a duration:", kb)
        return

    # ── Quick Keys: use same flow (duration → price → note → generate) ──
    if data.startswith("adm:qk:"):
        ok, code = safe_split_payload(data, 3)
        if not ok or code not in KEY_DURATIONS:
            await q.answer("❌ Invalid", show_alert=True)
            return
        context.user_data["pending_duration"] = code
        USER_STATE[uid] = "adm_keygen_price"
        label, _, _ = KEY_DURATIONS[code]
        await edit(
            q,
            f"⚡ <b>Quick Key — Step 2/3</b>\n\n"
            f"📅 Duration: <b>{label}</b>\n\n"
            f"💰 Send the <b>Price</b> (e.g. <code>50</code>):\n"
            f"<i>Just the number — ₱ symbol auto-added.</i>"
        )
        return

    # ── Add Note (separate flow for existing keys) ──
    if data.startswith("adm:note:"):
        ok, key = safe_split_payload(data, 3)
        if not ok:
            await q.answer("❌ Invalid", show_alert=True)
            return
        USER_STATE[uid] = f"adm_note:{key}"
        await edit(q, f"📝 <b>Add Note</b>\n\nSend a note for key:\n<code>{key}</code>")
        return

    # ── Copy Plain Text ──
    if data.startswith("adm:copy:"):
        ok, key = safe_split_payload(data, 3)
        if not ok:
            await q.answer("❌ Invalid", show_alert=True)
            return
        rec = load_keys()["keys"].get(key.upper())
        if not rec:
            await q.answer("Key not found", show_alert=True)
            return
        plain = format_key_receipt_plain(rec)
        await q.message.reply_text(f"<pre>{plain}</pre>", parse_mode=ParseMode.HTML)
        return

    # ── List Keys ──
    if data == "adm:listkeys":
        keys = load_keys()["keys"]
        if not keys:
            await edit(q, "📋 <b>No keys yet.</b>",
                       InlineKeyboardMarkup([
                           [InlineKeyboardButton("🔑 Generate", callback_data="adm:genkey")],
                           [InlineKeyboardButton("◀ Panel", callback_data="adm:panel")]
                       ]))
            return
        items = sorted(keys.values(), key=lambda r: r.get("created_at", ""), reverse=True)[:20]
        lines = [f"📋 <b>Latest Keys</b> ({len(keys)} total)\n"]
        for r in items:
            icon = status_emoji(r)
            exp = fmt_remaining(r.get("expires_at"))
            bound = r.get("bound_to") or "—"
            price = f"  💸 ₱{r.get('price')}" if r.get("price") else ""
            note = f"  📝 <i>{r.get('note')}</i>" if r.get("note") else ""
            lines.append(
                f"{icon} <code>{r['key']}</code>\n"
                f"   ⏰ {exp} · uses: {r.get('uses', 0)} · bound: {bound}{price}{note}"
            )
        await edit(q, "\n".join(lines)[:3900],
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Filter ──
    if data == "adm:filter":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Active only", callback_data="adm:flt:active")],
            [InlineKeyboardButton("⏰ Expired only", callback_data="adm:flt:expired")],
            [InlineKeyboardButton("🚫 Revoked only", callback_data="adm:flt:revoked")],
            [InlineKeyboardButton("🔒 Bound only", callback_data="adm:flt:bound")],
            [InlineKeyboardButton("🔓 Unbound only", callback_data="adm:flt:unbound")],
            [InlineKeyboardButton("◀ Panel", callback_data="adm:panel")],
        ])
        await edit(q, "🎯 <b>Filter Keys</b>\n\nChoose filter:", kb)
        return

    if data.startswith("adm:flt:"):
        ok, mode = safe_split_payload(data, 3)
        if not ok:
            await q.answer("❌ Invalid", show_alert=True)
            return
        keys = load_keys()["keys"]
        now = datetime.now()
        results = []
        for r in keys.values():
            expired = False
            if r.get("expires_at"):
                try:
                    expired = datetime.fromisoformat(r["expires_at"]) < now
                except Exception:
                    pass
            if mode == "active" and not r.get("revoked") and not expired:
                results.append(r)
            elif mode == "expired" and expired and not r.get("revoked"):
                results.append(r)
            elif mode == "revoked" and r.get("revoked"):
                results.append(r)
            elif mode == "bound" and r.get("bound_to"):
                results.append(r)
            elif mode == "unbound" and not r.get("bound_to"):
                results.append(r)
        if not results:
            await edit(q, f"🎯 No keys match filter: <b>{mode}</b>",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:filter")]]))
            return
        lines = [f"🎯 <b>Filter: {mode}</b> ({len(results)} results)\n"]
        for r in results[:30]:
            icon = status_emoji(r)
            lines.append(f"{icon} <code>{r['key']}</code> — {r.get('uses', 0)} uses")
        await edit(q, "\n".join(lines)[:3900],
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:filter")]]))
        return

    # ── Search ──
    if data == "adm:search":
        USER_STATE[uid] = "adm_search"
        await edit(q, "🔍 <b>Search Keys</b>\n\nSend a key fragment or note:")
        return

    # ── Revoke ──
    if data == "adm:revoke":
        USER_STATE[uid] = "adm_revoke"
        await edit(q, "🚫 <b>Revoke Key</b>\n\nSend the key to revoke:")
        return

    # ── Delete ──
    if data == "adm:delete":
        USER_STATE[uid] = "adm_delete"
        await edit(q, "🗑️ <b>Delete Key</b>\n\nSend the key to delete permanently:")
        return

    # ── Unbind ──
    if data == "adm:unbind":
        USER_STATE[uid] = "adm_unbind"
        await edit(q, "🔓 <b>Unbind Key</b>\n\nSend the key:")
        return

    # ── Extend ──
    if data == "adm:extend":
        USER_STATE[uid] = "adm_extend_key"
        await edit(q, "⏰ <b>Extend Key</b>\n\nSend the key:")
        return

    if data.startswith("adm:extend_dur:"):
        ok, code = safe_split_payload(data, 3)
        if not ok or code not in KEY_DURATIONS:
            await q.answer("❌ Invalid", show_alert=True)
            return
        pending = context.user_data.get("extend_key")
        if not pending:
            await edit(q, "❌ Session expired.")
            return
        ext_ok, msg = extend_key(pending, code)
        if ext_ok:
            audit(uid, "extend", f"{pending} +{KEY_DURATIONS[code][0]}")
            await edit(q, f"✅ Extended <code>{pending}</code> by <b>{KEY_DURATIONS[code][0]}</b>.",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        else:
            await edit(q, f"❌ {msg}",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Export ──
    if data == "adm:export":
        keys = load_keys()["keys"]
        if not keys:
            await edit(q, "📋 No keys.")
            return
        lines = ["KEY|DURATION|CREATED|EXPIRES|USES|BOUND|REVOKED|PRICE|NOTE"]
        for r in keys.values():
            lines.append(
                f"{r['key']}|{r.get('duration_label', '')}|"
                f"{r.get('created_at', '')}|{r.get('expires_at') or 'never'}|"
                f"{r.get('uses', 0)}|{r.get('bound_to') or '-'}|"
                f"{r.get('revoked', False)}|{r.get('price', '')}|"
                f"{r.get('note', '')}"
            )
        audit(uid, "export", f"{len(keys)} keys")
        await q.message.reply_document(
            document="\n".join(lines).encode(),
            filename=f"keys_export_{int(time.time())}.txt",
            caption=f"📤 {len(keys)} keys exported"
        )
        return

    # ── Backup ──
    if data == "adm:backup":
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = BACKUP_DIR / f"backup_{ts}.json"
        try:
            data_all = {
                "keys": load_keys(),
                "users": load_users(),
                "admins": load_admins(),
                "config": load_config(),
            }
            with open(backup_name, "w", encoding="utf-8") as f:
                json.dump(data_all, f, indent=2)
            audit(uid, "backup", str(backup_name))
            with open(backup_name, "rb") as f:
                await q.message.reply_document(
                    document=f,
                    filename=backup_name.name,
                    caption=f"💾 Full backup — {ts}"
                )
        except Exception as e:
            await edit(q, f"❌ Backup failed: {e}")
        return

    # ── Broadcast ──
    if data == "adm:broadcast":
        USER_STATE[uid] = "adm_broadcast"
        await edit(q, "📢 <b>Broadcast</b>\n\n"
                      "Send the message to broadcast to all tracked users.\n\n"
                      "<i>Send /cancel to abort.</i>")
        return

    # ── Users ──
    if data == "adm:users":
        users = load_users()["users"]
        if not users:
            await edit(q, "👥 No users tracked yet.",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
            return
        items = sorted(users.values(), key=lambda u: u.get("last_seen", ""), reverse=True)[:30]
        lines = [f"👥 <b>Tracked Users</b> ({len(users)} total)\n"]
        for u in items:
            uname = u.get("username", "—")
            uid_v = u.get("uid", "?")
            seen = u.get("last_seen", "")[:16].replace("T", " ")
            lines.append(f"• @{uname} — <code>{uid_v}</code>\n  <i>Last seen: {seen}</i>")
        await edit(q, "\n".join(lines)[:3900],
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Suspended Users ──
    if data == "adm:suspended":
        if not _TRACKING_AVAILABLE:
            await edit(q, "❌ Tracking not available.",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
            return
        suspended = _tracking.get_suspended_list()
        if not suspended:
            await edit(q, "✅ <b>No suspended users</b>",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
            return
        lines = [f"🚫 <b>Suspended Users</b> ({len(suspended)})\n"]
        for u in suspended[:20]:
            lines.append(
                f"🚫 <code>{u['hwid']}</code>\n"
                f"   User: {u.get('username', 'unknown')}\n"
                f"   Reason: {u.get('suspend_reason', 'N/A')}\n"
                f"   Date: {u.get('suspend_date', 'N/A')[:16]}\n"
            )
        await edit(q, "\n".join(lines)[:3900],
                   InlineKeyboardMarkup([
                       [InlineKeyboardButton("🔓 Unsuspend", callback_data="adm:unsuspend")],
                       [InlineKeyboardButton("◀ Back", callback_data="adm:panel")]
                   ]))
        return

    # ── Unsuspend (prompt for HWID) ──
    if data == "adm:unsuspend":
        USER_STATE[uid] = "adm_unsuspend"
        await edit(q, "🔓 <b>Unsuspend User</b>\n\nSend the HWID to unsuspend:")
        return

    # ── Tracking Stats ──
    if data == "adm:tracking":
        if not _TRACKING_AVAILABLE:
            await edit(q, "❌ Tracking not available.",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
            return
        users = _tracking.get_all_users()
        suspended = _tracking.get_suspended_list()
        total_tamper = sum(u.get("tamper_attempts", 0) for u in users)
        total_leak = sum(u.get("leak_attempts", 0) for u in users)
        text = (
            f"📊 <b>Tracking Stats</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 Total users: <b>{len(users)}</b>\n"
            f"🚫 Suspended: <b>{len(suspended)}</b>\n"
            f"⚠️ Tamper attempts: <b>{total_tamper}</b>\n"
            f"📤 Leak attempts: <b>{total_leak}</b>\n"
        )
        await edit(q, text,
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Cleanup ──
    if data == "adm:cleanup":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧹 Clean expired keys", callback_data="adm:cleanup_run")],
            [InlineKeyboardButton("◀ Back", callback_data="adm:panel")],
        ])
        await edit(q, "🧹 <b>Cleanup</b>\n\nThis will delete expired keys with 0 uses.\n\nContinue?", kb)
        return

    if data == "adm:cleanup_run":
        count = cleanup_expired()
        audit(uid, "cleanup", f"{count} removed")
        await edit(q, f"🧹 <b>Cleanup Complete</b>\n\nRemoved <b>{count}</b> expired keys.",
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Analytics ──
    if data == "adm:analytics":
        keys = load_keys()["keys"]
        now = datetime.now()
        total = len(keys)
        revoked = sum(1 for r in keys.values() if r.get("revoked"))
        expired = 0
        active = 0
        bound = 0
        total_uses = 0
        total_revenue = 0.0
        top_keys = []
        for k, r in keys.items():
            total_uses += r.get("uses", 0)
            if r.get("bound_to"):
                bound += 1
            try:
                p = float(r.get("price", 0) or 0)
                total_revenue += p
            except Exception:
                pass
            if r.get("revoked"):
                continue
            if r.get("expires_at"):
                try:
                    if datetime.fromisoformat(r["expires_at"]) < now:
                        expired += 1
                        continue
                except Exception:
                    pass
            active += 1
            top_keys.append((r.get("uses", 0), k))
        top_keys.sort(reverse=True)

        text = (
            f"📈 <b>Analytics</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Total keys: <b>{total}</b>\n"
            f"✅ Active: <b>{active}</b>\n"
            f"⏰ Expired: <b>{expired}</b>\n"
            f"🚫 Revoked: <b>{revoked}</b>\n"
            f"🔒 Bound: <b>{bound}</b>\n"
            f"🎯 Total uses: <b>{total_uses}</b>\n"
            f"💰 Revenue: <b>₱ {total_revenue:.2f}</b>\n\n"
            f"🏆 <b>Top 5 Most Used:</b>\n"
        )
        for uses, k in top_keys[:5]:
            text += f"• <code>{k}</code> — {uses} uses\n"

        await edit(q, text,
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Admins ──
    if data == "adm:admins":
        d = load_admins()
        lines = ["👤 <b>Admin List</b>\n"]
        for a in d["admins"]:
            tag = " (primary)" if a == d.get("primary") else ""
            lines.append(f"• <code>{a}</code>{tag}")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Admin", callback_data="adm:add_admin")],
            [InlineKeyboardButton("➖ Remove Admin", callback_data="adm:rm_admin")],
            [InlineKeyboardButton("◀ Back", callback_data="adm:panel")],
        ])
        await edit(q, "\n".join(lines), kb)
        return

    if data == "adm:add_admin":
        USER_STATE[uid] = "adm_add_admin"
        await edit(q, "➕ <b>Add Admin</b>\n\nSend the Telegram user ID:")
        return

    if data == "adm:rm_admin":
        USER_STATE[uid] = "adm_rm_admin"
        await edit(q, "➖ <b>Remove Admin</b>\n\nSend the Telegram user ID:")
        return

    # ── Config ──
    if data == "adm:config":
        cfg = load_config()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎯 Prefix: {cfg.get('key_prefix', 'COSMIC')}",
                                  callback_data="adm:cfg:prefix")],
            [InlineKeyboardButton(f"📏 Segments: {cfg.get('key_segments', 4)}",
                                  callback_data="adm:cfg:segments")],
            [InlineKeyboardButton(f"📐 Segment Length: {cfg.get('key_segment_len', 4)}",
                                  callback_data="adm:cfg:seglen")],
            [InlineKeyboardButton(f"🧹 Auto-cleanup: {cfg.get('auto_cleanup_hours', 24)}h",
                                  callback_data="adm:cfg:cleanup")],
            [InlineKeyboardButton(f"🔔 Notify on revoke: {'ON' if cfg.get('notify_on_revoke') else 'OFF'}",
                                  callback_data="adm:cfg:notify")],
            [InlineKeyboardButton("◀ Back", callback_data="adm:panel")],
        ])
        await edit(q, "⚙️ <b>Configuration</b>\n\nTap to edit:", kb)
        return

    if data.startswith("adm:cfg:"):
        ok, field = safe_split_payload(data, 3)
        if not ok:
            await q.answer("❌ Invalid", show_alert=True)
            return
        if field == "notify":
            cfg["notify_on_revoke"] = not cfg.get("notify_on_revoke", True)
            save_config(cfg)
            await admin_callback(update, context)
            return
        USER_STATE[uid] = f"adm_cfg:{field}"
        await edit(q, f"⚙️ Send new value for <b>{field}</b>:")
        return

    # ── Stats ──
    if data == "adm:stats":
        keys = load_keys()["keys"]
        users = load_users()["users"]
        admins = load_admins()["admins"]
        now = datetime.now()
        active = expired = revoked = bound = 0
        for r in keys.values():
            if r.get("revoked"):
                revoked += 1
                continue
            if r.get("expires_at"):
                try:
                    if datetime.fromisoformat(r["expires_at"]) < now:
                        expired += 1
                        continue
                except Exception:
                    pass
            active += 1
            if r.get("bound_to"):
                bound += 1
        text = (
            f"📊 <b>Full Stats</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔑 Total: <b>{len(keys)}</b>\n"
            f"✅ Active: <b>{active}</b>\n"
            f"⏰ Expired: <b>{expired}</b>\n"
            f"🚫 Revoked: <b>{revoked}</b>\n"
            f"🔒 Bound: <b>{bound}</b>\n\n"
            f"👥 Users: <b>{len(users)}</b>\n"
            f"👤 Admins: <b>{len(admins)}</b>\n"
        )
        await edit(q, text,
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Audit Log ──
    if data == "adm:audit":
        if not LOG_FILE.exists():
            await edit(q, "📜 No audit log yet.",
                       InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
            return
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()[-30:]
            text = "📜 <b>Recent Audit Log</b>\n\n"
            for line in lines:
                text += f"<code>{line.strip()}</code>\n"
        except Exception as e:
            text = f"❌ {e}"
        await edit(q, text[:3900],
                   InlineKeyboardMarkup([[InlineKeyboardButton("◀ Back", callback_data="adm:panel")]]))
        return

    # ── Fallback ──
    await q.answer("❌ Unknown action.")


# ══════════════════════════════════════════════════════════════════════════
#  TEXT ROUTER — STATE MACHINE FOR KEY GENERATION
#
#  NEW FLOW:
#   1. User taps "Generate Key"
#   2. Picks duration
#   3. Bot asks for PRICE (step 2/3)
#   4. User sends price
#   5. Bot asks for NOTE (step 3/3)
#   6. User sends note (or "skip" to skip)
#   7. Key is generated + receipt shown
# ══════════════════════════════════════════════════════════════════════════
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    txt = update.message.text.strip()

    if not _check_rate_limit(u.id):
        await update.message.reply_text("⚠️ Slow down. Rate limit reached.")
        return

    if txt == "👑 Admin Panel":
        return await cmd_admin(update, context)

    if not is_admin(u.id):
        return

    track_user(u.id, u.username or u.first_name)
    state = USER_STATE.get(u.id)

    # ═══════════════════════════════════════════════════════════════════
    #  NEW KEY GENERATION FLOW
    # ═══════════════════════════════════════════════════════════════════

    # ── STEP 2: AWAITING PRICE ──
    if state == "adm_keygen_price":
        price = txt.replace("₱", "").replace("P", "").strip()
        if not price:
            await update.message.reply_text("❌ Please send a valid price.")
            return
        context.user_data["pending_price"] = price
        USER_STATE[u.id] = "adm_keygen_note"
        await update.message.reply_text(
            f"🔑 <b>Generate Key — Step 3/3</b>\n\n"
            f"💰 Price: <b>₱ {price}</b>\n\n"
            f"📝 Send a <b>Note</b> (optional):\n"
            f"<i>Send <code>skip</code> to leave it blank.</i>",
            parse_mode=ParseMode.HTML
        )
        return

    # ── STEP 3: AWAITING NOTE → GENERATE KEY ──
    if state == "adm_keygen_note":
        note = "" if txt.lower() in ("skip", "none", "-", "") else txt[:200]
        duration = context.user_data.pop("pending_duration", None)
        price = context.user_data.pop("pending_price", "")
        USER_STATE.pop(u.id, None)

        if not duration or duration not in KEY_DURATIONS:
            await update.message.reply_text("❌ Session expired. Please start again.")
            return

        try:
            rec = create_key(duration, note=note, price=price, created_by=u.id)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed: {e}")
            return

        audit(u.id, "genkey", f"{rec['key']} | ₱{price} | {note}")
        receipt = format_key_receipt(rec)
        receipt_plain = format_key_receipt_plain(rec)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy Plain Text",
                                  callback_data=f"adm:copy:{rec['key']}")],
            [InlineKeyboardButton("🔑 Another", callback_data="adm:genkey"),
             InlineKeyboardButton("◀ Panel", callback_data="adm:panel")],
        ])

        await update.message.reply_text(receipt, parse_mode=ParseMode.HTML, reply_markup=kb)
        await update.message.reply_text(
            f"<b>📋 Plain-text (tap to copy):</b>\n\n<pre>{receipt_plain}</pre>",
            parse_mode=ParseMode.HTML
        )
        return

    # ═══════════════════════════════════════════════════════════════════
    #  OTHER STATE HANDLERS
    # ═══════════════════════════════════════════════════════════════════

    # ── Add Note (existing keys) ──
    if state and state.startswith("adm_note:"):
        USER_STATE.pop(u.id, None)
        ok, key = safe_split_payload(state, 3)
        if not ok:
            await update.message.reply_text("❌ Invalid state. Tap the button again.")
            return
        data = load_keys()
        k = key.upper()
        if k not in data["keys"]:
            await update.message.reply_text("❌ Key not found.")
            return
        data["keys"][k]["note"] = txt[:200]
        save_keys(data)
        await update.message.reply_text(f"✅ Note added to <code>{k}</code>.",
                                        parse_mode=ParseMode.HTML)
        return

    # ── Search ──
    if state == "adm_search":
        USER_STATE.pop(u.id, None)
        keys = load_keys()["keys"]
        q = txt.upper()
        matches = [r for k, r in keys.items()
                   if q in k.upper() or q in (r.get("note", "") or "").upper()
                   or q in (r.get("price", "") or "").upper()]
        if not matches:
            await update.message.reply_text("🔍 No matches.")
            return
        lines = [f"🔍 <b>{len(matches)} match(es)</b>\n"]
        for r in matches[:20]:
            icon = status_emoji(r)
            exp = fmt_remaining(r.get("expires_at"))
            lines.append(f"{icon} <code>{r['key']}</code> — {exp}")
        await update.message.reply_text("\n".join(lines)[:3800], parse_mode=ParseMode.HTML)
        return

    # ── Revoke ──
    if state == "adm_revoke":
        USER_STATE.pop(u.id, None)
        k = txt.upper()
        if revoke_key(k):
            audit(u.id, "revoke", k)
            await update.message.reply_text(f"🚫 Revoked <code>{k}</code>.",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Not found.")
        return

    # ── Delete ──
    if state == "adm_delete":
        USER_STATE.pop(u.id, None)
        k = txt.upper()
        if delete_key(k):
            audit(u.id, "delete", k)
            await update.message.reply_text(f"🗑️ Deleted <code>{k}</code>.",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Not found.")
        return

    # ── Unbind ──
    if state == "adm_unbind":
        USER_STATE.pop(u.id, None)
        k = txt.upper()
        if unbind_key(k):
            audit(u.id, "unbind", k)
            await update.message.reply_text(f"🔓 Unbound <code>{k}</code>.",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Not found.")
        return

    # ── Extend step 1 ──
    if state == "adm_extend_key":
        USER_STATE.pop(u.id, None)
        k = txt.upper()
        keys = load_keys()["keys"]
        if k not in keys:
            await update.message.reply_text("❌ Not found.")
            return
        context.user_data["extend_key"] = k
        await update.message.reply_text(
            f"⏰ Extend <code>{k}</code> — pick duration:",
            parse_mode=ParseMode.HTML,
            reply_markup=duration_kb("adm:extend_dur", cols=3))
        return

    # ── Broadcast ──
    if state == "adm_broadcast":
        USER_STATE.pop(u.id, None)
        users = load_users()["users"]
        if not users:
            await update.message.reply_text("👥 No users to broadcast to.")
            return
        asyncio.create_task(_run_broadcast(context, u.id, txt, users))
        await update.message.reply_text(
            f"📢 Broadcasting to {len(users)} users...\n"
            f"<i>You'll get a summary when done.</i>",
            parse_mode=ParseMode.HTML
        )
        return

    # ── Add Admin ──
    if state == "adm_add_admin":
        USER_STATE.pop(u.id, None)
        try:
            new_uid = int(txt)
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")
            return
        if add_admin(new_uid):
            audit(u.id, "add_admin", str(new_uid))
            await update.message.reply_text(f"✅ Added admin: <code>{new_uid}</code>.",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Already an admin.")
        return

    # ── Remove Admin ──
    if state == "adm_rm_admin":
        USER_STATE.pop(u.id, None)
        try:
            rm_uid = int(txt)
        except ValueError:
            await update.message.reply_text("❌ Invalid ID.")
            return
        if remove_admin(rm_uid):
            audit(u.id, "rm_admin", str(rm_uid))
            await update.message.reply_text(f"✅ Removed admin: <code>{rm_uid}</code>.",
                                            parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Cannot remove (not found or is primary).")
        return

    # ── Unsuspend User ──
    if state == "adm_unsuspend":
        USER_STATE.pop(u.id, None)
        hwid = txt.strip()
        if not _TRACKING_AVAILABLE:
            await update.message.reply_text("❌ Tracking not available.")
            return
        if _tracking.unsuspend_user(hwid):
            audit(u.id, "unsuspend", hwid)
            await update.message.reply_text(
                f"✅ <b>Unsuspended</b>\n\n<code>{hwid}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(f"❌ Not found: <code>{hwid}</code>",
                                            parse_mode=ParseMode.HTML)
        return

    # ── Config change ──
    if state and state.startswith("adm_cfg:"):
        USER_STATE.pop(u.id, None)
        ok, field = safe_split_payload(state, 3)
        if not ok:
            await update.message.reply_text("❌ Invalid state.")
            return
        cfg = load_config()
        try:
            if field in ("segments", "seglen", "cleanup"):
                val = int(txt)
                if field == "segments":
                    cfg["key_segments"] = max(1, min(6, val))
                elif field == "seglen":
                    cfg["key_segment_len"] = max(2, min(8, val))
                elif field == "cleanup":
                    cfg["auto_cleanup_hours"] = max(1, val)
            elif field == "prefix":
                cfg["key_prefix"] = txt.upper()[:12]
            save_config(cfg)
            audit(u.id, "config", f"{field}={txt}")
            await update.message.reply_text(f"✅ Config updated: <b>{field}</b>",
                                            parse_mode=ParseMode.HTML)
        except ValueError:
            await update.message.reply_text("❌ Invalid value.")
        return

    await update.message.reply_text("Use /start or /admin", reply_markup=main_menu(u.id))


# ══════════════════════════════════════════════════════════════════════════
#  AUTO-CLEANUP TASK
# ══════════════════════════════════════════════════════════════════════════
async def auto_cleanup_task(context: ContextTypes.DEFAULT_TYPE):
    try:
        cfg = load_config()
        interval = cfg.get("auto_cleanup_hours", 24)
        count = cleanup_expired()
        if count > 0:
            log.info(f"[AUTO-CLEANUP] Removed {count} expired keys")
        context.job_queue.run_once(auto_cleanup_task, interval * 3600)
    except Exception as e:
        log.error(f"auto_cleanup: {e}")


# ══════════════════════════════════════════════════════════════════════════
#  CALLBACK + ERROR + INIT
# ══════════════════════════════════════════════════════════════════════════
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data or ""
    if data.startswith("adm:"):
        await admin_callback(update, context)
        return
    await q.answer("❌ Unknown.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors — don't crash on network issues."""
    import telegram.error
    err = context.error
    
    # Re-apply DNS fix on network errors
    if isinstance(err, telegram.error.NetworkError):
        try:
            from dns_fix import fix_dns
            fix_dns()
            log.warning(f"Network error (DNS re-fixed): {err}")
        except Exception:
            log.error(f"Network error: {err}")
    else:
        log.error("Error:", exc_info=err)


async def post_init(application: Application):
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bf = BACKUP_DIR / f"auto_backup_{ts}.json"
        bd = {
            "keys": load_keys(), "users": load_users(),
            "admins": load_admins(), "config": load_config(),
            "timestamp": datetime.now().isoformat(),
        }
        with open(bf, "w", encoding="utf-8") as f:
            json.dump(bd, f, indent=2)
        log.info(f"Auto-backup: {bf}")
    except Exception as e:
        log.error(f"Auto-backup failed: {e}")
    cfg = load_config()
    interval = cfg.get("auto_cleanup_hours", 24)
    if application.job_queue:
        application.job_queue.run_once(auto_cleanup_task, 60)
    log.info(f"Auto-cleanup scheduled every {interval}h")


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    # ─── OWNER LOCK ───
    _enforce_bot_owner()
    
    # Re-apply DNS fix right before starting
    try:
        from dns_fix import fix_dns
        fix_dns()
    except Exception:
        pass
    
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .pool_timeout(60.0)
        .get_updates_connect_timeout(60.0)
        .get_updates_read_timeout(60.0)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    log.info("COSMIC Admin Bot starting...")
    log.info("Retrying connection... (this may take a minute)")
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║   🤖 COSMIC ADMIN BOT                                  ║
║   ════════════════════════════════════════════════════════  ║
║   👤 Primary Admin: {ADMIN_ID}
║   🎯 Keys File:     keys.json
║   💾 Backups Dir:   backups/
║   📜 Audit Log:     audit.log
║   ════════════════════════════════════════════════════════  ║
║   {CREDIT_LINE}
║   ✅ Running... Ctrl+C to stop
╚══════════════════════════════════════════════════════════════╝
""")
    # Run with retry loop
    import time as _t
    max_retries = 10
    for attempt in range(max_retries):
        try:
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False,
            )
            break
        except Exception as e:
            log.error(f"Run failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                _t.sleep(5)
                try:
                    from dns_fix import fix_dns
                    fix_dns()
                except Exception:
                    pass
            else:
                raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
    except Exception as e:
        log.exception("Fatal")
        print(f"\n❌ Fatal: {e}")