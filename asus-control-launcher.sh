#!/bin/bash
# ASUS Fan Control Launcher
# Automatically handles virtual environment and launches the application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    # Try to create venv automatically
    echo "Virtual environment not found. Creating it..."
    
    # Check if python3-venv is available
    if ! python3 -m venv --help > /dev/null 2>&1; then
        # Show error dialog if possible
        if command -v zenity > /dev/null 2>&1; then
            zenity --error --text="python3-venv is not installed.\n\nPlease install it with:\nsudo apt install python3-venv\n\nThen run the setup script:\npython3 setup_venv.py" --title="Setup Required"
        else
            echo "Error: python3-venv is not installed."
            echo "Please install it with: sudo apt install python3-venv"
            echo "Then run: python3 setup_venv.py"
            read -p "Press Enter to exit..."
        fi
        exit 1
    fi
    
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        if command -v zenity > /dev/null 2>&1; then
            zenity --error --text="Failed to create virtual environment.\n\nPlease run the setup script manually:\npython3 setup_venv.py" --title="Setup Error"
        else
            echo "Failed to create virtual environment."
            echo "Please run: python3 setup_venv.py"
            read -p "Press Enter to exit..."
        fi
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    if [ $? -ne 0 ]; then
        if command -v zenity > /dev/null 2>&1; then
            zenity --error --text="Failed to install dependencies.\n\nPlease run manually:\nsource venv/bin/activate\npip install -r requirements.txt" --title="Installation Error"
        else
            echo "Failed to install dependencies."
            echo "Please run: pip install -r requirements.txt"
            read -p "Press Enter to exit..."
        fi
        exit 1
    fi
fi

# Run the application
python3 run.py

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

exit $EXIT_CODE

