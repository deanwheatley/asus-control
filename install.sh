#!/bin/bash
# ASUS Fan Control Installer
# Sets up the application and creates desktop entry

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "ASUS Fan Control - Installation"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 > /dev/null 2>&1; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check python3-venv
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo ""
    echo "❌ Error: python3-venv is not installed."
    echo ""
    echo "Please install it with:"
    echo "  sudo apt install python${PYTHON_VERSION}-venv"
    echo ""
    echo "Then run this installer again."
    exit 1
fi

echo "✅ python3-venv is available"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Make launcher executable
chmod +x asus-control-launcher.sh

# Install desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/asus-control.desktop"
DESKTOP_DIR="$(dirname "$DESKTOP_FILE")"

mkdir -p "$DESKTOP_DIR"

# Create desktop entry with absolute path
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ASUS Fan Control
Comment=Modern GUI for ASUS laptop fan curve configuration with system monitoring
Exec=$SCRIPT_DIR/asus-control-launcher.sh
Path=$SCRIPT_DIR
Icon=applications-system
Terminal=false
Categories=System;Settings;HardwareSettings;
StartupNotify=true
Keywords=asus;fan;temperature;cooling;laptop;control;
EOF

chmod +x "$DESKTOP_FILE"

echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "The application has been installed and added to your application menu."
echo ""
echo "You can now:"
echo "  1. Launch it from your application menu (search for 'ASUS Fan Control')"
echo "  2. Or run it directly: ./asus-control-launcher.sh"
echo "  3. Or run it from terminal: source venv/bin/activate && python3 run.py"
echo ""
echo "To uninstall, remove:"
echo "  - $DESKTOP_FILE"
echo "  - $SCRIPT_DIR/venv (optional)"
echo ""

