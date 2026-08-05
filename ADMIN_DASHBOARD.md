# 🔥 MAC CHECKER v5.3 — Admin Dashboard Guide

## 🎉 NEW: Web-Based Admin Dashboard!

Admin တွေအတွက် full-featured web dashboard ကို Zaro workspace မှာ deploy လုပ်ပြီးပါပြီ။

### Features:
- 🔑 **One-click Key Generation** - MC5-XXXX-XXXX-XXXX keys တွေကို click တစ်ချက်တည်းနဲ့ ထုတ်နိုင်
- 👥 **Grant Permission** - User တွေကို GUI form ကနေ permission ပေးနိုင်
- 📊 **Real-time Statistics** - Active keys, users, usage rate တွေကို live monitor
- 📱 **Device Tracking** - ဘယ်သူဘယ် device (Android/Termux/Linux) ကနေသုံးလဲ track လုပ်
- 🔒 **Revoke/Reactivate** - Permission တွေကို click တစ်ချက်နဲ့ manage
- 📋 **Copy to Clipboard** - Keys တွေကို ချက်ချင်း copy လုပ်နိုင်
- 🎨 **Beautiful UI** - Modern, playful design (Linear-inspired)

### How to Access:
1. Zaro workspace ကို ဖွင့်ပါ
2. Apps tab ကနေ **"MAC CHECKER v5 — Admin Dashboard"** ကို click
3. Overview → Keys → Users → Logs tabs တွေကို လွယ်လင့်တကူ navigate

### Workflow:

**Step 1: Generate Key**
- Header ရဲ့ **"Generate Key"** button ကို click
- New key modal ပေါ်လာ → Copy button နဲ့ ကူးယူ

**Step 2: Grant Permission**
- **"Grant Permission"** button ကို click (သို့) new key modal က **"Grant Now"**
- Form ဖြည့်:
  - Telegram ID/Username (e.g. @kyaw123)
  - License Key (dropdown ကနေ ရွေး)
  - Device Limit (default: 1)
  - Expires (days, blank = never)
  - Notes (optional)
- **"Grant Permission"** button click

**Step 3: Share with User**
- User ကို Telegram ID + License Key ကို ပို့
- User က `python3 mac_checker_v5.py` run လိုက်ရင် enter လုပ်ရုံပဲ

### Data Structure:
All data stored in workspace `.table` files:
- `/mac-checker-v5/admin/license_keys.table` - All generated keys
- `/mac-checker-v5/admin/permissions.table` - User permissions
- `/mac-checker-v5/admin/usage_log.table` - Activity logs
- `/mac-checker-v5/admin/admins.table` - Admin accounts

### Screenshots:

**Overview Tab:**
- Stat cards: Active Keys | Active Users | Today Usage | Success Rate
- Recent activity feed with device icons
- Top users leaderboard with usage bars
- Quick Start guide (3-step)

**License Keys Tab:**
- Search + status filter
- Key list with prefix, created time, user count, device limit
- Actions: Activate/Deactivate, Delete
- Copy to clipboard

**Users Tab:**
- User list with Telegram ID, assigned key, device limit
- Grant time, expiry, notes
- Actions: Revoke/Reactivate

**Usage Logs Tab:**
- Real-time activity feed
- Device type icons (Android/Termux/Linux)
- Success/failure indicators
- User identifier + action + details

---

## For Users:

User တွေက tool သုံးဖို့:
1. Contact **@soulking4045** on Telegram
2. License key + activation request
3. Admin က dashboard ကနေ approve
4. Tool ကို run:
   ```bash
   python3 mac_checker_v5.py
   # Enter Telegram ID
   # Enter License Key (MC5-XXXX-XXXX-XXXX)
   # Tool validates → Access granted!
   ```

---

Made with ❤️ in Myanmar 🇲🇲
