#!/bin/sh
# Activate venv and run main.py as a module
VENV_DIR="$(dirname "$0")/venv"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Virtual environment not found in $VENV_DIR. Please create it first."
    exit 1
fi
. "$VENV_DIR/bin/activate"
python -m src.main
