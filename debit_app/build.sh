#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo " Building Gestionnaire de Debit - Desktop"
echo "============================================"

echo
echo "[1/2] Installing dependencies..."
python3 -m pip install -r requirements-desktop.txt

echo
echo "[2/2] Building executable..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "GestionnaireDebit" \
    --add-data "config/nomenclature.json:config" \
    --collect-submodules PyQt6 \
    main.py

echo
echo "============================================"
echo " Build complete!"
echo " Executable: dist/GestionnaireDebit"
echo "============================================"
