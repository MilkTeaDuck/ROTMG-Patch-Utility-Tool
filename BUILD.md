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

### "Ordinal Not Found" Error
If you encounter an "Ordinal Not Found" error when running the executable:

1. **Try the console build**: Run `build_console.bat` instead of `build.bat` - this creates a version with console output for debugging
2. **Check dependencies**: Make sure all required packages are installed:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Use the spec file**: The build scripts now use a comprehensive PyInstaller spec file that includes all necessary hidden imports
4. **Alternative build method**: If the issue persists, try building manually:
   ```bash
   pyinstaller --onefile --console --collect-all UnityPy --collect-all lz4 main.py
   ```

### Common Issues
- **Missing DLLs**: The spec file includes all UnityPy and lz4 dependencies
- **Import errors**: All necessary hidden imports are specified
- **File not found**: The patches directory is automatically included in the build
