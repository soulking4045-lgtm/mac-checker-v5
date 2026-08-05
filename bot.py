#!/usr/bin/env python3
"""MAC CHECKER v5.3 — Telegram Bot | License Permission Management"""
import hashlib, hmac, json, os, re, secrets, sqlite3, sys, time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ─── Config ───────────────────────────────────────────
CONFIG_DIR = os.path.expanduser("~/.mac_checker_v5")
DB_PATH = os.path.join(CONFIG_DIR, "keys.db")
BOT_TOKEN = os.environ.get("MC5_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.environ.get("MC5_ADMIN_IDS", "").split(",") if x.strip()]

# If no admin IDs set in env, allow anyone (or set specific IDs)
ALLOW_ALL = len(ADMIN_IDS) == 0

R,G,Y,C,N,B = '\033[0;31m','\033[0;32m','\033[1;33m','\033[0;36m','\033[0m','\033[1m'

# ─── Database ──────────────────────────────────────────
def get_db(): return sqlite3.connect(DB_PATH)

def hash_key(key): return hashlib.sha256(key.encode()).hexdigest()

# ─── Parse Time ───────────────────────────────────────
def parse_duration(duration_str: str) -> int:
    """Parse time string like: 1h30min, 2h, 45min, 1d, 3d12h. Returns total seconds, or -1."""
    if not duration_str:
        return -1
    duration_str = duration_str.lower().strip()
    total_seconds = 0
    day_match = re.search(r'(\d+)\s*d(?:ay)?s?', duration_str)
    if day_match:
        total_seconds += int(day_match.group(1)) * 86400
    hour_match = re.search(r'(\d+)\s*h(?:ou)?r?s?', duration_str)
    if hour_match:
        total_seconds += int(hour_match.group(1)) * 3600
    min_match = re.search(r'(\d+)\s*m(?:in)?(?:ute)?s?', duration_str)
    if min_match:
        total_seconds += int(min_match.group(1)) * 60
    sec_match = re.search(r'(\d+)\s*s(?:ec)?(?:ond)?s?', duration_str)
    if sec_match:
        total_seconds += int(sec_match.group(1))
    return total_seconds if total_seconds > 0 else -1

def format_duration(seconds: int) -> str:
    """Convert seconds to human-readable format"""
    if seconds <= 0:
        return "never"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}min")
    return " ".join(parts) if parts else f"{seconds}s"

# ─── Check Admin ──────────────────────────────────────
def is_admin(user_id: int) -> bool:
    if ALLOW_ALL:
        return True
    return user_id in ADMIN_IDS

# ─── Key Management ───────────────────────────────────
def ensure_key_exists(key: str) -> bool:
    """Check if key exists in DB, if not create it"""
    key_hash = hash_key(key)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM license_keys WHERE key_hash = ?", (key_hash,))
    if not c.fetchone():
        prefix = key.split("-")[0]
        try:
            c.execute('''INSERT INTO license_keys (key_hash, key_prefix, created_by, max_devices) 
                         VALUES (?, ?, ?, ?)''', (key_hash, prefix, "telegram_bot", 3))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
    conn.close()
    return True

def grant_permission(key: str, user_identifier: str, duration_seconds: int = None, device_limit: int = 1, granted_by: str = "admin"):
    """Grant time-limited permission to a user"""
    key_hash = hash_key(key)
    expires_at = None
    if duration_seconds and duration_seconds > 0:
        expires_at = datetime.now().timestamp() + duration_seconds
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM license_keys WHERE key_hash = ? AND is_active = 1", (key_hash,))
    if not c.fetchone():
        conn.close()
        return False, "Key not found or inactive!"
    c.execute('''SELECT id, expires_at, is_active FROM permissions 
                 WHERE key_hash = ? AND user_identifier = ?''', (key_hash, user_identifier))
    existing = c.fetchone()
    if existing:
        perm_id, old_exp, is_active = existing
        if is_active:
            c.execute('''UPDATE permissions SET expires_at = ?, device_limit = ?, is_active = 1, granted_by = ?
                         WHERE id = ?''', (expires_at, device_limit, granted_by, perm_id))
            conn.commit()
            conn.close()
            return True, "updated"
        else:
            c.execute('''UPDATE permissions SET expires_at = ?, device_limit = ?, is_active = 1, granted_by = ?
                         WHERE id = ?''', (expires_at, device_limit, granted_by, perm_id))
            conn.commit()
            conn.close()
            return True, "reactivated"
    try:
        c.execute('''INSERT INTO permissions (key_hash, user_identifier, granted_by, device_limit, expires_at)
                     VALUES (?, ?, ?, ?, ?)''', (key_hash, user_identifier, granted_by, device_limit, expires_at))
        conn.commit()
        conn.close()
        return True, "granted"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Permission already exists!"

