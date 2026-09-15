#!/usr/bin/env python3
"""
🚀 COSMIC PROXY SCRAPER v3.0 — ACCURATE EDITION
Multi-source, multi-test, retry, and real stats.
"""
import os, sys, re, time, threading, requests, random, hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import defaultdict

# ── Auto-install ──────────────────────────────────────────
for mod, pkg in [("rich", "rich"), ("requests", "requests")]:
    try:
        __import__(mod)
    except ImportError:
        os.system(f"{sys.executable} -m pip install -q {pkg}")

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

# ═══════════════════════════════════════════════════════════════
#  25+ SOURCES — Multi-protocol, multi-region
# ═══════════════════════════════════════════════════════════════
SOURCES = {
    # GitHub repos (high quality)
    "SpeedX-HTTP":     "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "SpeedX-SOCKS4":   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "SpeedX-SOCKS5":   "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "Monosans-HTTP":   "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "Monosans-SOCKS5": "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "ShiftyTR-HTTP":   "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "ShiftyTR-HTTPS":  "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "Clarketm":        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "MMPX-HTTP":       "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "MMPX-SOCKS5":     "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
    "Roslov":          "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "Hookzof":         "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "Anonym0us":       "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
    "Proxifly-All":    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "Proxifly-HTTP":   "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    "Proxifly-SOCKS5": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    "OpenProxy":       "https://openproxylist.xyz/http.txt",
    "OpenProxy-S5":    "https://openproxylist.xyz/socks5.txt",
    "Kuaidaili":       "https://raw.githubusercontent.com/kuaidaili/free-ip-proxy/master/proxies.txt",
    "Zhiliang":        "https://raw.githubusercontent.com/zhiliang-daili/free-proxies/main/http.txt",

    # APIs
    "ProxyScrape-HTTP": "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=http",
    "ProxyScrape-S5":   "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks5",
    "ProxyScrape-S4":   "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&protocol=socks4",
    "GeoNode-HTTP":     "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
    "GeoNode-SOCKS5":   "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
}

