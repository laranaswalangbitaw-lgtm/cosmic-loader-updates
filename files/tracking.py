#!/usr/bin/env python3
"""
COSMIC TRACKING — Anti-leak, tamper detection, auto-suspend.
"""
import os
import json
import hashlib
import socket
import platform
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
TRACK_FILE = BASE_DIR / "user_tracking.json"

# ─── SUSPEND CONTROL ───
SUSPEND_ENABLED = False  # ← Auto-suspend DISABLED

SUSPEND_FILE = BASE_DIR / "suspended_users.json"

# ═══════════════════════════════════════════════════════════
#  CONFIG — I-set mo 'to sa Telegram
# ═══════════════════════════════════════════════════════════
ADMIN_BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # Auto-load from .env
ADMIN_CHAT_ID = os.getenv("ADMIN_ID", "")     # Auto-load from .env


# Persistent HWID file
_HWID_FILE = BASE_DIR / ".hwid"

def _get_hwid():
    """Get or create persistent HWID (stable across runs)."""
    # Return saved HWID if exists
    if _HWID_FILE.exists():
        try:
            hwid = _HWID_FILE.read_text().strip()
            if hwid and len(hwid) == 12:
                return hwid
        except Exception:
            pass
    
    # Generate new stable HWID
    try:
        import uuid
        import random
        parts = [
            f"{uuid.getnode():012x}",
            socket.gethostname(),
            platform.machine(),
            os.getenv("ANDROID_ID", "no_id"),
            str(random.randint(0, 999999999)),
        ]
        combined = "|".join(p for p in parts if p)
        hwid = hashlib.sha256(combined.encode()).hexdigest()[:12]
    except Exception:
        hwid = "unknown"
    
    # Save for next run
    try:
        _HWID_FILE.write_text(hwid)
        os.chmod(_HWID_FILE, 0o600)
    except Exception:
        pass
    
    return hwid



def _save_user_session(username, key):
    """Save username + key for tamper reports."""
    try:
        import json as _json
        session_path = BASE_DIR / ".user_session"
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(_json.dumps({
            "username": username,
            "key": key,
        }))
    except Exception:
        pass


