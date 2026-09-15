#!/usr/bin/env python3
"""
COSMIC SECURITY — Source integrity + anti-tamper + obfuscation.
"""
import os
import sys
import json
import hashlib
import hmac
import base64
import secrets
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.resolve()

# Try to import tracking for reporting
try:
    import tracking as _tracking
    _TRACKING_AVAILABLE = True
except Exception:
    _TRACKING_AVAILABLE = False

INTEGRITY_FILE = BASE_DIR / ".integrity"
SECRET_FILE = BASE_DIR / ".secret"

# Files na dapat protektado
PROTECTED_FILES = [
    "cosmicloaderFORSALE.py",
    "updater.py",
    "security.py",
    "dns_fix.py",
]

# Admin HWID (owner lang makaka-view ng source)
# I-change mo 'to sa HWID mo
# Multiple owner HWIDs (any match = owner)
OWNER_HWIDS = [
    "7b71ea74eced",  # Owner HWID #1
    "a3607276ce52",  # Owner HWID #2 (fallback)
]

# Stable owner key (password-based, hindi nagbabago)
OWNER_KEY = "COSMIC-OWNER-2026"  # ← secret word mo

# Owner bypass file (para sa owner lang)
OWNER_BYPASS_FILE = BASE_DIR / ".owner"


# ═══════════════════════════════════════════════════════════
#  HASHING
# ═══════════════════════════════════════════════════════════
def _hash_file(path: Path) -> str:
    """SHA-256 hash ng file."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def _get_secret() -> bytes:
    """Get or create secret key for HMAC."""
    if SECRET_FILE.exists():
        try:
            return base64.b64decode(SECRET_FILE.read_text().strip())
        except Exception:
            pass
    # Create new secret
    s = secrets.token_bytes(32)
    try:
        SECRET_FILE.write_text(base64.b64encode(s).decode())
        os.chmod(SECRET_FILE, 0o600)
    except Exception:
        pass
    return s


def generate_integrity():
    """Generate integrity manifest ng lahat ng protected files."""
    secret = _get_secret()
    manifest = {
        "generated": datetime.now().isoformat(),
        "files": {},
    }
    for fname in PROTECTED_FILES:
        fpath = BASE_DIR / fname
        if fpath.exists():
            file_hash = _hash_file(fpath)
            # HMAC para hindi ma-forge
            sig = hmac.new(secret, file_hash.encode(), hashlib.sha256).hexdigest()
            manifest["files"][fname] = {
                "hash": file_hash,
                "sig": sig,
                "size": fpath.stat().st_size,
            }
    try:
        INTEGRITY_FILE.write_text(json.dumps(manifest, indent=2))
        os.chmod(INTEGRITY_FILE, 0o600)
    except Exception:
        pass
    return manifest


def verify_integrity() -> tuple:
    """
    Verify lahat ng protected files.
    Returns (ok, tampered_files).
    """
    if not INTEGRITY_FILE.exists():
        # First run — generate manifest
        generate_integrity()
        return True, []

    try:
        manifest = json.loads(INTEGRITY_FILE.read_text())
    except Exception:
        return True, []

    secret = _get_secret()
    tampered = []

    for fname, rec in manifest.get("files", {}).items():
        fpath = BASE_DIR / fname
        if not fpath.exists():
            tampered.append(fname)
            continue
        current_hash = _hash_file(fpath)
        if current_hash != rec.get("hash"):
            tampered.append(fname)
            continue
        # Verify HMAC
        expected_sig = hmac.new(secret, current_hash.encode(), hashlib.sha256).hexdigest()
        if expected_sig != rec.get("sig"):
            tampered.append(fname)

    return (len(tampered) == 0), tampered


# ═══════════════════════════════════════════════════════════
#  HWID CHECK
# ═══════════════════════════════════════════════════════════
def get_hwid() -> str:
    """Get STABLE machine HWID (combine multiple sources)."""
    try:
        import uuid
        import platform
        import socket
        
        parts = []
        
        # 1. MAC address (primary)
        try:
            parts.append(f"{uuid.getnode():012x}")
        except Exception:
            pass
        
        # 2. Hostname
        try:
            parts.append(socket.gethostname())
        except Exception:
            pass
        
        # 3. Platform info
        try:
            parts.append(platform.machine())
        except Exception:
            pass
        
        # Combine + hash for stable ID
        combined = "|".join(str(p) for p in parts if p)
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
    except Exception:
        return "unknown"


def get_hwid_alt() -> str:
    """Alternative HWID (MAC-only, legacy)."""
    try:
        import uuid
        return f"{uuid.getnode():012x}"
    except Exception:
        return "unknown"


def is_owner() -> bool:
    """Check if running on owner's machine (multi-method)."""
    # Method 1: Bypass file
    if OWNER_BYPASS_FILE.exists():
        try:
            content = OWNER_BYPASS_FILE.read_text().strip()
            if content == OWNER_KEY:
                return True
        except Exception:
            pass
    
    # Method 2: HWID match (multiple formats)
    try:
        hwid = get_hwid()
        hwid_alt = get_hwid_alt()
        if hwid in OWNER_HWIDS or hwid_alt in OWNER_HWIDS:
            return True
    except Exception:
        pass
    
    # Method 3: Environment variable (para sa testing)
    try:
        if os.getenv("COSMIC_OWNER") == "1":
            return True
    except Exception:
        pass
    
    return False


