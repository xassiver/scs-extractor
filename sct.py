import os
import sys
import shutil
import tempfile
import time
from utils import extract_archive, pack_scs

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
    SCS Conversion Tool v1.0{RESET}
    Developed for ETS2/ATS Modders
    """
    print(banner)

def main():
    os.system('color') # Enable ANSI colors on Windows
    print_banner()

    # Drop target or args
    files = sys.argv[1:]

    if not files:
        print(f"{YELLOW}[!] Instruction:{RESET} Drag and drop zip, rar, or 7z files onto this EXE.")
        print(f"{YELLOW}[!] Instruction:{RESET} Or use 'Open with' to select this application.")
        input("\nPress Enter to exit...")
        return

    print(f"{BLUE}[*] Process started for {len(files)} file(s)...{RESET}")

    # Create a temporary directory for extraction
    temp_dir = tempfile.mkdtemp(prefix="sct_work_")
    
    try:
        success_count = 0
        for i, file_path in enumerate(files):
            if not os.path.exists(file_path):
                print(f"{RED}[-] File not found: {file_path}{RESET}")
                continue

            print(f"{BLUE}[{i+1}/{len(files)}] Extracting: {os.path.basename(file_path)}...{RESET}")
            success, error = extract_archive(file_path, temp_dir)
            
            if success:
                success_count += 1
            else:
                print(f"{RED}[-] Extraction failed: {error}{RESET}")

        if success_count == 0:
            print(f"{RED}[-] No files were successfully extracted.{RESET}")
        else:
            # Output naming
            if len(files) == 1:
                base_name = os.path.splitext(os.path.basename(files[0]))[0]
            else:
                base_name = f"merged_mod_{int(time.time())}"
            
            output_name = f"{base_name}.scs"
            output_path = os.path.join(os.path.dirname(files[0]), output_name)

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
