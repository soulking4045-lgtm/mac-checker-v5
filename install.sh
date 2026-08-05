#!/bin/bash
# MAC CHECKER v5.3 Installer - License Key + Permission Protected
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
echo ""; echo -e "${CYAN}MAC CHECKER v5.3 - Installer${NC}"; echo ""
if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    IS_TERMUX=true; echo -e "${YELLOW}Detected: Termux (Android)${NC}"
else
    IS_TERMUX=false; echo -e "${YELLOW}Detected: Linux/PC${NC}"
fi
if $IS_TERMUX; then
    echo -e "\n${CYAN}[1/4]${NC} Installing Termux packages..."
    pkg update -y; pkg install -y python python-pip git clang build-essential
else
    echo -e "\n${CYAN}[1/4]${NC} Checking Python..."
    if ! command -v python3 &>/dev/null; then
        echo -e "${YELLOW}Python3 not found. Installing...${NC}"
        sudo apt-get update -y; sudo apt-get install -y python3 python3-pip python3-venv git
    fi
fi
echo -e "\n${CYAN}[2/4]${NC} Installing Python packages..."
pip install --upgrade pip; pip install aiohttp rich
echo -e "\n${CYAN}[3/4]${NC} Verifying..."
python3 -c "import aiohttp; import rich; print('  All deps OK')"
mkdir -p ~/.mac_checker_v5/profiles
echo -e "\n${CYAN}[4/4]${NC} Installation complete!"
echo ""
echo -e "${GREEN}READY TO RUN!${NC}"
echo -e "  Run:  ${YELLOW}python3 mac_checker_v5.py${NC}"
echo -e "  Server: ${YELLOW}python3 bot_key_server.py${NC}"
echo ""
echo -e "  FIRST TIME: Contact @soulking4045 on Telegram for license key"
if $IS_TERMUX; then
    echo -e "  Termux tip: termux-wake-lock acquire (prevents sleep)"
fi
echo ""
