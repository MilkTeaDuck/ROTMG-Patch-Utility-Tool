@echo off
echo Building ROTMG Patch Utility Tool...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)

REM Create build directory
if not exist "build" mkdir build
if not exist "dist" mkdir dist

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --name "ROTMG_Patch_Utility" --icon=icon.ico main.py
if errorlevel 1 (
    echo Error: Failed to build executable
    pause
    exit /b 1
)

REM Copy additional files to dist directory
echo Copying additional files...
copy "patches.json" "dist\" 2>nul
copy "README.md" "dist\" 2>nul
copy "LICENSE" "dist\" 2>nul
xcopy "patches" "dist\patches\" /E /I /Q 2>nul

echo Build complete! Executable is in the 'dist' directory.
pause
