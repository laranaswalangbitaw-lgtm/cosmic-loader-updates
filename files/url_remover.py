#!/usr/bin/env python3
"""COSMIC URL REMOVER v3.0"""
import os, re, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_DIR = SCRIPT_DIR / "url_input"
OUTPUT_DIR = SCRIPT_DIR / "url_output"

RESET="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"; CYAN="\033[36m"
GREEN="\033[92m"; YELLOW="\033[93m"; RED="\033[91m"; BRIGHT_CYAN="\033[96m"

def get_width():
    import shutil
    return shutil.get_terminal_size(fallback=(80, 24)).columns

def sep(char="=", color=CYAN):
    print(f"{color}{BOLD}{char * min(get_width(), 68)}{RESET}")

def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    w = get_width()
    print(); sep("=")
    title = "COSMIC URL REMOVER + CRED EXTRACTOR v3.0"
    pad = max(0, (w - len(title)) // 2)
    print(f"{' ' * pad}{BOLD}{BRIGHT_CYAN}{title}{RESET}")
    sep("="); print()

EMAIL_CRED = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s:]+")
GENERIC_CRED = re.compile(r"[a-zA-Z0-9._\-]+:[^\s:]+")
URL_PREFIX = re.compile(r"^(?:https?://|ftp://|www\.)", re.I)

def extract(line):
    line = line.strip()
    if not line or ":" not in line: return None
    m = EMAIL_CRED.search(line)
    if m: return m.group(0).strip()
    cleaned = URL_PREFIX.sub("", line)
    cleaned = re.sub(r"^[^:/\s]+[:/]", "", cleaned, count=1) if "://" in line else cleaned
    m = GENERIC_CRED.search(cleaned)
    if m:
        cred = m.group(0).strip()
        if len(cred) >= 6 and cred.count(":") >= 1:
            parts = cred.split(":", 1)
            if len(parts[0]) >= 2 and len(parts[1]) >= 2:
                return cred
    return None

def process_file(input_path, output_path, dedup=True, validate_email=False, threads=8):
    try:
        raw = input_path.read_bytes()
        text = None
        for enc in ("utf-8", "latin-1", "cp1252"):
            try: text = raw.decode(enc); break
            except Exception: continue
        if text is None: text = raw.decode("latin-1", errors="replace")
    except Exception as e:
        print(f"{RED}  Cannot read {input_path.name}: {e}{RESET}")
        return None

    lines = text.splitlines()
    total = len(lines)
    print(f"  {CYAN}{input_path.name}  ({total:,} lines){RESET}")

    def process_chunk(chunk):
        out = []
        for line in chunk:
            cred = extract(line)
            if cred:
                if validate_email and not EMAIL_CRED.search(cred): continue
                out.append(cred)
        return out

    chunk_size = max(1000, total // (threads * 4))
    chunks = [lines[i:i+chunk_size] for i in range(0, total, chunk_size)]
    results = []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(process_chunk, c) for c in chunks]
        for f in as_completed(futures): results.extend(f.result())

    if dedup:
        seen = set(); unique = []
        for r in results:
            if r not in seen:
                seen.add(r); unique.append(r)
        results = unique

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n")
    return {"total": total, "extracted": len(results), "output": str(output_path)}


def run_url_remover():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        print_banner()
        print(f"  {BOLD}Input:{RESET}  {CYAN}{INPUT_DIR}{RESET}")
        print(f"  {BOLD}Output:{RESET} {CYAN}{OUTPUT_DIR}{RESET}")
        print(); sep("-", DIM)
        files = [f for f in INPUT_DIR.iterdir() if f.is_file() and not f.name.startswith(".")]
        if not files:
            print(f"{YELLOW}  No files in input folder.{RESET}")
            print(f"  {DIM}Drop .txt files into: {INPUT_DIR}{RESET}")
            print(); sep("-", DIM)
            input(f"  {DIM}Press Enter...{RESET}")
            return
        print(f"  {BOLD}Found {len(files)} file(s):{RESET}\n")
        for i, f in enumerate(files, 1):
            size = f.stat().st_size
            size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"  {BOLD}{CYAN}{i:>3}){RESET} {f.name:<40} {DIM}{size_str}{RESET}")
        print(); sep("-", DIM)
        print(f"  {DIM}[a] Process ALL{RESET}")
        print(f"  {DIM}[b] Back{RESET}")
        sep("-", DIM)
        raw = input(f"\n  {BOLD}{CYAN}Pick:{RESET} ").strip().lower()
        if raw in ("b", "back", ""): return
        if raw == "a": targets = files
        else:
            try:
                idx = int(raw) - 1
                if not (0 <= idx < len(files)): continue
                targets = [files[idx]]
            except ValueError: continue
        print()
        dedup = input(f"  {CYAN}Remove duplicates? [Y/n]:{RESET} ").strip().lower() != "n"
        validate = input(f"  {CYAN}Only email:pass? [y/N]:{RESET} ").strip().lower() == "y"
        print(); sep("-", DIM)
        total_ok = 0; start = time.time()
        for f in targets:
            out = OUTPUT_DIR / f"{f.stem}_cleaned.txt"
            print(f"\n  {BOLD}{CYAN}Processing {f.name}...{RESET}")
            res = process_file(f, out, dedup=dedup, validate_email=validate)
            if res:
                total_ok += res["extracted"]
                rate = res["extracted"] / max(res["total"], 1) * 100
                print(f"  {GREEN}Extracted {res['extracted']:,} creds ({rate:.2f}%){RESET}")
                print(f"  {DIM}-> {out}{RESET}")
        elapsed = time.time() - start
        print(); sep("=", GREEN)
        print(f"  {GREEN}{BOLD}DONE - {total_ok:,} creds in {elapsed:.1f}s{RESET}")
        print(f"  {DIM}Output: {OUTPUT_DIR}{RESET}")
        sep("=", GREEN); print()
        input(f"  {DIM}Press Enter...{RESET}")
