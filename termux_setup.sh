#!/data/data/com.termux/files/usr/bin/bash
# MAC CHECKER v5.3 — Termux + Ubuntu PROOT Setup
# Run once to install: bash termux_setup.sh

set -e
echo ""
echo "============================================"
echo " MAC CHECKER v5.3 — Termux Setup"
echo "============================================"
echo ""
echo "[1/5] Installing proot-distro + Ubuntu..."
pkg update -y && pkg upgrade -y
pkg install -y proot-distro git curl
if ! proot-distro list | grep -q ubuntu; then
    echo "       Installing Ubuntu (3-5 min)..."
    proot-distro install ubuntu
fi
echo "[OK] Ubuntu ready"
echo ""
echo "[2/5] Installing Python + pip in Ubuntu..."
proot-distro login ubuntu -- bash -c "
apt update && apt upgrade -y
apt install -y python3 python3-pip screen
pip3 install aiohttp rich python-telegram-bot
"
echo "[OK] Dependencies installed"
echo ""
REPO_DIR="/data/data/com.termux/files/home/mac-checker-v5"
echo "[3/5] Cloning mac-checker-v5..."
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR" && git pull
else
    git clone https://github.com/soulking4045-lgtm/mac-checker-v5.git "$REPO_DIR"
fi
echo "[OK] Repo ready"
echo ""
echo "[4/5] Creating .env with bot token..."
cat > "$REPO_DIR/.env" << 'EOF'
MC5_BOT_TOKEN=8933721915:AAFQ79GCSOMse5oy-ZznzofTbqjrUzPGvzw
MC5_ADMIN_IDS=
EOF
echo "[OK] .env created"
echo ""
echo "[5/5] Creating launcher..."
cat > "$REPO_DIR/run.sh" << 'RUNEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mac-checker-v5
proot-distro login ubuntu --bind ~/mac-checker-v5:/root/mac-checker-v5 -- bash -c '
cd /root/mac-checker-v5
export $(grep -v "^#" .env | xargs)
screen -S keyserver -X quit 2>/dev/null || true
screen -S bot -X quit 2>/dev/null || true
screen -dmS keyserver python3 bot_key_server.py --port 8420
sleep 2
screen -dmS bot python3 bot.py
echo "Bot + Key Server started!"
echo "screen -r bot / screen -r keyserver"
'
RUNEOF
chmod +x "$REPO_DIR/run.sh"
cat > "$REPO_DIR/stop.sh" << 'STOPEOF'
#!/data/data/com.termux/files/usr/bin/bash
proot-distro login ubuntu -- bash -c '
screen -S keyserver -X quit 2>/dev/null
screen -S bot -X quit 2>/dev/null
echo "Services stopped"
'
STOPEOF
chmod +x "$REPO_DIR/stop.sh"
echo ""
echo "============================================"
echo " SETUP COMPLETE!"
echo "============================================"
echo ""
echo " To START: cd ~/mac-checker-v5 && ./run.sh"
echo " To STOP:  cd ~/mac-checker-v5 && ./stop.sh"
echo ""
echo " Test bot: @mac_checker_v5_bot on Telegram"