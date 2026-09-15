#!/usr/bin/env python3
"""
⚡ COSMIC SEPARATOR v5.0 — ACCURATE EDITION
Splits combo by keyword with high precision, dedup, and live dashboard.
"""
import os, re, mmap, sys, time, threading
from multiprocessing import Process, cpu_count, Manager
from collections import defaultdict
from pathlib import Path

# ── Auto-install ──────────────────────────────────────────
for mod, pkg in [("rich", "rich")]:
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
#  CONFIG
# ═══════════════════════════════════════════════════════════════
OUTPUT_FOLDER = "ALL_LISTED_TXT"
CHUNK_SIZE = 50 * 1024 * 1024
BATCH_SIZE = 10_000_000
DEDUP = True   # ← ON for accuracy (removes duplicates per keyword)

# ── 100+ Keywords — expanded with more services ───────────
KEYWORDS = {
    # Garena / Mobile Legends
    "garena.com":                     "garena.txt",
    "sso.garena.com":                 "sso_garena.txt",
    "authgop":                        "authgop.txt",
    "mobilelegends.com":              "mobilelegends.txt",
    "authgop.garena.com/oauth/login": "elite_access.txt",
    "auth.garena.com/ui/login":       "paldo_entry.txt",
    "Freefire":                       "freefire.txt",

    # Streaming
    "Spotify":                        "spotify.txt",
    "SpotifyPremium":                 "spotifyPrem.txt",
    "Netflix":                        "netflix.txt",
    "Vivamax":                        "VIV.txt",
    "HBOMax":                         "hbomax.txt",
    "Crunchyroll":                    "crunchyroll.txt",
    "Disney+":                        "disney.txt",
    "Hulu":                           "hulu.txt",
    "YouTube":                        "youtube.txt",
    "SoundCloud":                     "soundcloud.txt",
    "Deezer":                         "deezer.txt",
    "Twitch":                         "twitch.txt",

    # Social
    "Facebook":                       "facebook.txt",
    "Instagram":                      "instagram.txt",
    "Twitter":                        "twitter.txt",
    "Discord":                        "discord.txt",
    "Snapchat":                       "snapchat.txt",
    "Tiktok":                         "tiktok.txt",
    "tiktok":                         "tiktok.txt",
    "LinkedIn":                       "linked.txt",
    "Telegram":                       "telegram.txt",
    "Signal":                         "signal.txt",
    "Reddit":                         "reddit.txt",
    "VK":                             "vk.txt",
    "WeChat":                         "wechat.txt",
    "WhatsApp":                       "whatsapp.txt",
    "Skype":                          "skype.txt",
    "Zoom":                           "zoom.txt",
    "Slack":                          "slack.txt",
    "Pinterest":                      "pinterest.txt",

    # Ecommerce
    "Shopee":                         "shopee.txt",
    "Lazada":                         "lazada.txt",
    "Amazon":                         "Amazon.txt",
    "Ebay":                           "ebay.txt",
    "AliExpress":                     "aliexpress.txt",
    "Temu":                           "temu.txt",
    "Codashop":                       "codashop.txt",

    # Payment
    "Paypal":                         "paypal.txt",
    "uber":                           "ubereats.txt",

    # Gaming
    "Valorant":                       "valorant.txt",
    "PUBG":                           "pubg.txt",
    "riotgames":                      "riotgames.txt",
    "miniclip":                       "8BALL.txt",
    "clashofclan":                    "clashofclan.txt",
    "Cyberpunk":                      "cyberpunk.txt",
    "Halo":                           "halo.txt",
    "LOL2":                           "LOL.txt",
    "Honkai":                         "honkai.txt",
    "FIFA":                           "fifa.txt",
    "Fortnite":                       "fortnite.txt",
    "Genshin":                        "genshin.txt",
    "Apex":                           "apex.txt",
    "Dota2":                          "dota2.txt",
    "Warzone":                        "warzone.txt",
    "Minecraft":                      "minecraft.txt",
    "Steam":                          "steam.txt",
    "EpicGames":                      "epicgames.txt",
    "playstatiom":                    "psn.txt",
    "Xbox":                           "xbox.txt",
    "brawlstar":                      "brawlstar.txt",
    "crossfire":                      "cf.txt",

    # Cloud / Tools
    "GoogleDrive":                    "googledrive.txt",
    "Dropbox":                        "dropbox.txt",
    "OneDrive":                       "onedrive.txt",
    "Github":                         "github.txt",

    # Email
    "Email":                          "gmail.txt",
    "Hotmail":                        "hotmail.txt",
    "Yahoo":                          "yahoo.txt",

    # Misc
    "bili-bili":                      "bilibili.txt",
    "OnlyFans":                       "onlyfans.txt",
    "express":                        "VPN.txt",
    "Pub":                            "p.txt",
}

