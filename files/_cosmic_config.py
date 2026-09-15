"""Global speed + accuracy config for COSMIC tools."""
import os

# ── Network ────────────────────────────────────────────────
TIMEOUT_CONNECT = 3       # seconds
TIMEOUT_READ = 6          # seconds
TIMEOUT_TOTAL = 10        # seconds

# ── Threads ────────────────────────────────────────────────
THREADS_DEFAULT = 50
THREADS_MAX = 100
THREADS_PROXY_BONUS = 1.5  # multiply when proxy enabled

# ── Retry ──────────────────────────────────────────────────
RETRY_MAX = 12
RETRY_BASE = 0.3
RETRY_CAP = 3.0
RETRY_JITTER = 0.5

# ── Proxy health ───────────────────────────────────────────
PROXY_FAIL_THRESHOLD = 5
PROXY_COOLDOWN = 60
PROXY_MIN_SUCCESS_RATE = 0.3

# ── Connection pool ────────────────────────────────────────
POOL_CONNECTIONS = 50
POOL_MAX_SIZE = 100

# ── Cache ──────────────────────────────────────────────────
CACHE_DD_TTL = 300        # DataDome cookie cache (seconds)
CACHE_COOKIE_TTL = 600    # Cookie cache (seconds)
