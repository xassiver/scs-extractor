import os
import subprocess
import zipfile
import shutil
import sys
import tempfile

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def extract_archive(file_path, target_dir):
    """
    Extracts zip, rar, or 7z files using 7-Zip CLI.
    """
    # We will assume 7za.exe is in the same directory or bundled
    seven_zip_path = get_resource_path("7za.exe")
    
    if not os.path.exists(seven_zip_path):
        # Fallback for dev if not bundled yet
        seven_zip_path = "7za.exe" 

    try:
        # x: extract with full paths
        # -y: assume yes on all queries
        # -o: output directory
        cmd = [seven_zip_path, "x", file_path, f"-o{target_dir}", "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, result.stderr
        return True, None
    except Exception as e:
        return False, str(e)

def pack_scs(source_dir, output_path):
    """
    Packs the content of source_dir into a .scs file (which is a ZIP file).
    ETS2 usually prefers 'Store' (no compression) for performance, 
    but standard ZIP compression also works.
    """
    try:
        # Create a zip file but with .scs extension
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        return True, None
    except Exception as e:
        return False, str(e)