def report_key_use(key_str):
    """Report key usage to GitHub (increment uses counter)."""
    try:
        import requests
        import json
        from pathlib import Path as _P
        
        # Load GitHub token from config
        token_file = _P("/storage/emulated/0/COSMIC-LOADER-v4.0/.github_token")
        if not token_file.exists():
            return False
        
        GITHUB_TOKEN = token_file.read_text().strip()
        if not GITHUB_TOKEN:
            return False
        
        REPO = "laranaswalangbitaw-lgtm/cosmic-loader-updates"
        FILE_PATH = "files/keys.json"
        
        api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        r = requests.get(api_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return False
        
        file_data = r.json()
        import base64
        content = base64.b64decode(file_data["content"]).decode("utf-8")
        keys_data = json.loads(content)
        
        if key_str in keys_data.get("keys", {}):
            current_uses = keys_data["keys"][key_str].get("uses", 0)
            keys_data["keys"][key_str]["uses"] = current_uses + 1
            keys_data["keys"][key_str]["last_used"] = datetime.now().isoformat()
            
            new_content = json.dumps(keys_data, indent=2)
            new_content_b64 = base64.b64encode(new_content.encode()).decode()
            
            update_data = {
                "message": f"Report key use: {key_str}",
                "content": new_content_b64,
                "sha": file_data["sha"],
            }
            
            r2 = requests.put(api_url, headers=headers, json=update_data, timeout=10)
            return r2.status_code == 200
    except Exception:
        pass
    return False


def _notify_admin(message, urgent=False):
    """Send Telegram notification to admin."""
    try:
        import requests
        from pathlib import Path as _P
        
        env_file = _P("/storage/emulated/0/test_Tools2/.env")
        bot_token = ""
        admin_id = ""
        
        if env_file.exists():
            for line in env_file.read_text().split("\n"):
                line = line.strip()
                if line.startswith("BOT_TOKEN="):
                    bot_token = line.split("=", 1)[1].strip()
                elif line.startswith("ADMIN_ID="):
                    admin_id = line.split("=", 1)[1].strip()
        
        if not bot_token or not admin_id:
            return False
        
        prefix = "URGENT" if urgent else "NOTICE"
        full_text = prefix + " - COSMIC SECURITY\n\n" + str(message)
        
        url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
        resp = requests.post(url, json={
            "chat_id": admin_id,
            "text": full_text,
            "disable_notification": not urgent,
        }, timeout=10)
        
        return resp.status_code == 200
    except Exception as e:
        try:
            print("Notify error: " + str(e))
        except Exception:
            pass
        return False


def _load_json(path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _save_json(path, data):
    try:
        path.write_text(json.dumps(data, indent=2))
        os.chmod(path, 0o600)
        # Auto-sync to loader
        try:
            import shutil
            loader = Path("/storage/emulated/0/COSMIC-LOADER-v4.0/user_tracking.json")
            if str(path).endswith("user_tracking.json"):
                loader.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, loader)
        except Exception:
            pass
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════
#  TRACK USER ACTIVITY
# ═══════════════════════════════════════════════════════════
def register_user(username=None, key=None):
    """Register/track user sa database."""
    hwid = _get_hwid()
    data = _load_json(TRACK_FILE, {"users": {}})
    
    if "users" not in data:
        data["users"] = {}
    
    if hwid not in data["users"]:
        data["users"][hwid] = {
            "hwid": hwid,
            "username": username or "unknown",
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "session_count": 0,
            "keys_used": [],
            "tamper_attempts": 0,
            "leak_attempts": 0,
            "suspended": False,
            "suspend_reason": "",
            "suspend_date": None,
        }
    
    user = data["users"][hwid]
    user["last_seen"] = datetime.now().isoformat()
    user["session_count"] += 1
    if username:
        user["username"] = username
    if key and key not in user["keys_used"]:
        user["keys_used"].append(key)
    
    _save_json(TRACK_FILE, data)
    return hwid, user


def is_suspended(hwid=None):
    """Check if user is suspended. ALWAYS FALSE (disabled)."""
    if not SUSPEND_ENABLED:
        return False, ""
    if hwid is None:
        hwid = _get_hwid()
    data = _load_json(TRACK_FILE, {"users": {}})
    user = data.get("users", {}).get(hwid)
    if user and user.get("suspended"):
        return True, user.get("suspend_reason", "Unknown")
    return False, ""


def suspend_user(reason="Security violation", hwid=None):
    """Suspend a user."""
    if hwid is None:
        hwid = _get_hwid()
    data = _load_json(TRACK_FILE, {"users": {}})
    if hwid not in data.get("users", {}):
        return False
    user = data["users"][hwid]
    user["suspended"] = True
    user["suspend_reason"] = reason
    user["suspend_date"] = datetime.now().isoformat()
    _save_json(TRACK_FILE, data)
    return True


def unsuspend_user(hwid):
    """Unsuspend a user (admin only)."""
    data = _load_json(TRACK_FILE, {"users": {}})
    if hwid not in data.get("users", {}):
        return False
    data["users"][hwid]["suspended"] = False
    data["users"][hwid]["suspend_reason"] = ""
    data["users"][hwid]["suspend_date"] = None
    data["users"][hwid]["tamper_attempts"] = 0
    data["users"][hwid]["leak_attempts"] = 0
    _save_json(TRACK_FILE, data)
    return True


# ═══════════════════════════════════════════════════════════
#  ANTI-TAMPER REPORTING
# ═══════════════════════════════════════════════════════════
def report_tamper(files_modified, username=None, key=None):
    """Report tamper + notify admin via Telegram."""
    hwid = _get_hwid()
    
    # Try to get username + key from session file
    if not username or username == "unknown":
        try:
            session_path = BASE_DIR / ".user_session"
            if session_path.exists():
                import json as _json
                session_data = _json.loads(session_path.read_text())
                if session_data.get("username"):
                    username = session_data["username"]
                if session_data.get("key"):
                    key = session_data["key"]
        except Exception:
            pass
    
    data = _load_json(TRACK_FILE, {"users": {}})
    
    if hwid not in data.get("users", {}):
        data.setdefault("users", {})[hwid] = {
            "hwid": hwid,
            "username": username or "unknown",
            "first_seen": datetime.now().isoformat(),
        }
    
    user = data["users"][hwid]
    user["tamper_attempts"] = user.get("tamper_attempts", 0) + 1
    user["last_tamper"] = datetime.now().isoformat()
    user["last_tamper_files"] = files_modified
    user["last_seen"] = datetime.now().isoformat()
    if username and username != "unknown":
        user["username"] = username
    if key and key != "unknown":
        user["key_used"] = key
    
    _save_json(TRACK_FILE, data)
    
    # Build notification
    display_username = username if username and username != "unknown" else "Unknown (not logged in)"
    display_key = key if key and key != "unknown" else "Not logged in"
    
    msg = (
        f"<b>🚨 TAMPER DETECTED</b>\n\n"
        f"👤 Username: <b>{display_username}</b>\n"
        f"🆔 HWID: <code>{hwid}</code>\n"
        f"🔑 Key: <code>{display_key}</code>\n\n"
        f"📁 Modified files:\n"
    )
    for f in files_modified[:5]:
        msg += f"  • <code>{f}</code>\n"
    msg += f"\n⚠️ <b>User needs manual review</b>\n"
    msg += f"Use bot panel to suspend if needed."
    
    _notify_admin(msg, urgent=True)
    return True



def report_leak_detected(leaked_to=None, extra_info=None):
    """Report na may nag-leak ng source."""
    hwid = _get_hwid()
    data = _load_json(TRACK_FILE, {"users": {}})
    
    if hwid not in data.get("users", {}):
        register_user()
        data = _load_json(TRACK_FILE, {"users": {}})
    
    user = data["users"][hwid]
    user["leak_attempts"] = user.get("leak_attempts", 0) + 1
    user["last_leak_attempt"] = datetime.now().isoformat()
    user["suspended"] = True
    user["suspend_reason"] = f"Leak detected ({user['leak_attempts']}x)"
    user["suspend_date"] = datetime.now().isoformat()
    
    _save_json(TRACK_FILE, data)
    
    msg = (
        f"<b>🚨 LEAK DETECTED</b>\n\n"
        f"👤 Username: <b>{user.get('username', 'unknown')}</b>\n"
        f"🆔 HWID: <code>{hwid}</code>\n"
        f"🔑 Keys used: {len(user.get('keys_used', []))}\n"
        f"📤 Leaked to: <code>{leaked_to or 'unknown'}</code>\n"
        f"ℹ️ {extra_info or 'N/A'}\n\n"
        f"⚠️ <b>User needs manual review</b>"
    )
    _notify_admin(msg, urgent=True)
    return True


# ═══════════════════════════════════════════════════════════
#  GET STATS
# ═══════════════════════════════════════════════════════════
def get_suspended_list():
    """Get all suspended users."""
    data = _load_json(TRACK_FILE, {"users": {}})
    suspended = []
    for hwid, u in data.get("users", {}).items():
        if u.get("suspended"):
            suspended.append(u)
    return suspended


def get_all_users():
    """Get all tracked users."""
    data = _load_json(TRACK_FILE, {"users": {}})
    return list(data.get("users", {}).values())


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            users = get_all_users()
            print(f"Total users: {len(users)}")
            for u in users:
                status = "🚫 SUSPENDED" if u.get("suspended") else "✅ Active"
                print(f"  {status} | {u['hwid']} | {u.get('username', '?')}")
        elif cmd == "suspended":
            users = get_suspended_list()
            print(f"Suspended: {len(users)}")
            for u in users:
                print(f"  🚫 {u['hwid']} | {u.get('username', '?')} | {u.get('suspend_reason', '')}")
        elif cmd == "unsuspend" and len(sys.argv) > 2:
            hwid = sys.argv[2]
            if unsuspend_user(hwid):
                print(f"✅ Unsuspended: {hwid}")
            else:
                print(f"❌ Not found: {hwid}")
