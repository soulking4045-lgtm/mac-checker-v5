#!/usr/bin/env python3
"""MAC CHECKER v5.3 - BOT KEY SERVER | License Management & Permission System"""
import hashlib, hmac, json, os, re, secrets, sqlite3, sys, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
CONFIG_DIR = os.path.expanduser("~/.mac_checker_v5")
DB_PATH = os.path.join(CONFIG_DIR, "keys.db")
SECRET_FILE = os.path.join(CONFIG_DIR, ".secret")
LOG_FILE = os.path.join(CONFIG_DIR, "server.log")
DEFAULT_PORT = 8420
R,G,Y,C,N,B = '\033[0;31m','\033[0;32m','\033[1;33m','\033[0;36m','\033[0m','\033[1m'

def init_db():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS license_keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key_hash TEXT UNIQUE NOT NULL, key_prefix TEXT NOT NULL, created_by TEXT DEFAULT 'admin', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_active INTEGER DEFAULT 1, max_devices INTEGER DEFAULT 3, expires_at TIMESTAMP, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS permissions (id INTEGER PRIMARY KEY AUTOINCREMENT, key_hash TEXT NOT NULL, user_identifier TEXT NOT NULL, granted_by TEXT DEFAULT 'admin', granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_active INTEGER DEFAULT 1, device_limit INTEGER DEFAULT 1, expires_at TIMESTAMP, notes TEXT, FOREIGN KEY (key_hash) REFERENCES license_keys(key_hash))''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage_log (id INTEGER PRIMARY KEY AUTOINCREMENT, key_hash TEXT NOT NULL, user_identifier TEXT NOT NULL, action TEXT NOT NULL, device_id TEXT, ip_address TEXT, success INTEGER DEFAULT 0, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, details TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id TEXT UNIQUE NOT NULL, username TEXT, role TEXT DEFAULT 'admin', added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_active INTEGER DEFAULT 1)''')
    conn.commit(); conn.close()
    log_event("Database initialized")

def get_db(): return sqlite3.connect(DB_PATH)

def get_or_create_secret():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, 'rb') as f: return f.read()
    secret = secrets.token_bytes(32)
    with open(SECRET_FILE, 'wb') as f: f.write(secret)
    os.chmod(SECRET_FILE, 0o600); return secret

def generate_license_key(prefix="MC5"):
    secret = get_or_create_secret()
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(4).upper()
    payload = f"{prefix}:{timestamp}:{random_part}"
    signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()[:8].upper()
    return f"{prefix}-{random_part[:4]}-{random_part[4:8]}-{signature}"

def parse_duration(duration_str):
    """Parse time string like 1h30min, 2h, 45min, 1d. Returns seconds or -1."""
    if not duration_str: return -1
    total = 0
    m = re.search(r'(\d+)\s*d(?:ay)?s?', duration_str)
    if m: total += int(m.group(1)) * 86400
    m = re.search(r'(\d+)\s*h(?:ou)?r?s?', duration_str)
    if m: total += int(m.group(1)) * 3600
    m = re.search(r'(\d+)\s*m(?:in)?(?:ute)?s?', duration_str)
    if m: total += int(m.group(1)) * 60
    return total if total > 0 else -1

def hash_key(key): return hashlib.sha256(key.encode()).hexdigest()

def store_key(key, created_by="admin", max_devices=3, expires_days=None):
    key_hash = hash_key(key); prefix = key.split("-")[0]
    expires_at = None
    if expires_days: expires_at = datetime.now().timestamp() + (expires_days * 86400)
    conn = get_db(); c = conn.cursor()
    try:
        c.execute('''INSERT INTO license_keys (key_hash, key_prefix, created_by, max_devices, expires_at) VALUES (?, ?, ?, ?, ?)''', (key_hash, prefix, created_by, max_devices, expires_at))
        conn.commit(); log_event(f"Key stored: {key[:12]}...")
        return True
    except sqlite3.IntegrityError:
        print(f"{R}[!] Key already exists!{N}"); return False
    finally: conn.close()

def add_permission(key, user_identifier, granted_by="admin", device_limit=1, duration=None):
    key_hash = hash_key(key)
    expires_at = None
    if duration:
        if isinstance(duration, str):
            duration = parse_duration(duration)
        if duration and duration > 0:
            expires_at = datetime.now().timestamp() + duration
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT id FROM license_keys WHERE key_hash = ? AND is_active = 1", (key_hash,))
    if not c.fetchone():
        print(f"{R}[!] Key not found!{N}"); conn.close(); return False
    try:
        c.execute('''INSERT INTO permissions (key_hash, user_identifier, granted_by, device_limit, expires_at) VALUES (?, ?, ?, ?, ?)''', (key_hash, user_identifier, granted_by, device_limit, expires_at))
        conn.commit()
        print(f"{G}[✓] Permission granted to {B}{user_identifier}{N}{G} for key {key[:12]}...{N}")
        return True
    except sqlite3.IntegrityError:
        print(f"{Y}[!] Permission already exists!{N}"); return False
    finally: conn.close()

def validate_key(key, user_identifier, device_id="unknown"):
    key_hash = hash_key(key)
    conn = get_db(); c = conn.cursor()
    c.execute('''SELECT id, max_devices, expires_at FROM license_keys WHERE key_hash = ? AND is_active = 1''', (key_hash,))
    key_row = c.fetchone()
    if not key_row:
        log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, False, "Key not found"); conn.close()
        return False, "Invalid license key!", None
    key_id, max_devices, key_expires = key_row
    if key_expires and time.time() > key_expires:
        log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, False, "Key expired"); conn.close()
        return False, "License key has expired!", None
    c.execute('''SELECT id, device_limit, expires_at FROM permissions WHERE key_hash = ? AND user_identifier = ? AND is_active = 1''', (key_hash, user_identifier))
    perm_row = c.fetchone()
    if not perm_row:
        log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, False, "No permission"); conn.close()
        return False, f"'{user_identifier}' does not have permission. Contact @soulking4045 on Telegram.", None
    perm_id, device_limit, perm_expires = perm_row
    if perm_expires and time.time() > perm_expires:
        log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, False, "Permission expired"); conn.close()
        return False, "Permission has expired!", None
    c.execute('''SELECT COUNT(DISTINCT device_id) FROM usage_log WHERE key_hash = ? AND user_identifier = ? AND action = 'ACTIVATE' AND success = 1 AND timestamp > datetime('now', '-30 days')''', (key_hash, user_identifier))
    device_count = c.fetchone()[0]
    if device_count >= device_limit:
        c.execute("SELECT DISTINCT device_id FROM usage_log WHERE key_hash = ? AND user_identifier = ? AND action = 'ACTIVATE' AND success = 1 ORDER BY timestamp DESC LIMIT ?", (key_hash, user_identifier, device_limit))
        existing = [r[0] for r in c.fetchall()]
        log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, False, f"Device limit ({device_count}/{device_limit})"); conn.close()
        return False, f"Device limit reached ({device_count}/{device_limit})! Devices: {', '.join(existing)}", None
    remaining = "∞"
    if perm_expires: remaining = str(int((perm_expires - time.time()) / 86400))
    data = {"max_devices": max_devices, "device_limit": device_limit, "remaining_days": remaining, "key_prefix": key.split("-")[0]}
    log_usage(conn, key_hash, user_identifier, "VALIDATE", device_id, True, "Access granted"); conn.close()
    return True, f"Access granted! Welcome {user_identifier} ({remaining} days)", data

def log_usage(conn, key_hash, user_identifier, action, device_id, success, details=""):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO usage_log (key_hash, user_identifier, action, device_id, success, details) VALUES (?, ?, ?, ?, ?, ?)''', (key_hash, user_identifier, action, device_id, 1 if success else 0, details))
        conn.commit()
    except: pass

