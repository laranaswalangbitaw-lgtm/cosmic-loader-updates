#!/usr/bin/env python3
"""COSMIC DECODER + ENCODER v4.0"""
import base64, codecs, gzip, io, marshal, os, re, shutil, string, sys, time, zlib
from datetime import datetime
from urllib.parse import unquote, quote
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_FOLDER = SCRIPT_DIR / "decoder_input"
RESULTS_FOLDER = SCRIPT_DIR / "decoder_results"

RESET="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"
DARK_RED="\033[31m"; BRIGHT_RED="\033[91m"; DIM_RED="\033[2;31m"
WHITE_BOLD="\033[1;97m"; BOLD_RED="\033[1;31m"

def dr(t): return f"{BOLD}{DARK_RED}{t}{RESET}"
def br(t): return f"{BOLD}{BRIGHT_RED}{t}{RESET}"
def wb(t): return f"{WHITE_BOLD}{t}{RESET}"
def bd(t): return f"{BOLD}{t}{RESET}"
def dimr(t): return f"{DIM_RED}{t}{RESET}"
def bdr(t): return f"{BOLD_RED}{t}{RESET}"

def get_width(): return shutil.get_terminal_size(fallback=(80, 24)).columns

def center(text, width=None):
    if width is None: width = get_width()
    visible = re.sub("\033\\[[0-9;]*m", "", text)
    return " " * max(0, (width - len(visible)) // 2) + text

def cprint(text, end="\n"): print(center(text), end=end)

def sep_line(char="-", width=None, color_fn=dr):
    if width is None: width = get_width()
    return color_fn(char * width)

def print_sep(char="-", color_fn=dr): print(sep_line(char, color_fn=color_fn))

SPINNER = ["|", "/", "-", "\\"]

def spin(label="Processing", duration=1.0):
    w = get_width(); end = time.time() + duration; i = 0
    while time.time() < end:
        f = SPINNER[i % len(SPINNER)]
        sys.stdout.write(f"\r  {BOLD}{BRIGHT_RED}{f}{RESET}  {BOLD}{DARK_RED}{label}{RESET}  ")
        sys.stdout.flush(); time.sleep(0.08); i += 1
    sys.stdout.write("\r" + " " * w + "\r"); sys.stdout.flush()

def pause():
    try: input(dimr("\n  Press Enter to continue..."))
    except (EOFError, KeyboardInterrupt): pass

BANNER = [
    "  ####  ###  ####  #   #  ###  #### ",
    " #     #   # #     ## ## #   # #   #",
    " #     #   #  ###  # # # #   # #   #",
    " #     #   #     # #  ## #   # #   #",
    "  ####  ###  ####  #   #  ###  #### ",
    "",
    "+=================================+",
    "|  DECODER + ENCODER v4.0         |",
    "|  Powered by COSMIC              |",
    "+=================================+",
]

def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    w = get_width(); print()
    for i, line in enumerate(BANNER):
        if not line: print(); continue
        pad = max(0, (w - len(line)) // 2)
        color = BRIGHT_RED if i < 5 else DARK_RED
        print(f"{' ' * pad}{BOLD}{color}{line}{RESET}")
    print(); print_sep("="); print()

def ensure_folders():
    for f in [INPUT_FOLDER, RESULTS_FOLDER]:
        f.mkdir(parents=True, exist_ok=True)

def safe_decode_bytes(b):
    for enc in ("utf-8","latin-1","ascii","utf-16"):
        try: return b.decode(enc)
        except Exception: pass
    return b.decode("latin-1", errors="replace")

def is_mostly_printable(text, threshold=0.8):
    if not text: return False
    return sum(1 for c in text if c in string.printable) / len(text) >= threshold

def truncate(text, limit=800):
    if len(text) <= limit: return text
    h = limit // 2
    return text[:h] + f"\n{dimr('... [truncated] ...')}\n" + text[-h:]

def print_step(n, desc, content, ok=True):
    icon = wb("[OK]") if ok else br("[X]")
    print(f"\n  {icon}  {bd(f'Layer {n}:')}  {bdr(desc)}")
    print_sep("-", color_fn=dimr); print(truncate(content)); print_sep("-", color_fn=dimr)


class PythonDecoder:
    @staticmethod
    def b64(code):
        out = []
        for m in re.finditer(r"b64decode\s*\(\s*[b]?['\"]([\w+/=\s]+)['\"]", code, re.I):
            raw = m.group(1).replace("\n","").replace(" ","")
            try: out.append(safe_decode_bytes(base64.b64decode(raw + "==")))
            except Exception: pass
        s = code.strip().replace("\n","").replace(" ","")
        if re.fullmatch(r"[A-Za-z0-9+/=]+", s) and len(s) >= 16:
            try:
                t = safe_decode_bytes(base64.b64decode(s + "=="))
                if is_mostly_printable(t): out.append(t)
            except Exception: pass
        return out

    @staticmethod
    def hex_(code):
        out = []
        r = re.sub(r"\\x([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1),16)), code)
        if r != code: out.append(r)
        for m in re.finditer(r"['\"]([0-9A-Fa-f]{6,})['\"]", code):
            h = m.group(1)
            if len(h) % 2 == 0:
                try:
                    t = safe_decode_bytes(bytes.fromhex(h))
                    if is_mostly_printable(t): out.append(t)
                except Exception: pass
        return out

    @staticmethod
    def compressed(code):
        out = []
        s = code.strip().replace("\n","").replace(" ","")
        if re.fullmatch(r"[A-Za-z0-9+/=]+", s) and len(s) >= 16:
            try:
                blob = base64.b64decode(s + "==")
                for fn, name in ((zlib.decompress,"zlib"),(gzip.decompress,"gzip")):
                    try:
                        t = safe_decode_bytes(fn(blob))
                        if is_mostly_printable(t): out.append((name,t))
                    except Exception: pass
            except Exception: pass
        return out

    @staticmethod
    def rot13(code): return [("ROT13", codecs.decode(code,"rot_13"))]

    @staticmethod
    def unicode_esc(code):
        out = []
        try:
            d = code.encode("raw_unicode_escape").decode("unicode_escape")
            if d != code: out.append(d)
        except Exception: pass
        return out

    @staticmethod
    def reversed_str(code):
        out = []
        for m in re.finditer(r"['\"]((?:[^'\"\\]|\\.){4,})['\"]\s*\[\s*::\s*-\s*1\s*\]", code):
            out.append(m.group(1)[::-1])
        return out

    @staticmethod
    def chr_seq(code):
        r = re.sub(r"\bchr\s*\(\s*(\d+)\s*\)", lambda m: chr(int(m.group(1))), code)
        return [r] if r != code else []

    @staticmethod
    def url_decode(code):
        out = []
        if re.search(r"%[0-9A-Fa-f]{2}", code):
            try:
                d = unquote(code)
                if d != code: out.append(d)
            except Exception: pass
        return out

    @staticmethod
    def decimal_array(code):
        out = []
        for m in re.finditer(r"\[(\s*\d+(?:\s*,\s*\d+){3,}\s*)\]", code):
            try:
                nums = [int(x.strip()) for x in m.group(1).split(",")]
                if all(0 <= n <= 127 for n in nums):
                    t = "".join(chr(n) for n in nums)
                    if is_mostly_printable(t): out.append(t)
            except Exception: pass
        return out

    @staticmethod
    def base32(code):
        out = []
        for m in re.finditer(r"b32decode\s*\(\s*[b]?['\"]([\w=]+)['\"]", code, re.I):
            try:
                d = base64.b32decode(m.group(1).strip(), casefold=True)
                t = safe_decode_bytes(d)
                if is_mostly_printable(t): out.append(t)
            except Exception: pass
        return out

    @staticmethod
    def base85(code):
        out = []
        for m in re.finditer(r"b85decode\s*\(\s*[b]?['\"]([\x21-\x7e\s]+)['\"]", code, re.I):
            try:
                d = base64.b85decode(m.group(1).strip().encode())
                t = safe_decode_bytes(d)
                if is_mostly_printable(t): out.append(t)
            except Exception: pass
        return out

    @classmethod
    def multilayer(cls, code, max_depth=8):
        hist = []; cur = code
        for depth in range(1, max_depth + 1):
            found = False
            for name, fn in (("Base64",cls.b64),("Hex",cls.hex_),("Compressed",cls.compressed),
                            ("Unicode",cls.unicode_esc),("Reversed",cls.reversed_str),
                            ("chr()",cls.chr_seq),("URL",cls.url_decode),
                            ("Decimal",cls.decimal_array),("Base32",cls.base32),
                            ("Base85",cls.base85)):
                cands = fn(cur)
                if cands:
                    for c in cands:
                        if isinstance(c, tuple): text, label = c[1], f"{name} [{c[0]}]"
                        else: text, label = c, name
                        if text and text != cur and is_mostly_printable(text):
                            hist.append((depth, label, text)); cur = text; found = True; break
                    if found: break
            if not found: break
        return hist


class LuaDecoder:
    @staticmethod
    def b64(code):
        out = []
        for m in re.finditer(r"(?:loadstring|load)\s*\(\s*(?:\w+\.)?(?:b64decode|decode)\s*\(\s*['\"]([\w+/=\n\s]+)['\"]", code, re.I):
            try: out.append(safe_decode_bytes(base64.b64decode(m.group(1).replace("\n","") + "==")))
            except Exception: pass
        return out

    @staticmethod
    def hex_(code):
        r = re.sub(r"\\x([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1),16)), code)
        return [r] if r != code else []

    @staticmethod
    def string_char(code):
        out = []
        for m in re.finditer(r"string\.char\s*\(\s*([\d\s,]+)\s*\)", code, re.I):
            try:
                nums = [int(x.strip()) for x in m.group(1).split(",") if x.strip()]
                out.append("".join(chr(n) for n in nums if 0 <= n <= 0x10FFFF))
            except Exception: pass
        return out

    @staticmethod
    def reversed_str(code):
        out = []
        for m in re.finditer(r"string\.reverse\s*\(\s*['\"](.*?)['\"]\s*\)", code):
            out.append(m.group(1)[::-1])
        return out

    @staticmethod
    def peel(code):
        out = []
        for m in re.finditer(r"(?:loadstring|load)\s*\(\s*['\"]([\s\S]+?)['\"]\s*\)", code, re.I):
            out.append(m.group(1))
        return out

    @staticmethod
    def xor_single(code):
        out = []
        for m in re.finditer(r"['\"]([0-9A-Fa-f]{8,})['\"]", code):
            h = m.group(1)
            if len(h) % 2 == 0:
                data = bytes.fromhex(h)
                for k in range(1, 256):
                    t = safe_decode_bytes(bytes(b ^ k for b in data))
                    if is_mostly_printable(t):
                        out.append((f"XOR 0x{k:02X}", t))
                        if len(out) >= 5: break
        return out

    @classmethod
    def multilayer(cls, code, max_depth=8):
        hist = []; cur = code
        for depth in range(1, max_depth + 1):
            found = False
            for name, fn in (("Base64",cls.b64),("Hex",cls.hex_),("string.char()",cls.string_char),
                            ("Reversed",cls.reversed_str),("loadstring peel",cls.peel),
                            ("XOR single",cls.xor_single)):
                cands = fn(cur)
                if cands:
                    for c in cands:
                        if isinstance(c, tuple): text, label = c[1], f"{name} [{c[0]}]"
                        else: text, label = c, name
                        if text and text != cur and is_mostly_printable(text):
                            hist.append((depth, label, text)); cur = text; found = True; break
                    if found: break
            if not found: break
        return hist


class Encoder:
    @staticmethod
    def base64(code): return base64.b64encode(code.encode()).decode()
    @staticmethod
    def hex_(code): return code.encode().hex()
    @staticmethod
    def rot13(code): return codecs.encode(code, "rot_13")
    @staticmethod
    def reverse(code): return code[::-1]
    @staticmethod
    def marshal(code):
        try:
            compiled = compile(code, "<string>", "exec")
            return base64.b64encode(marshal.dumps(compiled)).decode()
        except Exception as e: return f"[marshal error: {e}]"
    @staticmethod
    def url(code): return quote(code, safe="")
    @staticmethod
    def chr_chain(code): return "+".join(f"chr({ord(c)})" for c in code)
    @staticmethod
    def base32(code): return base64.b32encode(code.encode()).decode()
    @staticmethod
    def base85(code): return base64.b85encode(code.encode()).decode()


PY_SIGNALS = [r"\bexec\s*\(", r"\beval\s*\(", r"base64|b64decode", r"\\x[0-9A-Fa-f]{2}",
              r"zlib\.decompress", r"marshal\.loads", r"\bchr\s*\(\d+\)", r"__import__"]
LUA_SIGNALS = [r"\bloadstring\s*\(", r"\bload\s*\(", r"string\.char\s*\(",
               r"string\.reverse\s*\(", r":reverse\(\)", r"\bxor\b"]

def detect_lang(code, ext=""):
    ext = ext.lower()
    if ext == ".py": return "python"
    if ext == ".lua": return "lua"
    ps = sum(1 for p in PY_SIGNALS if re.search(p, code, re.I))
    ls = sum(1 for p in LUA_SIGNALS if re.search(p, code, re.I))
    return "lua" if ls > ps else "python"

def _paste_code():
    print(dimr("  (Press Enter twice to finish)\n"))
    lines = []; blanks = 0
    while True:
        try: line = input()
        except EOFError: break
        if line == "":
            blanks += 1
            if blanks >= 2 and lines: break
        else: blanks = 0
        lines.append(line)
    return "\n".join(lines)

def run_decoder_mode():
    ensure_folders()
    print_banner()
    print(f"  {bd('Input:')}  {wb(str(INPUT_FOLDER))}")
    print(f"  {bd('Results:')} {wb(str(RESULTS_FOLDER))}")
    print(); print_sep("-", color_fn=dimr)

    files = [f for f in INPUT_FOLDER.iterdir() if f.is_file() and not f.name.startswith(".")]
    if not files:
        print(br("\n  No files in decoder_input/"))
        print(dimr("  Drop your .py / .lua / .txt files there."))
        pause(); return

    print(f"\n  {bd('Found')} {wb(str(len(files)))} {bd('file(s):')}\n")
    for i, f in enumerate(files, 1):
        size = f.stat().st_size
        size_str = f"{size:,} B" if size < 1024 else f"{size/1024:.1f} KB"
        tag = bdr("[PY] ") if f.suffix == ".py" else br("[LUA]") if f.suffix == ".lua" else dr("[TXT]")
        print(f"  {BOLD}{DARK_RED}{i:>3}){RESET}  {tag}  {wb(f.name):<40} {dimr(size_str)}")
    print(f"\n  {dimr('p')}  Paste code")
    print(f"  {dimr('b')}  Back")
    print_sep("-", color_fn=dimr)

    raw = input(f"  {BOLD}{DARK_RED}Pick:{RESET} ").strip().lower()
    if raw in ("b","back",""): return
    if raw == "p":
        code = _paste_code(); source_name = "pasted_input"
    else:
        try:
            idx = int(raw) - 1
            if not (0 <= idx < len(files)): return
            f = files[idx]; source_name = f.name
            spin(f"Reading {f.name}", 0.5)
            code = f.read_text(encoding="utf-8", errors="replace")
        except (ValueError, Exception) as e:
            print(br(f"  Error: {e}")); pause(); return

    if not code or not code.strip():
        print(br("  Empty code.")); pause(); return

    lang = detect_lang(code, Path(source_name).suffix)
    print(f"\n  {bd('Detected:')} {bdr(lang.upper())}")
    override = input(f"  {dimr('Override? [Enter=keep/py/lua]:')} ").strip().lower()
    if override in ("py","python"): lang = "python"
    elif override in ("lua","l"): lang = "lua"

    print(); spin(f"Decoding {lang}...", 0.8)
    layers = (LuaDecoder if lang == "lua" else PythonDecoder).multilayer(code)

    if not layers:
        print(br("\n  No decodable layers found."))
    else:
        print(wb(f"\n  Decoded {len(layers)} layer(s)!\n"))
        for d, m, t in layers:
            print_step(d, m, t)
        save = input(f"\n  {BOLD}{DARK_RED}Save? [Y/n]:{RESET} ").strip().lower()
        if save != "n":
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = RESULTS_FOLDER / f"decoded_{Path(source_name).stem}_{ts}.txt"
            with open(out, "w", encoding="utf-8") as f:
                f.write(f"COSMIC DECODER v4.0\nSource: {source_name}\nLayers: {len(layers)}\n")
                f.write("=" * 60 + "\n\n")
                for i, (d, m, t) in enumerate(layers, 1):
                    f.write(f"[Layer {i} | depth={d} | {m}]\n{t}\n\n")
                f.write("FINAL:\n" + layers[-1][2] + "\n")
            print(wb(f"  Saved -> {out}"))
    pause()


def run_encoder_mode():
    print_banner()
    print(f"  {bd('ENCODER MODE')}\n")
    for num, name in [("1","Base64"),("2","Hex"),("3","ROT13"),("4","Reverse"),
                      ("5","Marshal"),("6","URL"),("7","chr() Chain"),
                      ("8","Base32"),("9","Base85")]:
        print(f"  {BOLD}{DARK_RED}[{num}]{RESET} {name}")
    print(f"  {BOLD}{DARK_RED}[b]{RESET} Back")
    print_sep("-", color_fn=dimr)

    choice = input(f"  {BOLD}{DARK_RED}Pick:{RESET} ").strip().lower()
    if choice == "b": return

    print(f"\n  {bd('Paste code:')}")
    code = _paste_code()
    if not code:
        print(br("  No input.")); pause(); return

    encoders = {"1":("Base64",Encoder.base64),"2":("Hex",Encoder.hex_),
                "3":("ROT13",Encoder.rot13),"4":("Reverse",Encoder.reverse),
                "5":("Marshal",Encoder.marshal),"6":("URL",Encoder.url),
                "7":("chr()",Encoder.chr_chain),"8":("Base32",Encoder.base32),
                "9":("Base85",Encoder.base85)}
    if choice not in encoders:
        print(br("  Invalid.")); pause(); return

    name, fn = encoders[choice]
    spin(f"Encoding {name}", 0.5)
    result = fn(code)
    print(f"\n  {wb('=== ENCODED ===')}\n"); print(result); print()
    save = input(f"  {BOLD}{DARK_RED}Save? [Y/n]:{RESET} ").strip().lower()
    if save != "n":
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = RESULTS_FOLDER / f"encoded_{name.lower()}_{ts}.txt"
        out.write_text(result)
        print(wb(f"  Saved -> {out}"))
    pause()


def run_decoder_encoder_menu():
    """Entry point for loader."""
    while True:
        print_banner()
        print(f"  {bd('MODE')}\n")
        print(f"  {BOLD}{BRIGHT_RED}[1]{RESET} DECODER - decode obfuscated code")
        print(f"  {BOLD}{DARK_RED}[2]{RESET} ENCODER - encode your code")
        print(f"  {BOLD}{DARK_RED}[0]{RESET} Back")
        print_sep("-", color_fn=dimr)
        choice = input(f"  {BOLD}{DARK_RED}Pick:{RESET} ").strip()
        if choice == "1": run_decoder_mode()
        elif choice == "2": run_encoder_mode()
        elif choice == "0": return
