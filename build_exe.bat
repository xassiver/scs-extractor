@echo off
REM Build single-file executable with PyInstaller and bundle resource binaries.
REM Place 7za.exe and unrar.exe into the "resources" folder before building.
set PYINSTALLER_FLAGS=--noconfirm --onefile --console --name "SCT"





pause
necho Build finished. See the dist\SCT.exe file.pyinstaller %PYINSTALLER_FLAGS% --add-data "resources\7za.exe;resources" --add-data "resources\unrar.exe;resources" sct.pynREM Ensure virtualenv/requirements installed: pip install pyinstaller