class KeyServerHandler(BaseHTTPRequestHandler):
    def log_message(self, f, *a): log_event(f"HTTP: {a[0]}")
    def _send_json(self, code, data):
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    def do_OPTIONS(self):
        self.send_response(200); self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'); self.send_header('Access-Control-Allow-Headers', 'Content-Type'); self.end_headers()
    def do_GET(self):
        if self.path == "/ping": self._send_json(200, {"status": "ok", "server": "MAC CHECKER v5.3 Key Server"})
        elif self.path == "/stats": self._serve_stats()
        else: self._send_json(404, {"error": "Not found"})
    def do_POST(self):
        cl = int(self.headers.get('Content-Length', 0)); body = self.rfile.read(cl) if cl else b'{}'
        try: data = json.loads(body)
        except: self._send_json(400, {"error": "Invalid JSON"}); return
        if self.path == "/validate": self._handle_validate(data)
        elif self.path == "/activate": self._handle_activate(data)
        elif self.path == "/heartbeat": self._handle_heartbeat(data)
        else: self._send_json(404, {"error": "Not found"})
    def _handle_validate(self, data):
        key = data.get("key", ""); user_id = data.get("user_id", ""); device_id = data.get("device_id", "unknown")
        if not key or not user_id: self._send_json(400, {"valid": False, "message": "Missing key or user_id"}); return
        is_valid, message, extra = validate_key(key, user_id, device_id)
        resp = {"valid": is_valid, "message": message, "timestamp": int(time.time())}
        if extra: resp.update(extra)
        self._send_json(200, resp)
    def _handle_activate(self, data):
        key = data.get("key", ""); user_id = data.get("user_id", ""); device_id = data.get("device_id", "unknown")
        key_hash = hash_key(key); conn = get_db()
        log_usage(conn, key_hash, user_id, "ACTIVATE", device_id, validate_key(key, user_id, device_id)[0], "Device activation"); conn.close()
        self._send_json(200, {"status": "ok"})
    def _handle_heartbeat(self, data): self._send_json(200, {"status": "alive", "server_time": int(time.time())})
    def _serve_stats(self):
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM license_keys WHERE is_active = 1"); ak = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM permissions WHERE is_active = 1"); ap = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM usage_log WHERE success = 1 AND timestamp > datetime('now', '-24 hours')"); du = c.fetchone()[0]
        conn.close()
        self._send_json(200, {"active_keys": ak, "active_permissions": ap, "daily_validations": du, "uptime": int(time.time())})