# ── Compile patterns (case-insensitive) ───────────────────
# Sort keywords by length DESC so longer matches win (prevents "Pub" matching inside "PUBG")
SORTED_KW = sorted(KEYWORDS.keys(), key=len, reverse=True)
PATTERN = re.compile("|".join(re.escape(k) for k in SORTED_KW), re.IGNORECASE)

# ── Line cleanup patterns ─────────────────────────────────
# Extract "user:pass" from lines like:
#   https://garena.com:user@example.com:password
#   https://garena.com\|user@example.com:password
#   user@example.com:password
CLEAN_PATTERNS = [
    re.compile(rb'^[^:]+://[^:]+[:|]'),       # strip URL prefix
    re.compile(rb'^[^:]+[:|](?=[^:]+:[^:]+$)'), # strip domain prefix
]
COMBO_RE = re.compile(rb'[\w\.\-\+]+@?[\w\.\-]*:[\S]+')


# ═══════════════════════════════════════════════════════════════
#  WORKER
# ═══════════════════════════════════════════════════════════════
def _init_files(worker_id):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    return {
        key: open(os.path.join(OUTPUT_FOLDER, f"w{worker_id}_{fname}"), "ab", buffering=65536)
        for key, fname in KEYWORDS.items()
    }


def _clean_line(line_bytes):
    """Extract clean user:pass from a raw line."""
    line = line_bytes.strip()
    for pat in CLEAN_PATTERNS:
        line = pat.sub(b'', line)
    # Must have at least one colon
    if b':' not in line:
        return None
    return line.strip()


def _flush(buffer, outputs):
    for key, lines in buffer.items():
        if lines:
            outputs[key].write(b"\n".join(lines) + b"\n")
    buffer.clear()


