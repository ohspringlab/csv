@echo off
echo ============================================
echo  Building Gestionnaire de Debit - Meubles
echo ============================================

echo.
echo [1/2] Installing dependencies...
pip install -r requirements-desktop.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo [2/2] Building executable...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "GestionnaireDebit" ^
    --add-data "config\nomenclature.json;config" ^
    --collect-submodules PyQt6 ^
    main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build complete!
echo  Executable: dist\GestionnaireDebit.exe
echo ============================================
pause
