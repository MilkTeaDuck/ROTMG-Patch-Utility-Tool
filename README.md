# ROTMG Assets Patch Utility Tool

A comprehensive GUI application for patching and managing assets in Realm of the Mad God (ROTMG). This tool provides a user-friendly interface for applying regex-based patches to Unity assets files.

## Description

This tool is a modular .exe application that allows you to:
- Apply regex-based patches to ROTMG resources.assets files
- Manage patch collections with add/edit/remove functionality
- Selectively apply patches with toggle controls
- Create and restore backups automatically
- View detailed logging and progress information

## Features

- **GUI Interface**: Modern tkinter-based interface for easy operation
- **Modular Patch System**: Add, edit, and remove patches dynamically
- **Selective Patching**: Choose which patches to apply
- **Backup Management**: Automatic backup creation and restoration
- **Real-time Logging**: Detailed progress and error reporting
- **Progress Tracking**: Visual progress bars during patching
- **Patch Validation**: Built-in validation for patch data integrity
- **Cross-platform**: Works on Windows, Linux, and macOS

## Installation

### Option 1: Download Pre-built Executable
1. Download the latest release from the [Releases](https://github.com/MilkTeaDuck/ROTMG-Patch-Utility-Tool/releases) page
2. Extract the files to your desired location
3. Run `ROTMG_Patch_Utility.exe`

### Option 2: Build from Source
1. Clone the repository:
```bash
git clone https://github.com/MilkTeaDuck/ROTMG-Patch-Utility-Tool.git
cd ROTMG-Patch-Utility-Tool
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build the executable:
```bash
# Windows
build.bat

# Linux/macOS
chmod +x build.sh
./build.sh
```

## Usage

### Running the Application
1. Launch `ROTMG_Patch_Utility.exe` (or the appropriate executable for your OS)
2. The application will automatically load all patches from the `patches/` directory
3. Select your `resources.assets` file using the Browse button
4. Select which patches you want to apply from the loaded list
5. Click "Apply Selected Patches" or "Apply All Patches"

### Managing Patches
- **Auto-loading**: Patches are automatically loaded from the `patches/` directory on startup
- **Add Patch**: Create new patches with custom regex patterns
- **Edit Patch**: Modify existing patch names, locators, and rules
- **Remove Patch**: Delete patches you no longer need
- **Save Patches**: Export your patch collection to a single JSON file
- **Save to Directory**: Save all patches as individual files in the `patches/` directory
- **Load Patches**: Import patches from a JSON file (overrides auto-loaded patches)

### Patch Directory Structure
The application uses a `patches/` directory containing individual patch files:
```
patches/
├── 01_Ice_Citadel_State_Patches.json
├── 02_Better_Tips.json
├── 03_Spoof_Lucky_Clover_as_Potion_of_Speed.json
└── ... (more patch files)
```

Each patch file contains a single patch definition:
```json
{
  "name": "Patch Name",
  "locator": "regex pattern to find the asset",
  "patches": [
    {
      "target": "regex pattern to match",
      "replacement": "replacement text"
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect the terms of service of Realm of the Mad God and use this tool responsibly.

## Author

MilkTeaDuck

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