def _worker(file, start, end, wid, shared_stats):
    outputs = _init_files(wid)
    buffer = defaultdict(list)
    seen = defaultdict(set)
    total_lines = 0
    matched = 0

    with open(file, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        mm.seek(start)

        while mm.tell() < end:
            line = mm.readline()
            if not line:
                break
            total_lines += 1

            # Search keyword
            match = PATTERN.search(line.decode(errors="ignore"))
            if not match:
                continue

            key = match.group(0)
            clean_line = _clean_line(line)
            if not clean_line:
                continue

            matched += 1

            if DEDUP:
                if clean_line in seen[key]:
                    continue
                seen[key].add(clean_line)

            buffer[key].append(clean_line)

            if sum(len(v) for v in buffer.values()) >= BATCH_SIZE:
                _flush(buffer, outputs)

        mm.close()

    _flush(buffer, outputs)

    for f in outputs.values():
        f.close()

    # Update shared stats
    with shared_stats['lock']:
        shared_stats['total'] += total_lines
        shared_stats['matched'] += matched
        for key, lines in seen.items():
            shared_stats['by_key'][key] = shared_stats['by_key'].get(key, 0) + len(lines)


# ═══════════════════════════════════════════════════════════════
#  SPLIT + MERGE
# ═══════════════════════════════════════════════════════════════
def _split_file(file):
    size = os.path.getsize(file)
    chunks = []
    with open(file, "rb") as f:
        start = 0
        while start < size:
            end = start + CHUNK_SIZE
            if end >= size:
                chunks.append((start, size))
                break
            f.seek(end)
            f.readline()
            end = f.tell()
            chunks.append((start, end))
            start = end
    return chunks


def _merge_outputs():
    """Merge worker outputs into final files, with dedup."""
    merged_files = 0
    for key, fname in KEYWORDS.items():
        final_path = os.path.join(OUTPUT_FOLDER, fname)
        worker_files = [f for f in os.listdir(OUTPUT_FOLDER)
                        if f.startswith("w") and f.endswith(fname)]
        if not worker_files:
            continue

        if DEDUP:
            # Cross-worker dedup
            seen = set()
            with open(final_path, "wb") as outfile:
                for wf in worker_files:
                    with open(os.path.join(OUTPUT_FOLDER, wf), "rb") as f:
                        for line in f:
                            line = line.strip()
                            if line and line not in seen:
                                seen.add(line)
                                outfile.write(line + b"\n")
                    os.remove(os.path.join(OUTPUT_FOLDER, wf))
        else:
            with open(final_path, "wb") as outfile:
                for wf in worker_files:
                    with open(os.path.join(OUTPUT_FOLDER, wf), "rb") as f:
                        outfile.write(f.read())
                    os.remove(os.path.join(OUTPUT_FOLDER, wf))

        merged_files += 1

    return merged_files


# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════
_state = {
    'start': 0.0,
    'total': 0,
    'matched': 0,
    'by_key': {},
    'log': [],
    'phase': 'idle',
    'running': False,
}


def _log(msg, color="white"):
    ts = time.strftime("%H:%M:%S")
    _state['log'].append(f"[dim]{ts}[/dim] [{color}]{msg}[/{color}]")
    if len(_state['log']) > 50:
        _state['log'].pop(0)


def _render():
    elapsed = time.time() - _state['start']
    mins, secs = divmod(int(elapsed), 60)
    rate = _state['total'] / elapsed if elapsed > 0 else 0

    # Left: Status
    status = Table(show_header=False, box=None, padding=(0, 1))
    status.add_column(style="dim", width=14)
    status.add_column(style="bright_white")
    status.add_row("Phase:", f"[yellow]{_state['phase']}[/yellow]")
    status.add_row("Workers:", f"[cyan]{cpu_count()}[/cyan]")
    status.add_row("Dedup:", "[green]ON[/green]" if DEDUP else "[red]OFF[/red]")
    status.add_row("Uptime:", f"[bright_white]{mins:02d}:{secs:02d}[/bright_white]")
    status_panel = Panel(status, title="[bold cyan]⚙ STATUS[/bold cyan]",
                         border_style="cyan", box=box.ROUNDED)

    # Left: Stats
    stats = Table(show_header=False, box=None, padding=(0, 1))
    stats.add_column(style="dim", width=14)
    stats.add_column(style="bright_white")
    stats.add_row("Total lines:", f"[bright_yellow]{_state['total']:,}[/bright_yellow]")
    stats.add_row("Matched:", f"[bright_green]{_state['matched']:,}[/bright_green]")
    stats.add_row("Speed:", f"[cyan]{rate:,.0f}/s[/cyan]")
    stats.add_row("Keywords:", f"[magenta]{len(KEYWORDS)}[/magenta]")
    stats_panel = Panel(stats, title="[bold cyan]📊 STATS[/bold cyan]",
                        border_style="cyan", box=box.ROUNDED)

    # Left: Top keywords
    kw = Table(show_header=False, box=None, padding=(0, 1))
    kw.add_column(style="dim", width=18)
    kw.add_column(style="bright_white", justify="right")
    top = sorted(_state['by_key'].items(), key=lambda x: -x[1])[:6]
    if not top:
        kw.add_row("[dim]Waiting...[/dim]", "[dim]—[/dim]")
    for k, v in top:
        kw.add_row(f"[cyan]{k[:16]}[/cyan]", f"[green]{v:,}[/green]")
    kw_panel = Panel(kw, title="[bold cyan]🔑 TOP KEYWORDS[/bold cyan]",
                     border_style="cyan", box=box.ROUNDED)

    # Right: Live feed
    feed = Text()
    for line in _state['log'][-25:]:
        try:
            feed.append_text(Text.from_markup(line + "\n"))
        except Exception:
            feed.append(line + "\n", style="dim")
    if not feed.plain:
        feed.append("Waiting for events...", style="dim")
    feed_panel = Panel(feed, title="[bold cyan]📡 LIVE FEED[/bold cyan]",
                       border_style="cyan", box=box.ROUNDED)

    header = Panel(
        Align.center(Text("✦ COSMIC SEPARATOR v5.0 ✦", style="bold cyan")),
        border_style="cyan", box=box.HEAVY
    )
    footer = Panel(
        Align.center(Text("Ctrl+C to stop  ·  Multi-core  ·  Accurate Edition", style="dim")),
        border_style="cyan", box=box.HEAVY
    )

    left = Group(status_panel, stats_panel, kw_panel)
    body = Table.grid(expand=True, padding=(0, 1))
    body.add_column(ratio=1)
    body.add_column(ratio=2)
    body.add_row(left, feed_panel)

    return Group(header, body, footer)


# ═══════════════════════════════════════════════════════════════
#  PUBLIC ENTRY
# ═══════════════════════════════════════════════════════════════
def run_separator():
    global _state
    console.clear()
    console.print(Panel(
        Align.center(Text("✦ COSMIC SEPARATOR v5.0 ✦", style="bold cyan")),
        border_style="cyan", box=box.DOUBLE, padding=(1, 2),
    ))
    console.print()

    file_path = input("  📂 Enter input file: ").strip().strip("'\"")
    if not file_path or not os.path.isfile(file_path):
        console.print(f"  [red]✖ File not found: {file_path}[/red]")
        input("  Press Enter to return...")
        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    console.print(f"  [green]✓[/green] File: [cyan]{os.path.basename(file_path)}[/cyan]  "
                  f"[dim]({size_mb:.1f} MB)[/dim]")
    console.print()

    chunks = _split_file(file_path)

    _state = {
        'start': time.time(),
        'total': 0,
        'matched': 0,
        'by_key': {},
        'log': [],
        'phase': 'scraping',
        'running': True,
    }

    _log(f"Loaded {os.path.basename(file_path)}", "cyan")
    _log(f"Split into {len(chunks)} chunk(s)", "yellow")
    _log(f"Spawning {cpu_count()} workers", "cyan")

    console.print(f"  [cyan]⚡ CPU cores:[/cyan] {cpu_count()}")
    console.print(f"  [cyan]📦 Chunks:[/cyan]    {len(chunks)}")
    console.print()

    # Shared stats via Manager
    manager = Manager()
    shared_stats = manager.dict()
    shared_stats['total'] = 0
    shared_stats['matched'] = 0
    shared_stats['by_key'] = manager.dict()
    shared_stats['lock'] = manager.Lock()

    processes = []
    for i, (start, end) in enumerate(chunks):
        p = Process(target=_worker, args=(file_path, start, end, i, shared_stats))
        p.start()
        processes.append(p)
        _log(f"Worker {i} → chunk {i+1}/{len(chunks)}", "cyan")

    # Live UI
    stop_flag = threading.Event()

    def _refresh():
        with Live(_render(), console=console, refresh_per_second=4, screen=True) as live:
            while not stop_flag.is_set():
                # Sync shared stats
                try:
                    _state['total'] = shared_stats['total']
                    _state['matched'] = shared_stats['matched']
                    _state['by_key'] = dict(shared_stats['by_key'])
                except Exception:
                    pass
                live.update(_render())
                time.sleep(0.25)

    t = threading.Thread(target=_refresh, daemon=True)
    t.start()

    for p in processes:
        p.join()

    _state['phase'] = 'merging'
    _log("Merging outputs...", "yellow")

    stop_flag.set()
    t.join(timeout=1)

    merged = _merge_outputs()

    _log(f"Merged {merged} files", "green")

    elapsed = time.time() - _state['start']
    console.print()
    console.print(Panel(
        Group(
            Text(f"✅ Separator complete!", style="bold green"),
            Text(f"📁 Output: {OUTPUT_FOLDER}/", style="cyan"),
            Text(f"⏱️  Time: {int(elapsed//60)}m {int(elapsed%60)}s", style="dim"),
            Text(f"📊 Lines: {_state['total']:,}  ·  Matched: {_state['matched']:,}", style="cyan"),
            Text(f"📦 Files: {merged}", style="cyan"),
        ),
        title="[bold cyan]RESULTS[/bold cyan]",
        border_style="green", box=box.DOUBLE,
    ))
    console.print()
    input("  Press Enter to return to menu...")
