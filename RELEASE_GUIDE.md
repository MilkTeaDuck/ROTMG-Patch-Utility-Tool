# GitHub Release Guide

## Creating a Release Package

### Step 1: Build the Application
First, build the executable:
```bash
# Windows
build.bat

# Linux/macOS
chmod +x build.sh
./build.sh
```

### Step 2: Create Release Package
Run the release packaging script:
```bash
# Windows
create_release.bat

# Linux/macOS
chmod +x create_release.sh
./create_release.sh
```

### Step 3: Release Package Contents
The `release/` directory will contain:
- `ROTMG_Patch_Utility.exe` (Windows) or `ROTMG_Patch_Utility` (Linux/macOS)
- `patches/` directory with all individual patch files
- `README.md` - Full documentation
- `LICENSE` - MIT License
- `BUILD.md` - Build instructions
- `QUICK_START.md` - Simple usage guide
- `VERSION.txt` - Version information

### Step 4: Create GitHub Release

#### Option A: Using GitHub Web Interface
1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose a tag (e.g., `v1.0.0`)
4. Add release title: "ROTMG Patch Utility Tool v1.0.0"
5. Add release description:
   ```
   ## Features
   - Modular patch system with individual patch files
   - Enhanced patch creation with character count preservation
   - Auto-loading patches from patches/ directory
   - Backup and restore functionality
   - Real-time preview and logging
   - Cross-platform support (Windows, Linux, macOS)
   
   ## Installation
   1. Download the appropriate executable for your OS
   2. Extract all files to a folder
   3. Run the executable
   
   ## Usage
   See QUICK_START.md for basic usage or README.md for detailed instructions.
   ```
6. Upload the entire `release/` folder as a ZIP file
7. Click "Publish release"

#### Option B: Using GitHub CLI
```bash
# Install GitHub CLI if not already installed
# Then create release:
gh release create v1.0.0 \
  --title "ROTMG Patch Utility Tool v1.0.0" \
  --notes "Initial release with modular patch system and character count preservation" \
  release/*
```

### Step 5: Alternative - Create ZIP Archive
If you prefer to upload a single ZIP file:
```bash
# Windows
powershell Compress-Archive -Path "release\*" -DestinationPath "ROTMG_Patch_Utility_v1.0.0.zip"

# Linux/macOS
cd release && zip -r ../ROTMG_Patch_Utility_v1.0.0.zip . && cd ..
```

## Release Checklist
- [ ] Application builds successfully
- [ ] Executable runs without errors
- [ ] All patches are included in patches/ directory
- [ ] Documentation is up to date
- [ ] Version number is correct
- [ ] Release notes are comprehensive
- [ ] Appropriate OS-specific executables are included

## Multi-Platform Releases
For releases supporting multiple platforms:
1. Build on each platform (Windows, Linux, macOS)
2. Create separate release packages for each
3. Upload all packages to the same GitHub release
4. Clearly label which executable is for which OS
