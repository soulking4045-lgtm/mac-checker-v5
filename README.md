# MAC CHECKER v5.3 - Smart Connect Edition
> Rich TUI | Session Pool | Guardian Engine | Smart Auto-Connect
> NOW WITH LICENSE KEY + PERMISSION SYSTEM

A powerful network bypass tool for Ruijie gateway networks.

## LICENSE KEY SYSTEM (NEW!)
This tool requires a valid license key AND admin permission.

### For Users:
1. Contact @soulking4045 on Telegram
2. Request access to MAC CHECKER v5
3. Receive license key (format: MC5-XXXX-XXXX-XXXX)
4. Enter key + Telegram ID when tool starts

### For Admin:
```bash
python3 bot_key_server.py --port 8420   # Start key server
python3 bot_key_server.py --generate-key  # Generate key
python3 bot_key_server.py --add-user      # Grant permission
python3 bot_key_server.py --list-users    # List users
python3 bot_key_server.py --list-keys     # List keys
python3 bot_key_server.py --remove-user   # Revoke access
```

## Quick Install
```bash
git clone https://github.com/soulking4045-lgtm/mac-checker-v5.git
cd mac-checker-v5
bash install.sh
python3 mac_checker_v5.py
```

## Menu
1. ADB Connect
2. Scan & Save (Zero-Touch)
3. Smart Auto-Connect (All Shops)
4. Load Profile & Guardian Mode
5. Tune Android Stability
6. Keep Wi-Fi Awake
7. License Info
8. Exit

## Requirements
- Python 3.8+
- aiohttp, rich
- ADB + phone connected
- Valid license key + admin permission

## Key Server API
| Endpoint | Method | Description |
|----------|--------|-------------|
| /validate | POST | Validate key + permission |
| /activate | POST | Log device activation |
| /heartbeat | POST | Server health check |
| /ping | GET | Ping server |
| /stats | GET | Server statistics |

## File Structure
- mac_checker_v5.py - Main tool with license validation
- bot_key_server.py - License key management server
- install.sh - One-click installer
- requirements.txt - Python dependencies

## License
MIT License

## Disclaimer
For educational purposes only. Use only on networks you own.

Contact: @soulking4045 on Telegram
Made with heart in Myanmar