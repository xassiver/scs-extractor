# SCS Conversion Tool

A standalone tool to convert ZIP, RAR, and 7z archive files into `.scs` mod files for Euro Truck Simulator 2 and American Truck Simulator.

## Features

- ✅ Convert ZIP, RAR, 7z files to SCS format
- ✅ Drag-and-drop support
- ✅ Merge multiple archives into a single SCS file
- ✅ Automatically opens File Explorer to show the created file
- ✅ Standalone executable - no Python installation required

## Usage

### Download
Download the latest `SCT.exe` from the [Releases](../../releases) page.

### How to Use

1. **Drag and Drop**: Drag archive files onto `SCT.exe`
2. **Open With**: Right-click an archive → Open with → Select `SCT.exe`
3. **Command Line**: `SCT.exe file1.zip file2.rar file3.7z`

When converting multiple files, they will be merged into a single `.scs` file with a timestamped name.

## Building from Source

### Goal
Create a single-file Windows `SCT.exe` that contains the Python runtime and bundled helper binaries so end-users don't need to supply `7za.exe` or `unrar.exe` separately.

### Requirements
- Python 3.8+ (recommended)
- PyInstaller

### Prepare resources
Create a `resources` folder in the project root and place the helper binaries there:

- `resources\7za.exe` (7-Zip standalone)
- `resources\unrar.exe` (UnRAR)

You will not ship these executables next to the final `SCT.exe` — they will be bundled inside the exe.

### Build Steps (Windows)
1. Install PyInstaller:
```powershell
pip install pyinstaller
```
2. Place `7za.exe` and `unrar.exe` into the `resources` folder.
3. Run the provided build script:
```powershell
.\build_exe.bat
```

PyInstaller will bundle the `resources` files into the single `dist\SCT.exe` file.

### Running
- Drag-and-drop an archive or run from command line:
```powershell
dist\SCT.exe file1.rar file2.7z
```

The built `SCT.exe` produced by the provided build process bundles the helper binaries (`7za.exe`, `unrar.exe`) inside the executable. If you upload only the single `SCT.exe` to the GitHub Releases page, end users will not need to provide `7za.exe` or `unrar.exe` separately — the exe is self-contained.

The tool also checks your project's GitHub releases (fixed to your repo) and prints a short English message in the console when a newer release tag exists.

## Project Structure

```
SCS/
├── sct.py          # Main application source code
├── utils.py        # Utility functions for archive handling
├── 7za.exe         # 7-Zip standalone executable
├── SCT.exe         # Built executable (not in repo)
└── README.md       # This file
```

## License

Free to use and modify.

## Credits

Developed for ETS2/ATS modders.