def create_owner_bypass():
    """Create .owner file para maging owner."""
    try:
        OWNER_BYPASS_FILE.write_text(OWNER_KEY)
        os.chmod(OWNER_BYPASS_FILE, 0o600)
        print(f"✅ Created: {OWNER_BYPASS_FILE}")
        print(f"✅ You are now OWNER")
    except Exception as e:
        print(f"❌ Failed: {e}")


# ═══════════════════════════════════════════════════════════
#  ANTI-TAMPER — kill if modified
# ═══════════════════════════════════════════════════════════
def enforce_integrity():
    """Check integrity + block if tampered (non-owner)."""
    ok, tampered = verify_integrity()
    if ok:
        return True

    # Owner pwede pa rin
    if is_owner():
        return True

    # Report tamper to admin
    if _TRACKING_AVAILABLE:
        try:
            import os
            username = os.getenv("USER", "unknown")
            _tracking.report_tamper(tampered, username=username)
        except Exception:
            pass
    
    # Tampered — WARN ONLY, don't exit
    w = 66
    print()
    print(f"  \033[38;2;255;200;100m┏{'━' * w}┓\033[0m")
    print(f"  \033[38;2;255;200;100m┃\033[0m\033[1m\033[38;2;230;240;255m{'⚠  INTEGRITY NOTICE'.center(w)}\033[0m\033[38;2;255;200;100m┃\033[0m")
    print(f"  \033[38;2;255;200;100m┣{'━' * w}┫\033[0m")
    print(f"  \033[38;2;255;200;100m┃\033[0m  \033[2mSome files were modified:\033[0m")
    for f in tampered[:5]:
        print(f"  \033[38;2;255;200;100m┃\033[0m    \033[38;2;255;200;100m•\033[0m \033[38;2;230;240;255m{f}\033[0m")
    print(f"  \033[38;2;255;200;100m┃\033[0m")
    print(f"  \033[38;2;255;200;100m┃\033[0m  \033[2mLoader will continue. Auto-fixing integrity...\033[0m")
    print(f"  \033[38;2;255;200;100m┗{'━' * w}┛\033[0m")
    print()
    
    # Auto-regenerate integrity
    try:
        generate_integrity()
    except Exception:
        pass
    
    import time
    time.sleep(1.5)
    return True


# ═══════════════════════════════════════════════════════════
#  SOURCE HIDING — only show to owner
# ═══════════════════════════════════════════════════════════
def require_owner():
    """Block non-owner from viewing source."""
    if not is_owner():
        print("\n  \033[38;2;255;100;120m✖  Access denied. Owner only.\033[0m\n")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════
#  AUTO-RUN ON IMPORT
# ═══════════════════════════════════════════════════════════
if __name__ != "__main__":
    try:
        enforce_integrity()
    except SystemExit:
        raise
    except Exception:
        pass


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["generate", "verify", "hwid", "reset", "iamowner", "revoke"])
    args = ap.parse_args()

    if args.action == "generate":
        m = generate_integrity()
        print(f"✅ Generated integrity for {len(m['files'])} files")
    elif args.action == "verify":
        ok, bad = verify_integrity()
        print(f"OK: {ok}")
        if bad:
            print(f"Tampered: {bad}")
    elif args.action == "hwid":
        print(f"HWID: {get_hwid()}")
    elif args.action == "reset":
        if INTEGRITY_FILE.exists():
            INTEGRITY_FILE.unlink()
        print("✅ Integrity reset")
    elif args.action == "iamowner":
        create_owner_bypass()
    elif args.action == "revoke":
        if OWNER_BYPASS_FILE.exists():
            OWNER_BYPASS_FILE.unlink()
            print("✅ Owner bypass revoked")
