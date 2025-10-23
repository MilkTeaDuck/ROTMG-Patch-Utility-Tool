@echo off
echo Creating release package for GitHub...

REM Check if dist directory exists
if not exist "dist" (
    echo Error: dist directory not found. Please run build.bat first.
    pause
    exit /b 1
)

REM Create release directory
if exist "release" rmdir /s /q "release"
mkdir "release"

REM Copy executable
echo Copying executable...
copy "dist\ROTMG_Patch_Utility.exe" "release\"

REM Copy patches directory
echo Copying patches directory...
xcopy "patches" "release\patches\" /E /I /Q

REM Copy documentation
echo Copying documentation...
copy "README.md" "release\"
copy "LICENSE" "release\"
copy "BUILD.md" "release\"

REM Create a simple usage guide
echo Creating usage guide...
(
echo # ROTMG Patch Utility Tool - Quick Start
echo.
echo ## Installation
echo 1. Download ROTMG_Patch_Utility.exe
echo 2. Place it in a folder with the patches directory
echo 3. Run the executable
echo.
echo ## Usage
echo 1. Launch ROTMG_Patch_Utility.exe
echo 2. Select your resources.assets file
echo 3. Choose which patches to apply
echo 4. Click "Apply Selected Patches"
echo.
echo ## Features
echo - Auto-loads patches from patches/ directory
echo - Enhanced patch creation with character count preservation
echo - Backup and restore functionality
echo - Real-time preview and logging
echo.
echo For detailed instructions, see README.md
) > "release\QUICK_START.md"

REM Create version info file
echo Creating version info...
(
echo ROTMG Patch Utility Tool
echo Version: 1.0.0
echo Build Date: %date% %time%
echo.
echo Features:
echo - Modular patch system
echo - Character count preservation
echo - Enhanced patch creation dialog
echo - Auto-loading from patches directory
echo - Backup and restore functionality
) > "release\VERSION.txt"

echo.
echo Release package created in 'release' directory!
echo Contents:
dir "release" /b
echo.
echo Ready for GitHub release upload.
pause
