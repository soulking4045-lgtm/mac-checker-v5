# 🔥 MAC CHECKER v5.3 — Smart Connect Edition

> **Rich TUI • Session Pool • Guardian Engine • Smart Auto-Connect**

A powerful network bypass tool for Ruijie gateway networks with live Rich TUI dashboard,
automated failover, keepalive, and zero-touch Smart Auto-Connect across multiple shops.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Smart Auto-Connect** | 🔐 One-click → loops ALL saved shops, auto-connects to first working MAC |
| **Zero-Touch Scan & Save** | ⚡ Scan → bypass try → auto-save profile (no name prompt needed) |
| **Guardian Engine** | 🛡️ Auto-failover, preemptive MAC switching, keepalive pings |
| **Preemptive Switch** | ⚠️ Ping > 150ms → instant MAC switch before disconnect |
| **Session Pool** | 🏊 Pre-warmed sessions for instant failover |
| **Multi-Layer Ping** | ICMP + HTTP + TCP — detect real latency |
| **Device Name Discovery** | 📡 9 methods (OUI, DHCP, mDNS, NetBIOS, ARP, dumpsys wifi…) |
| **OUI Database** | 🗄️ 105+ entries (PS5, RPi4, Tuya, Samsung, Apple…) |
| **Rich TUI Dashboard** | 📊 Live ping graph, MAC table, quality indicator 🟢🟡🟠🔴 |
| **Termux-Optimized** | 📱 Auto-detects Android → reduced workers to avoid OOM |

---

## 📦 Quick Install

### Termux (Android)
```bash
# 1. Clone
git clone https://github.com/soulking4045-lgtm/mac-checker-v5.git
cd mac-checker-v5

# 2. Install
bash install.sh

# 3. Run
python3 mac_checker_v5.py

# 4. (Optional) Prevent phone sleep
termux-wake-lock acquire
```

### Linux / PC
```bash
git clone https://github.com/soulking4045-lgtm/mac-checker-v5.git
cd mac-checker-v5
bash install.sh
python3 mac_checker_v5.py
```

---

## 🎮 Menu

```
1. 📱 ADB Connect
2. ⚡ Scan & Save (Zero-Touch)
3. 🔐 Smart Auto-Connect (All Shops)    ← ⭐ NEW!
4. 📂 Load Profile & Guardian Mode
5. 🎛  Tune Android Stability
6. ☕ Keep Wi-Fi Awake
7. ❌ Exit
```

---

## 🚀 Workflow

### First time at a shop:
1. **Option 1** → connect phone ADB
2. **Option 2** → scan network → auto-try bypass → auto-save profile
3. Done! Profile saved as `shop_192_168_X_X.json`

### Returning to ANY saved shop:
1. **Option 3** → one click
2. Tool loops ALL profiles → tries known-working MACs → connects instantly
3. Guardian engine auto-manages connection!
4. **Zero manual input required!** 🔥

---

## 📊 TUI Dashboard

```
🛡️  MAC CHECKER v5.3 Smart Connect
MAC: 96:1C:64:EE:FE:10  │  Uptime: 2h35m  │  ● 42ms  jitter: 2.1ms  🟡 Good

📊 Ping Graph: █▄▃▂▄█▃▄▁▆█▄▃▂▄▆█▃▄▁█▅▃▂▄▆▃█▄▁▅█▃▂▄▅▆▃█▄▁▅

📡 MAC Pool (48 devices)
  ⭐ 96:1C:64:EE:FE:10  RPi4-Living    ● 42ms  0% loss  2.1ms jitter
     AA:BB:CC:DD:EE:FF  Samsung-TV     ● 51ms  0% loss  3.2ms jitter
     ...
```

---

## ⚙️ Config (Ruijie-Tuned)

| Setting | Value |
|--------|-------|
| Preemptive switch threshold | 150ms |
| Spike fails → switch | 2 spikes |
| Failover trigger | 2 consecutive fails |
| Recovery interval | 2.0s |
| Cooldown (stable) | 0.3s (<30ms) / 0.5s (<50ms) |
| Keepalive | TCP DNS every 20s |
| Session reuse | 12× / 90s |

---

## 🛠️ Requirements

- Python 3.8+
- `aiohttp` (HTTP async)
- `rich` (TUI)
- ADB (Android Debug Bridge) + phone connected

---

## 📝 Dependencies

```
aiohttp>=3.9.0
rich>=13.0.0
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Use only on networks you own or have permission to test. The author is not responsible for any misuse.

---

**Made with ❤️ in Myanmar 🇲🇲**
