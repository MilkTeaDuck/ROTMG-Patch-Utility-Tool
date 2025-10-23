#!/bin/bash

echo "Creating release package for GitHub..."

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "Error: dist directory not found. Please run build.sh first."
    exit 1
fi

# Create release directory
if [ -d "release" ]; then
    rm -rf "release"
fi
mkdir "release"

# Copy executable
echo "Copying executable..."
cp "dist/ROTMG_Patch_Utility" "release/"

# Copy patches directory
echo "Copying patches directory..."
cp -r "patches" "release/"

# Copy documentation
echo "Copying documentation..."
cp "README.md" "release/"
cp "LICENSE" "release/"
cp "BUILD.md" "release/"

# Create a simple usage guide
echo "Creating usage guide..."
cat > "release/QUICK_START.md" << 'EOF'
# ROTMG Patch Utility Tool - Quick Start

## Installation
1. Download ROTMG_Patch_Utility
2. Place it in a folder with the patches directory
3. Run the executable

## Usage
1. Launch ROTMG_Patch_Utility
2. Select your resources.assets file
3. Choose which patches to apply
4. Click "Apply Selected Patches"

## Features
- Auto-loads patches from patches/ directory
- Enhanced patch creation with character count preservation
- Backup and restore functionality
- Real-time preview and logging

For detailed instructions, see README.md
EOF

# Create version info file
echo "Creating version info..."
cat > "release/VERSION.txt" << EOF
ROTMG Patch Utility Tool
Version: 1.0.0
Build Date: $(date)

Features:
- Modular patch system
- Character count preservation
- Enhanced patch creation dialog
- Auto-loading from patches directory
- Backup and restore functionality
EOF

echo ""
echo "Release package created in 'release' directory!"
echo "Contents:"
ls -la "release"
echo ""
echo "Ready for GitHub release upload."
