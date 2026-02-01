@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
echo Preparing resources folder...
if not exist resources mkdir resources

REM Check for Chocolatey
where choco >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Chocolatey found. Installing 7zip and unrar via choco...
    choco install 7zip -y --no-progress
    choco install unrar -y --no-progress

    echo Copying installed executables to resources folder...
    if exist "%ProgramFiles%\7-Zip\7z.exe" (
        copy /Y "%ProgramFiles%\7-Zip\7z.exe" resources\7za.exe >nul
    ) else (
        if exist "%ProgramFiles(x86)%\7-Zip\7z.exe" (
            copy /Y "%ProgramFiles(x86)%\7-Zip\7z.exe" resources\7za.exe >nul
        )
    )

    REM Try to locate unrar.exe
    where unrar >nul 2>&1
    if %ERRORLEVEL%==0 (
        for /f "delims=" %%a in ('where unrar') do (
            copy /Y "%%a" resources\unrar.exe >nul
            goto copied_unrar
        )
    )
    if exist "%ProgramFiles%\UnRAR\UnRAR.exe" (
        copy /Y "%ProgramFiles%\UnRAR\UnRAR.exe" resources\unrar.exe >nul
    ) else if exist "%ProgramFiles(x86)%\UnRAR\UnRAR.exe" (
        copy /Y "%ProgramFiles(x86)%\UnRAR\UnRAR.exe" resources\unrar.exe >nul
    )
    :copied_unrar

    echo Done. Check the resources folder.
    exit /b 0
)

echo Chocolatey not found. Please install Chocolatey or place 7za.exe and unrar.exe into the resources folder manually.
echo To install Chocolatey, open an elevated PowerShell and run:
echo Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
echo Or download 7-Zip and UnRAR manually and copy their EXE files into the resources folder.
exit /b 1
