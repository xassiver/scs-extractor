import os
import sys
import shutil
import tempfile
import time
from tkinter import filedialog
import tkinter as tk
from utils import extract_archive, pack_scs, check_for_update

# ASCII ART and Colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner():
    banner = f"""
{BLUE}{BOLD}    ███████╗ ██████╗████████╗
    ██╔════╝██╔════╝╚══██╔══╝
    ███████╗██║        ██║   
    ╚════██║██║        ██║   
    ███████║╚██████╗   ██║   
    ╚══════╝ ╚═════╝   ╚═╝   
    SCS Conversion Tool v1.1{RESET}
    Developed for ETS2/ATS Modders
    """
    print(banner)

def convert_scs_to_zip(scs_files):
    """
    Convert .scs files to .zip files (SCS files are already ZIP format)
    """
    print(f"{BLUE}[*] Converting {len(scs_files)} SCS file(s) to ZIP...{RESET}")
    
    success_count = 0
    for scs_file in scs_files:
        if not os.path.exists(scs_file):
            print(f"{RED}[-] File not found: {scs_file}{RESET}")
            continue
        
        # Create output path with .zip extension
        base_name = os.path.splitext(os.path.basename(scs_file))[0]
        output_path = os.path.join(os.path.dirname(scs_file), f"{base_name}.zip")
        
        try:
            # SCS files are already ZIP files, just copy and rename
            shutil.copy2(scs_file, output_path)
            print(f"{GREEN}[+] Converted: {os.path.basename(scs_file)} → {os.path.basename(output_path)}{RESET}")
            success_count += 1
        except Exception as e:
            print(f"{RED}[-] Failed to convert {os.path.basename(scs_file)}: {str(e)}{RESET}")
    
    if success_count > 0:
        # Open File Explorer to the first converted file's location
        first_converted = os.path.join(os.path.dirname(scs_files[0]), 
                                      f"{os.path.splitext(os.path.basename(scs_files[0]))[0]}.zip")
        if os.path.exists(first_converted):
            print(f"{BLUE}[*] Opening File Explorer...{RESET}")
            import subprocess
            subprocess.run(['explorer', '/select,', first_converted], shell=True)
    
    return success_count

def select_files():
    """
    Open a file picker dialog to select files for conversion
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    files = filedialog.askopenfilenames(
        title="Select files to convert",
        filetypes=[
            ("Archive files", "*.zip *.rar *.7z *.scs"),
            ("ZIP files", "*.zip"),
            ("RAR files", "*.rar"),
            ("7Z files", "*.7z"),
            ("SCS files", "*.scs"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return list(files) if files else []

def main():
    os.system('color') # Enable ANSI colors on Windows
    print_banner()

    CURRENT_VERSION = "1.1"

    # Parse args: accept optional --repo <github_url> followed by file paths
    raw_args = sys.argv[1:]
    # Default to user's repo if not provided
    DEFAULT_REPO = "https://github.com/xassiver/scs-extractor"
    repo_url = None
    files = []
    i = 0
    while i < len(raw_args):
        a = raw_args[i]
        if a in ('--repo', '-r') and i + 1 < len(raw_args):
            repo_url = raw_args[i+1]
            i += 2
        else:
            files.append(a)
            i += 1

    # Use provided repo or default
    if not repo_url:
        repo_url = DEFAULT_REPO

    # Check for updates (English message)
    if repo_url:
        try:
            is_newer, latest_tag, html_url, err = check_for_update(repo_url, CURRENT_VERSION)
            if err:
                print(f"[UPDATE CHECK ERROR] {err}")
            else:
                if is_newer:
                    print(f"\n[UPDATE] New version available: {latest_tag}\nVisit: {html_url}\n")
                else:
                    print(f"[UPDATE] You are running the latest version ({CURRENT_VERSION}).")
        except Exception as e:
            print(f"[UPDATE CHECK EXCEPTION] {e}")

    # If no files were collected from args, keep using the files list parsed above
    if not files:
        files = []

    if not files:
        # Open file picker dialog
        print(f"{YELLOW}[!] No files provided. Opening file picker...{RESET}")
        files = select_files()
        
        if not files:
            print(f"{YELLOW}[!] No files selected.{RESET}")
            input("\nPress Enter to exit...")
            return

    print(f"{BLUE}[*] Process started for {len(files)} file(s)...{RESET}")

    # Separate SCS files from archive files
    scs_files = [f for f in files if f.lower().endswith('.scs')]
    archive_files = [f for f in files if not f.lower().endswith('.scs')]

    # Handle SCS to ZIP conversion
    if scs_files:
        convert_scs_to_zip(scs_files)
    
    # Handle archive to SCS conversion
    if archive_files:
        # Create a temporary directory for extraction
        temp_dir = tempfile.mkdtemp(prefix="sct_work_")
        
        try:
            success_count = 0
            for i, file_path in enumerate(archive_files):
                if not os.path.exists(file_path):
                    print(f"{RED}[-] File not found: {file_path}{RESET}")
                    continue

                print(f"{BLUE}[{i+1}/{len(archive_files)}] Extracting: {os.path.basename(file_path)}...{RESET}")
                success, error = extract_archive(file_path, temp_dir)
                
                if success:
                    success_count += 1
                else:
                    print(f"{RED}[-] Extraction failed: {error}{RESET}")

            if success_count == 0:
                print(f"{RED}[-] No files were successfully extracted.{RESET}")
            else:
                # Output naming
                if len(archive_files) == 1:
                    base_name = os.path.splitext(os.path.basename(archive_files[0]))[0]
                else:
                    base_name = f"merged_mod_{int(time.time())}"
                
                output_name = f"{base_name}.scs"
                output_path = os.path.join(os.path.dirname(archive_files[0]), output_name)

                print(f"{YELLOW}[*] Packing into {output_name}...{RESET}")
                pack_success, pack_error = pack_scs(temp_dir, output_path)

                if pack_success:
                    print(f"{GREEN}[+] SUCCESS: Mod file created at:{RESET}")
                    print(f"{GREEN}{output_path}{RESET}")
                    
                    # Open File Explorer to the output location
                    print(f"{BLUE}[*] Opening File Explorer...{RESET}")
                    import subprocess
                    subprocess.run(['explorer', '/select,', output_path], shell=True)
                else:
                    print(f"{RED}[-] Packing failed: {pack_error}{RESET}")

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"\n{BLUE}[*] Task finished.{RESET}")
    # Wait for user if there were messages to read
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
