#!/bin/bash
# ─── MAC CHECKER v5.3 — One-Click Install for Termux & Linux ───
# Usage: bash install.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    🔥 MAC CHECKER v5.3 — Smart Connect Edition  ║${NC}"
echo -e "${CYAN}║              INSTALLER SCRIPT                    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Detect environment
if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    IS_TERMUX=true
    echo -e "${YELLOW}📱 Detected: Termux (Android)${NC}"
else
    IS_TERMUX=false
    echo -e "${YELLOW}💻 Detected: Linux/PC${NC}"
fi

# Install system dependencies
if $IS_TERMUX; then
    echo -e "\n${CYAN}[1/4]${NC} Installing Termux packages..."
    pkg update -y
    pkg install -y python python-pip git clang build-essential
else
    echo -e "\n${CYAN}[1/4]${NC} Checking Python..."
    if ! command -v python3 &>/dev/null; then
        echo -e "${YELLOW}Python3 not found. Installing...${NC}"
        sudo apt-get update -y
        sudo apt-get install -y python3 python3-pip python3-venv git
    fi
fi

# Install Python dependencies
echo -e "\n${CYAN}[2/4]${NC} Installing Python packages..."
pip install --upgrade pip
pip install aiohttp rich

echo -e "\n${CYAN}[3/4]${NC} Verifying installation..."
python3 -c "import aiohttp; import rich; print('  ✅ All dependencies OK')"

# Installation complete
echo -e "\n${CYAN}[4/4]${NC} Installation complete!"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ READY TO RUN!                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Run:  ${YELLOW}python3 mac_checker_v5.py${NC}"
echo ""
echo -e "  First time:"
echo -e "    1. Connect phone via ADB (USB or TCP)"
echo -e "    2. Option 1 → enter phone IP (e.g. 192.168.1.5)"
echo -e "    3. Option 2 → scan & auto-save shop profile"
echo -e "    4. Option 3 → Smart Auto-Connect (zero-touch!)"
echo ""

if $IS_TERMUX; then
    echo -e "  ${YELLOW}⚠️  Termux tips:${NC}"
    echo -e "    • Run: ${GREEN}termux-wake-lock acquire${NC} (prevents sleep)"
    echo -e "    • Give battery: Unrestricted (Settings → Apps → Termux)"
    echo ""
fi
