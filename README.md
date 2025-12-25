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

### Requirements
- Python 3.7+
- PyInstaller
- 7-Zip standalone executable (`7za.exe`)

### Build Steps

1. Install dependencies:
```bash
pip install pyinstaller
```

2. Download `7za.exe` and place it in the project directory

3. Build the executable:
```bash
python -m PyInstaller --noconfirm --onefile --console --name "SCT" --add-data "7za.exe;." sct.py
```

The executable will be created in the `dist` folder.

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