def revoke_permission(key: str, user_identifier: str):
    """Revoke a user's permission"""
    key_hash = hash_key(key)
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE permissions SET is_active = 0 
                 WHERE key_hash = ? AND user_identifier = ? AND is_active = 1''', 
              (key_hash, user_identifier))
    count = c.rowcount
    conn.commit()
    conn.close()
    return count

# ─── Bot Commands ─────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    user = update.effective_user
    welcome_msg = f"""🔥 *MAC CHECKER v5.3 — Bot Server*

Welcome, {user.first_name}!

*Admin Commands:*
`/genkey <time> <key>` — Grant permission with time limit
`/revoke <key> <user_id>` — Remove permission
`/keyinfo <key>` — Check key details
`/listusers [key]` — List all users / users for a key
`/generatekey` — Generate a new license key

*Time Formats:*
`1h30min` = 1 hour 30 min
`2h` = 2 hours
`45min` = 45 minutes
`1d` = 1 day
`3d12h` = 3 days 12 hours

*Example:*
`/genkey 1h30min MC5-547M-4PUH-SGK6 @kyaw123`"""
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Grant permission: /genkey <time> <key> [user_id]"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ *Admin only!* You are not authorized.", parse_mode="Markdown")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: `/genkey <time> <key> [user_id]`\n\n"
            "Example: `/genkey 1h30min MC5-547M-4PUH-SGK6 @kyaw123`\n"
            "Example: `/genkey 2h MC5-XXXX-XXXX-XXXX @user`",
            parse_mode="Markdown")
        return
    duration_str = args[0]
    key = args[1].upper().strip()
    target_user = args[2] if len(args) > 2 else ""
    if not re.match(r'^MC5-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', key):
        await update.message.reply_text("❌ Invalid key format! Expected: `MC5-XXXX-XXXX-XXXX`", parse_mode="Markdown")
        return
    duration_seconds = parse_duration(duration_str)
    if duration_seconds <= 0:
        await update.message.reply_text(
            "❌ Invalid time format!\n"
            f"Got: `{duration_str}`\n"
            "Valid: `1h30min`, `2h`, `45min`, `1d`, `3d12h`",
            parse_mode="Markdown")
        return
    ensure_key_exists(key)
    if not target_user:
        target_user = update.effective_user.username or str(user_id)
    success, action = grant_permission(key, target_user, duration_seconds, granted_by=str(user_id))
    if success:
        duration_readable = format_duration(duration_seconds)
        expires_time = datetime.now() + timedelta(seconds=duration_seconds)
        expires_str = expires_time.strftime("%Y-%m-%d %H:%M:%S")
        action_emoji = {"granted": "✅", "updated": "🔄", "reactivated": "♻️"}.get(action, "✅")
        await update.message.reply_text(
            f"{action_emoji} *Permission {action}!*\n\n"
            f"▸ *Key:* `{key[:14]}...`\n"
            f"▸ *User:* `{target_user}`\n"
            f"▸ *Duration:* {duration_readable}\n"
            f"▸ *Expires:* {expires_str}\n\n"
            f"_User can now use this key for {duration_readable}._",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Failed: {action}", parse_mode="Markdown")

async def generate_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a new license key: /generatekey"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ *Admin only!*", parse_mode="Markdown")
        return
    import hmac as hmac_mod
    secret_file = os.path.join(CONFIG_DIR, ".secret")
    if os.path.exists(secret_file):
        with open(secret_file, 'rb') as f:
            secret = f.read()
    else:
        secret = secrets.token_bytes(32)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(secret_file, 'wb') as f:
            f.write(secret)
        os.chmod(secret_file, 0o600)
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(4).upper()
    payload = f"MC5:{timestamp}:{random_part}"
    signature = hmac_mod.new(secret, payload.encode(), hashlib.sha256).hexdigest()[:8].upper()
    new_key = f"MC5-{random_part[:4]}-{random_part[4:8]}-{signature}"
    conn = get_db()
    c = conn.cursor()
    key_hash_val = hash_key(new_key)
    try:
        c.execute('''INSERT INTO license_keys (key_hash, key_prefix, created_by, max_devices) 
                     VALUES (?, ?, ?, ?)''', (key_hash_val, "MC5", str(user_id), 3))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    await update.message.reply_text(
        f"🔑 *New Key Generated:*\n\n"
        f"`{new_key}`\n\n"
        f"_Use `/genkey <time> {new_key} <user>` to grant access._",
        parse_mode="Markdown")

async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Revoke permission: /revoke <key> <user_id>"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ *Admin only!*", parse_mode="Markdown")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Usage: `/revoke <key> <user_id>`", parse_mode="Markdown")
        return
    key = args[0].upper().strip()
    target_user = args[1]
    count = revoke_permission(key, target_user)
    if count > 0:
        await update.message.reply_text(
            f"✅ *Permission revoked!*\nUser `{target_user}` can no longer use key `{key[:14]}...`",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(
            f"⚠️ No active permission found for `{target_user}` on key `{key[:14]}...`",
            parse_mode="Markdown")

async def keyinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check key info: /keyinfo <key>"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ *Admin only!*", parse_mode="Markdown")
        return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("⚠️ Usage: `/keyinfo <key>`", parse_mode="Markdown")
        return
    key = args[0].upper().strip()
    key_hash = hash_key(key)
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT key_prefix, created_by, max_devices, expires_at, is_active, created_at 
                 FROM license_keys WHERE key_hash = ?''', (key_hash,))
    key_row = c.fetchone()
    if not key_row:
        conn.close()
        await update.message.reply_text("❌ Key not found!", parse_mode="Markdown")
        return
    prefix, created_by, max_dev, key_exp, is_active, created_at = key_row
    status = "✅ Active" if is_active else "❌ Inactive"
    c.execute('''SELECT user_identifier, device_limit, expires_at, is_active, granted_at 
                 FROM permissions WHERE key_hash = ? ORDER BY granted_at DESC''', (key_hash,))
    perms = c.fetchall()
    conn.close()
    msg = f"🔑 *Key Info:* `{key[:14]}...`\n\n"
    msg += f"▸ Prefix: `{prefix}`\n"
    msg += f"▸ Status: {status}\n"
    msg += f"▸ Max Devices: {max_dev}\n"
    msg += f"▸ Created: {created_at}\n"
    msg += f"▸ Key Expires: {key_exp or 'Never'}\n\n"
    if perms:
        msg += f"*Permissions ({len(perms)}):*\n"
        for p in perms[:10]:
            uid, dl, pexp, pactive, ga = p
            ps = "✅" if pactive else "❌"
            pexp_str = pexp or "Never"
            msg += f"  {ps} `{uid}` — limit:{dl} exp:{pexp_str}\n"
    else:
        msg += "_No permissions granted yet._"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List users: /listusers [key]"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ *Admin only!*", parse_mode="Markdown")
        return
    args = context.args
    conn = get_db()
    c = conn.cursor()
    if args:
        key = args[0].upper().strip()
        key_hash = hash_key(key)
        c.execute('''SELECT user_identifier, device_limit, expires_at, is_active, granted_at 
                     FROM permissions WHERE key_hash = ? ORDER BY granted_at DESC LIMIT 20''', (key_hash,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            await update.message.reply_text(f"No users found for key `{key[:14]}...`", parse_mode="Markdown")
            return
        msg = f"*Users for key* `{key[:14]}...`:\n\n"
        for r in rows:
            uid, dl, exp, act, ga = r
            status = "✅" if act else "❌"
            exp_str = exp or "Never"
            msg += f"  {status} `{uid}` (limit:{dl}, exp:{exp_str})\n"
    else:
        c.execute('''SELECT p.user_identifier, lk.key_prefix, p.device_limit, p.expires_at, p.is_active, p.granted_at 
                     FROM permissions p JOIN license_keys lk ON p.key_hash = lk.key_hash 
                     ORDER BY p.granted_at DESC LIMIT 20''')
        rows = c.fetchall()
        conn.close()
        if not rows:
            await update.message.reply_text("No users found.", parse_mode="Markdown")
            return
        msg = f"*All Users ({len(rows)}):*\n\n"
        for r in rows:
            uid, prefix, dl, exp, act, ga = r
            status = "✅" if act else "❌"
            exp_str = exp or "Never"
            msg += f"  {status} `{uid}` [{prefix}] (limit:{dl}, exp:{exp_str})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─── Main ─────────────────────────────────────────────

def main():
    print(f"{C}╔══════════════════════════════════════════════════════════════╗{N}")
    print(f"{C}║{Y}        🔥 MAC CHECKER v5.3 — Telegram Bot Server     {C}      ║{N}")
    print(f"{C}║{G}              Admin License & Permission Bot           {C}      ║{N}")
    print(f"{C}╚══════════════════════════════════════════════════════════════╝{N}")
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"\n{R}[!] ERROR: Bot token not set!{N}")
        print(f"{Y}Set the MC5_BOT_TOKEN environment variable:{N}")
        print(f"{C}  export MC5_BOT_TOKEN=your_bot_token_here{N}")
        print(f"{Y}Optionally set admin IDs:{N}")
        print(f"{C}  export MC5_ADMIN_IDS=123456789,987654321{N}")
        sys.exit(1)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("genkey", genkey_command))
    app.add_handler(CommandHandler("generatekey", generate_key_command))
    app.add_handler(CommandHandler("revoke", revoke_command))
    app.add_handler(CommandHandler("keyinfo", keyinfo_command))
    app.add_handler(CommandHandler("listusers", listusers_command))
    print(f"\n{G}[✓]{N} Bot is running...")
    print(f"{C}[*]{N} Commands: /genkey /generatekey /revoke /keyinfo /listusers")
    if ALLOW_ALL:
        print(f"{Y}[!] Warning: ALLOW_ALL mode — anyone can use admin commands!{N}")
        print(f"{Y}    Set MC5_ADMIN_IDS=your_id to restrict.{N}")
    print()
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()