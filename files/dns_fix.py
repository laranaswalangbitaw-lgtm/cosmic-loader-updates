#!/usr/bin/env python3
"""
ULTIMATE DNS FIX — Forces Telegram API to use hardcoded IPs.
Works even if Android resets /etc/resolv.conf.
"""
import os
import socket
from pathlib import Path

# ── Telegram API IPs (multiple fallbacks) ────────────────────
TELEGRAM_IPS = {
    "api.telegram.org": ["149.154.166.110", "149.154.167.220", "149.154.175.50"],
    "core.telegram.org": ["149.154.167.99"],
    "telegram.org": ["149.154.167.99"],
    "t.me": ["149.154.167.99"],
}

# ── DNS servers ──────────────────────────────────────────────
DNS_SERVERS = ["1.1.1.1", "8.8.8.8", "8.8.4.4", "9.9.9.9"]


def _write_resolv_conf():
    """Force-write resolv.conf."""
    try:
        prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        resolv = Path(prefix) / "etc" / "resolv.conf"
        resolv.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(f"nameserver {s}" for s in DNS_SERVERS) + "\n"
        if not resolv.exists() or resolv.read_text() != content:
            resolv.write_text(content)
    except Exception:
        pass


def _write_hosts_file():
    """Force-write /etc/hosts with all Telegram IPs."""
    try:
        prefix = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")
        hosts = Path(prefix) / "etc" / "hosts"
        hosts.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing
        existing = ""
        if hosts.exists():
            existing = hosts.read_text()
        
        # Check if we need to update
        needs_update = False
        for host, ips in TELEGRAM_IPS.items():
            if host not in existing:
                needs_update = True
                break
        
        if needs_update:
            with open(hosts, "a") as f:
                f.write("\n# Telegram (auto-added)\n")
                for host, ips in TELEGRAM_IPS.items():
                    for ip in ips:
                        f.write(f"{ip} {host}\n")
    except Exception:
        pass


def _monkey_patch_dns():
    """Monkey-patch socket.getaddrinfo to fallback to hardcoded IPs."""
    _original_getaddrinfo = socket.getaddrinfo
    
    def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return _original_getaddrinfo(host, port, family, type, proto, flags)
        except (socket.gaierror, OSError):
            # DNS failed — try hardcoded IPs
            host_str = host.decode() if isinstance(host, bytes) else host
            if host_str in TELEGRAM_IPS:
                results = []
                for ip in TELEGRAM_IPS[host_str]:
                    try:
                        return _original_getaddrinfo(ip, port, family, type, proto, flags)
                    except Exception:
                        continue
            raise
    
    socket.getaddrinfo = _patched_getaddrinfo


def _patch_httpx_dns():
    """Also patch httpx's DNS resolver if available."""
    try:
        import httpx
        # httpx uses socket.getaddrinfo internally, so monkey-patch is enough
    except ImportError:
        pass


def fix_dns():
    """Apply all DNS fixes."""
    _write_resolv_conf()
    _write_hosts_file()
    _monkey_patch_dns()
    _patch_httpx_dns()
    
    # Set global socket timeout
    try:
        socket.setdefaulttimeout(30)
    except Exception:
        pass
    
    return True


# ── Auto-apply on import ─────────────────────────────────────
fix_dns()


if __name__ == "__main__":
    print("✅ ULTIMATE DNS FIX applied")
    print(f"  resolv.conf: {len(DNS_SERVERS)} servers")
    print(f"  /etc/hosts: {sum(len(v) for v in TELEGRAM_IPS.values())} entries")
    print(f"  socket.getaddrinfo: monkey-patched")