def log_event(message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); line = f"[{ts}] {message}"
    print(f"{C}[LOG]{N} {line}")
    try:
        with open(LOG_FILE, 'a') as f: f.write(line + "\n")
    except: pass

def print_banner():
    print(f"""
{C}KEY SERVER — MAC CHECKER v5.3{N}
""")

def cli_generate_key():
    print_banner(); key = generate_license_key()
    print(f"\n{G}New Key:{N} {B}{Y}{key}{N}\n"); store_key(key)

def cli_add_user():
    print_banner()
    uid = input(f"{Y}User ID: {N}").strip()
    key = input(f"{Y}License key: {N}").strip()
    dl = input(f"{Y}Device limit (1): {N}").strip() or "1"
    dur = input(f"{Y}Duration e.g. 1h30min, 2h, 30min, 1d (never): {N}").strip()
    duration_val = parse_duration(dur) if dur else None
    add_permission(key=key, user_identifier=uid, device_limit=int(dl), duration=duration_val)

def cli_remove_user():
    print_banner(); uid = input(f"{Y}User ID to remove: {N}").strip()
    conn = get_db(); c = conn.cursor()
    c.execute("UPDATE permissions SET is_active = 0 WHERE user_identifier = ?", (uid,)); n = c.rowcount
    conn.commit(); conn.close()
    print(f"{G}Removed {n} permission(s){N}" if n else f"{Y}No permissions found{N}")

def cli_list_users():
    print_banner()
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT p.user_identifier, lk.key_prefix, p.device_limit, p.granted_at, p.expires_at, p.is_active FROM permissions p JOIN license_keys lk ON p.key_hash = lk.key_hash ORDER BY p.granted_at DESC")
    for row in c.fetchall():
        uid, pf, dl, ga, ex, ac = row
        s = f"{G}ACTIVE{N}" if ac else f"{R}INACTIVE{N}"
        print(f"  {uid:<25} {pf:<10} {dl:<8} {s}")
    conn.close()

def cli_list_keys():
    print_banner()
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT key_prefix, created_at, max_devices, expires_at, is_active FROM license_keys ORDER BY created_at DESC")
    for row in c.fetchall():
        pf, ca, md, ex, ac = row
        s = f"{G}ACTIVE{N}" if ac else f"{R}INACTIVE{N}"
        print(f"  {pf:<8} {ca[:19]:<20} {md:<12} {s}")
    conn.close()

def run_server(port=DEFAULT_PORT):
    print_banner(); init_db()
    server = HTTPServer(('0.0.0.0', port), KeyServerHandler)
    print(f"{G}[✓] Key Server on port {port}{N}")
    print(f"  POST /validate | POST /activate | POST /heartbeat | GET /ping | GET /stats")
    try: server.serve_forever()
    except KeyboardInterrupt: print(f"\n{Y}Server stopped.{N}"); server.shutdown()

if __name__ == "__main__":
    init_db()
    if "--generate-key" in sys.argv: cli_generate_key()
    elif "--add-user" in sys.argv: cli_add_user()
    elif "--remove-user" in sys.argv: cli_remove_user()
    elif "--list-users" in sys.argv: cli_list_users()
    elif "--list-keys" in sys.argv: cli_list_keys()
    else:
        port = DEFAULT_PORT
        for i, a in enumerate(sys.argv):
            if a == "--port" and i+1 < len(sys.argv): port = int(sys.argv[i+1])
        run_server(port)