#!/bin/bash

echo "Building ROTMG Patch Utility Tool..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements"
    exit 1
fi

# Create build directory
mkdir -p build dist

# Check if icon file exists
if [ ! -f "duck_icon.ico" ]; then
    echo "Warning: duck_icon.ico not found. Building without custom icon."
    echo "To add the duck icon, place duck_icon.ico in the project root directory."
fi

# Build the executable using spec file
echo "Building executable..."
pyinstaller ROTMG_Patch_Utility.spec
if [ $? -ne 0 ]; then
    echo "Error: Failed to build executable"
    exit 1
fi

# Copy additional files to dist directory
echo "Copying additional files..."
cp patches.json dist/ 2>/dev/null || true
cp README.md dist/ 2>/dev/null || true
cp LICENSE dist/ 2>/dev/null || true
cp -r patches dist/ 2>/dev/null || true

echo "Build complete! Executable is in the 'dist' directory."
