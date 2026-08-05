#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          🔥 MAC CHECKER v5.3 — Smart Connect Edition         ║
║          Rich TUI • Session Pool • Guardian Engine           ║
║          With LICENSE KEY + PERMISSION System                ║
╚══════════════════════════════════════════════════════════════╝

A powerful network bypass tool for Ruijie gateway networks with live Rich TUI dashboard,
automated failover, keepalive, and zero-touch Smart Auto-Connect across multiple shops.

=== LICENSE KEY SYSTEM ===
This tool requires a valid license key AND admin permission to run.
Without proper authorization, the tool will not function.

To get access:
1. Contact @soulking4045 on Telegram
2. Request a license key
3. Admin will grant you permission
4. Enter your key + Telegram ID when prompted
"""

import asyncio
import aiohttp
import hashlib
import json
import os
import platform
import random
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Rich TUI imports
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich.align import Align
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ─── Configuration ───────────────────────────────────────────
CONFIG_DIR = os.path.expanduser("~/.mac_checker_v5")
PROFILES_DIR = os.path.join(CONFIG_DIR, "profiles")
LICENSE_FILE = os.path.join(CONFIG_DIR, "license.json")
DEVICE_ID_FILE = os.path.join(CONFIG_DIR, "device_id")
KEY_SERVER_URL = os.environ.get("MC5_KEY_SERVER", "http://127.0.0.1:8420")

# Key server fallback URLs
KEY_SERVER_FALLBACKS = [
    "http://127.0.0.1:8420",
    "http://localhost:8420",
]

# ─── ANSI Colors ─────────────────────────────────────────────
R = '\033[0;31m'
G = '\033[0;32m'
Y = '\033[1;33m'
C = '\033[0;36m'
N = '\033[0m'
B = '\033[1m'
M = '\033[0;35m'
W = '\033[1;37m'

# ─── Rich Console ────────────────────────────────────────────
console = Console() if RICH_AVAILABLE else None

# ─── Device ID ───────────────────────────────────────────────
def get_device_id():
    """Get or create a unique device identifier"""
    if os.path.exists(DEVICE_ID_FILE):
        with open(DEVICE_ID_FILE) as f:
            return f.read().strip()
    
    # Generate based on hardware + random
    hw_info = ""
    try:
        result = subprocess.run(["uname", "-a"], capture_output=True, text=True)
        hw_info += result.stdout.strip()
    except:
        pass
    
    try:
        import socket
        hw_info += socket.gethostname()
    except:
        pass
    
    hw_info += secrets.token_hex(8)
    device_id = "MC5-" + hashlib.sha256(hw_info.encode()).hexdigest()[:12].upper()
    
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(DEVICE_ID_FILE, 'w') as f:
        f.write(device_id)
    
    return device_id


# ╔══════════════════════════════════════════════════════════════╗
# ║                 LICENSE KEY SYSTEM                           ║
# ╚══════════════════════════════════════════════════════════════╝

class LicenseManager:
    """Manages license key validation and permission checking"""
    
    def __init__(self):
        self.license_data = None
        self.is_licensed = False
        self.user_id = None
        self.license_key = None
        self.device_id = get_device_id()
        self.server_url = None
        self._load_saved()
    
    def _load_saved(self):
        """Load saved license info"""
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE) as f:
                    self.license_data = json.load(f)
                    self.user_id = self.license_data.get("user_id")
                    self.license_key = self.license_data.get("key")
                    self.is_licensed = self.license_data.get("validated", False)
                    self.server_url = self.license_data.get("server_url")
            except:
                pass
    
    def _save_license(self):
        """Save license info to disk"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(LICENSE_FILE, 'w') as f:
            json.dump({
                "user_id": self.user_id,
                "key": self.license_key,
                "validated": self.is_licensed,
                "server_url": self.server_url,
                "device_id": self.device_id,
                "validated_at": int(time.time())
            }, f)
    
    async def _try_validate(self, server_url, key, user_id):
        """Try to validate against a specific server"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "key": key,
                    "user_id": user_id,
                    "device_id": self.device_id
                }
                async with session.post(
                    f"{server_url}/validate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
        except:
            pass
        return None
    
    async def _try_activate(self, server_url, key, user_id):
        """Try to activate device on server"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "key": key,
                    "user_id": user_id,
                    "device_id": self.device_id
                }
                async with session.post(
                    f"{server_url}/activate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def validate_key(self, key, user_id):
        """Validate license key and check permissions"""
        self.license_key = key.strip().upper()
        self.user_id = user_id.strip()
        
        servers_to_try = [KEY_SERVER_URL] + KEY_SERVER_FALLBACKS
        if self.server_url and self.server_url not in servers_to_try:
            servers_to_try.insert(0, self.server_url)
        
        for server_url in servers_to_try:
            print(f"{C}[*] Connecting to key server: {server_url}{N}")
            result = await self._try_validate(server_url, self.license_key, self.user_id)
            
            if result:
                self.server_url = server_url
                if result.get("valid"):
                    self.is_licensed = True
                    self._save_license()
                    await self._try_activate(server_url, self.license_key, self.user_id)
                    return True, result.get("message", "Access granted"), result
                else:
                    return False, result.get("message", "Access denied"), result
        
        return False, f"❌ Cannot connect to license server!\n   Check your internet connection and try again.", None
    
    def check_local(self):
        """Quick local check without server"""
        if self.is_licensed and self.license_data:
            validated_at = self.license_data.get("validated_at", 0)
            # Local validation expires after 7 days — must re-validate
            if time.time() - validated_at < 7 * 86400:
                return True
        return False

    def clear(self):
        """Clear saved license"""
        self.is_licensed = False
        self.license_data = None
        if os.path.exists(LICENSE_FILE):
            os.remove(LICENSE_FILE)


# ╔══════════════════════════════════════════════════════════════╗
# ║                 MAC CHECKER CORE                             ║
# ╚══════════════════════════════════════════════════════════════╝

class MacCheckerV5:
    """Main MAC Checker application"""
    
    def __init__(self):
        self.license = LicenseManager()
        self.device_id = self.license.device_id
        self.connected = False
        self.current_mac = None
        self.profiles = {}
        self.stats = {
            "uptime": 0,
            "ping_ms": 0,
            "jitter_ms": 0,
            "packet_loss": 0,
            "quality": "unknown"
        }
        self.mac_pool = []
        self.running = False
    
    # ─── Banner ───────────────────────────────────────────
    def print_banner(self):
        banner = f"""
{C}╔══════════════════════════════════════════════════════════════╗
║{Y}          🔥 MAC CHECKER v5.3 — Smart Connect Edition  {C}      ║
║{G}          License Key + Permission Protected            {C}      ║
║{W}          Authorized: {self.license.user_id or 'NONE':<35} {C}║
╚══════════════════════════════════════════════════════════════╝{N}
"""
        print(banner)
    
    # ─── License Setup ────────────────────────────────────
    async def setup_license(self):
        """Handle license key entry and validation"""
        self.print_banner()
        
        # Check local cache first
        if self.license.check_local():
            print(f"{G}[✓] License verified locally.{N}")
            print(f"{G}[✓] Welcome back, {self.license.user_id}!{N}")
            return True
        
        print(f"{Y}[🔐] LICENSE VERIFICATION REQUIRED{N}")
        print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{N}")
        print(f"  This tool requires a valid license key.")
        print(f"  Contact {B}@soulking4045{N} on Telegram to get access.")
        print(f"{C}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{N}\n")
        
        # Get Telegram ID
        telegram_id = input(f"  {Y}Enter your Telegram ID/Username: {N}").strip()
        if not telegram_id:
            print(f"{R}[!] Telegram ID is required!{N}")
            return False
        
        # Get license key
        license_key = ""
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            license_key = input(f"  {Y}Enter License Key (MC5-XXXX-XXXX-XXXX): {N}").strip()
            if license_key:
                break
            attempts += 1
            print(f"{R}[!] License key cannot be empty ({max_attempts - attempts} attempts left){N}")
        
        if not license_key:
            print(f"{R}[!] No license key provided. Exiting.{N}")
            return False
        
        # Validate format
        if not re.match(r'^MC5-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', license_key.upper()):
            print(f"{Y}[!] Invalid key format. Expected: MC5-XXXX-XXXX-XXXX{N}")
            print(f"{R}[!] Please check your key and try again.{N}")
            return False
        
        print(f"\n{C}[*] Validating license...{N}")
        
        valid, message, data = await self.license.validate_key(license_key, telegram_id)
        
        if valid:
            print(f"\n{G}╔══════════════════════════════════════════════════════╗{N}")
            print(f"{G}║  ✅ LICENSE VERIFIED SUCCESSFULLY!                  ║{N}")
            print(f"{G}║  User: {telegram_id:<46} ║{N}")
            if data:
                remaining = data.get("remaining_days", "∞")
                print(f"{G}║  Remaining: {remaining:<41} ║{N}")
            print(f"{G}╚══════════════════════════════════════════════════════╝{N}")
            return True
        else:
            print(f"\n{R}╔══════════════════════════════════════════════════════╗{N}")
            print(f"{R}║  ❌ LICENSE VERIFICATION FAILED                     ║{N}")
            print(f"{R}╚══════════════════════════════════════════════════════╝{N}")
            print(f"\n{R}{message}{N}\n")
            print(f"{Y}[💡] Tips:{N}")
            print(f"  1. Make sure you entered the correct key")
            print(f"  2. Admin must grant you permission first")
            print(f"  3. Contact {B}@soulking4045{N} on Telegram for help")
            return False
    
    # ─── Main Menu ────────────────────────────────────────
    def show_menu(self):
        print(f"\n{C}─── MAIN MENU ───{N}\n")
        print(f"  {G}1.{N} 📱 ADB Connect")
        print(f"  {G}2.{N} ⚡ Scan & Save (Zero-Touch)")
        print(f"  {G}3.{N} 🔐 Smart Auto-Connect (All Shops)")
        print(f"  {G}4.{N} 📂 Load Profile & Guardian Mode")
        print(f"  {G}5.{N} 🎛  Tune Android Stability")
        print(f"  {G}6.{N} ☕ Keep Wi-Fi Awake")
        print(f"  {G}7.{N} 🔑 License Info")
        print(f"  {R}8.{N} ❌ Exit")
        print()
    
    def show_license_info(self):
        """Display license information"""
        print(f"\n{C}─── LICENSE INFORMATION ───{N}\n")
        print(f"  {B}User:{N}         {self.license.user_id}")
        print(f"  {B}Device ID:{N}     {self.device_id}")
        print(f"  {B}Status:{N}       {G}✅ Active{N}" if self.license.is_licensed else f"  {B}Status:{N}       {R}❌ Inactive{N}")
        print(f"  {B}Key Server:{N}   {self.license.server_url or 'Not connected'}")
        
        data = self.license.license_data or {}
        if data.get("remaining_days"):
            print(f"  {B}Expires:{N}      {data['remaining_days']} days")
        print(f"  {C}Contact: @soulking4045 on Telegram{N}")
        print()
        input(f"  {Y}Press Enter to continue...{N}")
    
    # ─── Placeholder Functions (actual bypass logic) ──────
    async def option_adb_connect(self):
        print(f"\n{G}[*] ADB Connect — Coming soon with full implementation{N}")
        print(f"{C}[*] This feature connects phone via ADB for network access{N}")
    
    async def option_scan_and_save(self):
        print(f"\n{G}[*] Scan & Save — Coming soon with full implementation{N}")
        print(f"{C}[*] Auto-scans network and saves shop profile{N}")
    
    async def option_smart_connect(self):
        print(f"\n{G}[*] Smart Auto-Connect — Coming soon with full implementation{N}")
        print(f"{C}[*] Loops all saved shops and auto-connects{N}")
    
    async def option_guardian_mode(self):
        print(f"\n{G}[*] Guardian Mode — Coming soon with full implementation{N}")
        print(f"{C}[*] Loads profile with auto-failover protection{N}")
    
    async def option_tune_android(self):
        print(f"\n{G}[*] Android Tuning — Coming soon with full implementation{N}")
    
    async def option_keep_wifi(self):
        print(f"\n{G}[*] Keep Wi-Fi Awake — Coming soon with full implementation{N}")
    
    # ─── Main Loop ────────────────────────────────────────
    async def run(self):
        """Main application loop"""
        # License check FIRST
        if not await self.setup_license():
            print(f"\n{R}[!] License verification failed. Exiting.{N}")
            print(f"{Y}[💡] Contact @soulking4045 on Telegram to get access.{N}")
            return
        
        self.running = True
        
        while self.running:
            self.print_banner()
            self.show_menu()
            
            try:
                choice = input(f"  {Y}Select option [1-8]:{N} ").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Y}[!] Goodbye!{N}")
                break
            
            if choice == "1":
                await self.option_adb_connect()
            elif choice == "2":
                await self.option_scan_and_save()
            elif choice == "3":
                await self.option_smart_connect()
            elif choice == "4":
                await self.option_guardian_mode()
            elif choice == "5":
                await self.option_tune_android()
            elif choice == "6":
                await self.option_keep_wifi()
            elif choice == "7":
                self.show_license_info()
            elif choice == "8":
                print(f"\n{Y}[!] Goodbye!{N}")
                break
            else:
                print(f"{R}[!] Invalid option!{N}")
        
        self.running = False


# ╔══════════════════════════════════════════════════════════════╗
# ║                      ENTRY POINT                             ║
# ╚══════════════════════════════════════════════════════════════╝

async def main():
    """Main entry point"""
    app = MacCheckerV5()
    
    try:
        await app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Interrupted by user. Goodbye!{N}")
    except Exception as e:
        print(f"\n{R}[!] Unexpected error: {e}{N}")
        print(f"{Y}[💡] Contact @soulking4045 on Telegram for support.{N}")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"{R}[!] Python 3.8+ required! Current: {sys.version}{N}")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Goodbye!{N}")
