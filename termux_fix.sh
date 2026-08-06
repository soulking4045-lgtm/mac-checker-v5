#!/data/data/com.termux/files/usr/bin/bash
# MAC CHECKER v5.3 — Termux Quick Fix & Run
# Fixes pip error + creates run.sh + starts bot

set -e
echo ""
echo "============================================"
echo " MAC CHECKER v5.3 — FIX & RUN"
echo "============================================"
echo ""
echo "[1/3] Installing Python packages in Ubuntu (fixed)..."
proot-distro login ubuntu -- bash -c '
pip3 install --break-system-packages aiohttp rich python-telegram-bot
echo "[OK] Packages installed"
'
echo ""
echo "[2/3] Creating run.sh & stop.sh..."
cat > ~/mac-checker-v5/run.sh << 'RUNEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mac-checker-v5
proot-distro login ubuntu --bind ~/mac-checker-v5:/root/mac-checker-v5 -- bash -c '
cd /root/mac-checker-v5
export MC5_BOT_TOKEN="8933721915:AAFQ79GCSOMse5oy-ZznzofTbqjrUzPGvzw"
export MC5_ADMIN_IDS=""
screen -S keyserver -X quit 2>/dev/null || true
screen -S bot -X quit 2>/dev/null || true
sleep 1
echo "[*] Starting Key Server..."
screen -dmS keyserver python3 bot_key_server.py --port 8420
sleep 2
echo "[*] Starting Telegram Bot..."
screen -dmS bot python3 bot.py
echo ""
echo "BOT IS RUNNING 24/7!"
echo "  screen -r bot       → bot logs"
echo "  screen -r keyserver → server logs"
echo "  Ctrl+A D            → detach"
'
RUNEOF
cat > ~/mac-checker-v5/stop.sh << 'STOPEOF'
#!/data/data/com.termux/files/usr/bin/bash
proot-distro login ubuntu -- bash -c '
screen -S keyserver -X quit 2>/dev/null
screen -S bot -X quit 2>/dev/null
echo "Bot stopped"
'
STOPEOF
cat > ~/mac-checker-v5/logs.sh << 'LOGSEOF'
#!/data/data/com.termux/files/usr/bin/bash
proot-distro login ubuntu -- screen -r bot
LOGSEOF
cat > ~/mac-checker-v5/restart.sh << 'RESTARTEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mac-checker-v5
bash stop.sh
sleep 2
bash run.sh
RESTARTEOF
chmod +x ~/mac-checker-v5/run.sh
chmod +x ~/mac-checker-v5/stop.sh
chmod +x ~/mac-checker-v5/logs.sh
chmod +x ~/mac-checker-v5/restart.sh
echo "[OK] Scripts created"
echo ""
echo "[3/3] Starting the bot..."
bash ~/mac-checker-v5/run.sh
echo ""
echo "Done! Open Telegram and test your bot."
echo "Send: /start"