OUTPUT_DIR = Path("proxies_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Test URLs (rotate for reliability) ─────────────────────
TEST_URLS = [
    ("http://httpbin.org/ip", "json:origin"),
    ("https://api.ipify.org?format=json", "json:ip"),
    ("http://ip-api.com/json/?fields=query", "json:query"),
    ("https://icanhazip.com", "text"),
]

TEST_TIMEOUT = 5
PROXY_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b')
IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.scraped = 0
        self.valid = 0
        self.failed = 0
        self.sources_ok = 0
        self.sources_fail = 0
        self.total_sources = len(SOURCES)
        self.start_time = time.time()
        self.live_feed = []
        self.last_proxy = ""
        self.last_latency = 0.0
        self.ip = ""
        self.server_online = self._check_server()
        self.session = hashlib.md5(f"{time.time()}{random.random()}".encode()).hexdigest()[:12].upper()

    def _check_server(self):
        for url, _ in TEST_URLS:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    return True
            except Exception:
                continue
        return False

    def log(self, msg, color="white"):
        with self.lock:
            ts = datetime.now().strftime("%H:%M:%S")
            self.live_feed.append(f"[dim]{ts}[/dim] [{color}]{msg}[/{color}]")
            if len(self.live_feed) > 40:
                self.live_feed.pop(0)


state = State()


# ═══════════════════════════════════════════════════════════════
#  SCRAPER
# ═══════════════════════════════════════════════════════════════
def scrape_source(name, url, q):
    state.log(f"Scraping {name}...", "cyan")
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = r.text

        # JSON handling (GeoNode)
        if "geonode" in url.lower():
            try:
                data = r.json()
                proxies = []
                for item in data.get("data", []):
                    ip = item.get("ip")
                    port = item.get("port")
                    if ip and port:
                        proxies.append(f"{ip}:{port}")
                text = "\n".join(proxies)
            except Exception:
                pass

        found = PROXY_RE.findall(text)
        for p in found:
            q.put(p)
        state.log(f"✓ {name}: {len(found)}", "green")
        with state.lock:
            state.sources_ok += 1
    except Exception as e:
        state.log(f"✗ {name}: {type(e).__name__}", "red")
        with state.lock:
            state.sources_fail += 1


# ═══════════════════════════════════════════════════════════════
#  VALIDATOR — Multi-URL, retry, real latency
# ═══════════════════════════════════════════════════════════════
def _test_one(url, format_hint, proxy):
    try:
        t0 = time.time()
        r = requests.get(
            url,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=TEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        latency = (time.time() - t0) * 1000
        if r.status_code != 200:
            return None

        if format_hint.startswith("json:"):
            key = format_hint.split(":", 1)[1]
            try:
                data = r.json()
                ip = str(data.get(key, "")).split(",")[0].strip()
                return (ip, latency)
            except Exception:
                m = IP_RE.search(r.text)
                return (m.group(0) if m else "", latency)
        else:
            m = IP_RE.search(r.text.strip())
            return (m.group(0) if m else "", latency)
    except Exception:
        return None


def validate_proxy(proxy):
    """Try multiple URLs — succeed if ANY works."""
    for url, hint in TEST_URLS:
        result = _test_one(url, hint, proxy)
        if result:
            ip, lat = result
            with state.lock:
                state.valid += 1
                state.last_proxy = proxy
                state.last_latency = lat
                state.ip = ip
            return (proxy, lat, ip)
    with state.lock:
        state.failed += 1
    return None


# ═══════════════════════════════════════════════════════════════
#  UI — 2-Grid
# ═══════════════════════════════════════════════════════════════
def render():
    elapsed = time.time() - state.start_time
    mins, secs = divmod(int(elapsed), 60)

    # Left: System Status
    sys_tbl = Table(show_header=False, box=None, padding=(0, 1))
    sys_tbl.add_column(style="dim", width=14)
    sys_tbl.add_column(style="bright_white")
    sys_tbl.add_row("Server:", "[green]ONLINE[/green]" if state.server_online else "[red]OFFLINE[/red]")
    sys_tbl.add_row("Test URLs:", f"[cyan]{len(TEST_URLS)}[/cyan]")
    sys_tbl.add_row("Session:", f"[yellow]{state.session}[/yellow]")
    sys_tbl.add_row("Uptime:", f"[bright_white]{mins:02d}:{secs:02d}[/bright_white]")
    sys_panel = Panel(sys_tbl, title="[bold cyan]⚙ SYSTEM[/bold cyan]",
                      border_style="cyan", box=box.ROUNDED)

    # Left: Scrape Stats
    total = state.valid + state.failed
    rate = (state.valid / total * 100) if total > 0 else 0.0
    stats_tbl = Table(show_header=False, box=None, padding=(0, 1))
    stats_tbl.add_column(style="dim", width=14)
    stats_tbl.add_column(style="bright_white")
    stats_tbl.add_row("Sources:", f"[bright_white]{state.sources_ok}/{state.total_sources}[/bright_white]"
                                 + (f" [red]({state.sources_fail}✗)[/red]" if state.sources_fail else ""))
    stats_tbl.add_row("Scraped:", f"[bright_yellow]{state.scraped:,}[/bright_yellow]")
    stats_tbl.add_row("Valid:", f"[bright_green]{state.valid:,}[/bright_green]")
    stats_tbl.add_row("Failed:", f"[bright_red]{state.failed:,}[/bright_red]")
    stats_tbl.add_row("Success:", f"[bold green]{rate:.1f}%[/bold green]")
    stats_tbl.add_row("Last Latency:", f"[cyan]{state.last_latency:.0f}ms[/cyan]" if state.last_latency else "[dim]—[/dim]")
    stats_panel = Panel(stats_tbl, title="[bold cyan]📊 STATS[/bold cyan]",
                        border_style="cyan", box=box.ROUNDED)

    # Left: Last Entry
    last = Text()
    if state.last_proxy:
        last.append(f"{state.last_proxy}", style="bright_white")
        if state.ip:
            last.append(f"\n→ {state.ip}", style="dim")
    else:
        last.append("Waiting...", style="dim")
    last_panel = Panel(last, title="[bold cyan]⚡ LAST PROXY[/bold cyan]",
                       border_style="cyan", box=box.ROUNDED)

    # Right: Live Feed
    feed = Text()
    for line in state.live_feed[-25:]:
        try:
            feed.append_text(Text.from_markup(line + "\n"))
        except Exception:
            feed.append(line + "\n", style="dim")
    if not feed.plain:
        feed.append("Waiting for events...", style="dim")
    feed_panel = Panel(feed, title="[bold cyan]📡 LIVE FEED[/bold cyan]",
                       border_style="cyan", box=box.ROUNDED)

    # Layout
    header = Panel(
        Align.center(Text("✦ PROXY SCRAPER · Cosmic v3.0 ✦", style="bold cyan")),
        border_style="cyan", box=box.HEAVY
    )
    footer = Panel(
        Align.center(Text("Ctrl+C to stop  ·  25+ sources  ·  4 test URLs",
                          style="dim")),
        border_style="cyan", box=box.HEAVY
    )

    left = Group(sys_panel, stats_panel, last_panel)
    body = Table.grid(expand=True, padding=(0, 1))
    body.add_column(ratio=1)
    body.add_column(ratio=2)
    body.add_row(left, feed_panel)

    return Group(header, body, footer)


# ═══════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ═══════════════════════════════════════════════════════════════
def run_proxy_scraper():
    global state
    state = State()

    state.log("Booting scrape core...", "cyan")
    state.log(f"Server: {'ONLINE' if state.server_online else 'OFFLINE'}",
              "green" if state.server_online else "red")
    state.log(f"Session: {state.session}", "yellow")

    import queue as _q
    q = _q.Queue()
    seen = set()

    state.log(f"Scraping {len(SOURCES)} sources...", "yellow")
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = [ex.submit(scrape_source, n, u, q) for n, u in SOURCES.items()]
        for _ in as_completed(futures):
            pass

    while not q.empty():
        p = q.get()
        if p not in seen:
            seen.add(p)

    state.scraped = len(seen)
    state.log(f"Total unique: {state.scraped:,}", "green")

    if not seen:
        console.print("[red]❌ No proxies scraped! Check internet.[/red]")
        input("Press Enter...")
        return

    proxies = list(seen)
    random.shuffle(proxies)
    state.log(f"Validating {len(proxies):,}...", "yellow")

    results = []
    stop_event = threading.Event()

    with Live(render(), console=console, refresh_per_second=4, screen=True) as live:
        def _update():
            while not stop_event.is_set():
                live.update(render())
                time.sleep(0.25)

        t = threading.Thread(target=_update, daemon=True)
        t.start()

        with ThreadPoolExecutor(max_workers=250) as ex:
            futures = {ex.submit(validate_proxy, p): p for p in proxies}
            for f in as_completed(futures):
                r = f.result()
                if r:
                    results.append(r)

        stop_event.set()
        t.join(timeout=1)

    state.log(f"Done — {len(results):,} valid", "green")

    # ── Save with 3 tiers ─────────────────────────────────
    if results:
        results.sort(key=lambda x: x[1])
        all_path = OUTPUT_DIR / "working_proxies.txt"
        fast_path = OUTPUT_DIR / "fast_proxies.txt"
        ultra_path = OUTPUT_DIR / "ultra_fast_proxies.txt"

        with open(all_path, "w") as f:
            for p, lat, ip in results:
                f.write(f"{p}\n")
        with open(fast_path, "w") as f:
            for p, lat, ip in results:
                if lat < 2000:
                    f.write(f"{p}\n")
        with open(ultra_path, "w") as f:
            for p, lat, ip in results:
                if lat < 1000:
                    f.write(f"{p}\n")

        console.print()
        console.print(Panel(
            Group(
                Text(f"✅ {len(results):,} working proxies saved", style="bold green"),
                Text(f"📁 {all_path}", style="cyan"),
                Text(f"⚡ {fast_path}  (<2s: {sum(1 for _,l,_ in results if l<2000):,})", style="cyan"),
                Text(f"🚀 {ultra_path}  (<1s: {sum(1 for _,l,_ in results if l<1000):,})", style="cyan"),
                Text(f"💾 Scraped: {state.scraped:,}  ·  Success: {len(results)/state.scraped*100:.1f}%", style="dim"),
            ),
            title="[bold cyan]RESULTS[/bold cyan]",
            border_style="green", box=box.DOUBLE,
        ))
        console.print()

        # Top 10 table
        top = Table(title="🏆 Top 10 Fastest", box=box.ROUNDED, border_style="cyan")
        top.add_column("#", style="dim", width=4)
        top.add_column("Proxy", style="bright_white")
        top.add_column("Latency", style="green", justify="right")
        top.add_column("Exit IP", style="cyan")
        for i, (p, lat, ip) in enumerate(results[:10], 1):
            top.add_row(str(i), p, f"{lat:.0f}ms", ip or "—")
        console.print(top)
    else:
        console.print("[red]❌ No working proxies found[/red]")

    input("\nPress Enter to return to menu...")
