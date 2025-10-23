# ROTMG Patch Utility Tool - Build Configuration

This directory contains the build configuration for creating a standalone executable.

## Building the Application

### Windows
Run the `build.bat` file:
```batch
build.bat
```

### Linux/macOS
Run the `build.sh` file:
```bash
chmod +x build.sh
./build.sh
```

## Manual Build

If the automated build scripts don't work, you can build manually:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build the executable:
```bash
pyinstaller --onefile --windowed --name "ROTMG_Patch_Utility" main.py
```

## Build Output

The built executable will be in the `dist/` directory along with:
- `ROTMG_Patch_Utility.exe` (Windows) or `ROTMG_Patch_Utility` (Linux/macOS)
- `patches.json` (default patches file)
- `README.md`
- `LICENSE`

## Requirements

- Python 3.7 or higher
- pip package manager
- PyInstaller (installed via requirements.txt)
- UnityPy (installed via requirements.txt)

## Troubleshooting

If you encounter issues:

1. Make sure Python and pip are installed and in your PATH
2. Try running `pip install --upgrade pip` first
3. On Windows, you might need to run the command prompt as Administrator
4. On Linux/macOS, you might need to use `python3` and `pip3` instead of `python` and `pip`
