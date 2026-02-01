import os
import subprocess
import zipfile
import shutil
import sys
import tempfile
import json
import urllib.request
import urllib.error
import socket

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def try_run_fetch_resources(timeout=60):
    """If a fetch_resources.bat script exists next to the project, run it to populate resources."""
    try:
        # Prefer script in project root or scripts folder
        candidates = [get_resource_path('fetch_resources.bat'),
                      os.path.join(os.path.dirname(get_resource_path('.')), 'fetch_resources.bat'),
                      os.path.join(os.path.dirname(get_resource_path('.')), 'scripts', 'fetch_resources.bat')]
        for c in candidates:
            if os.path.exists(c):
                try:
                    result = subprocess.run([c], capture_output=True, text=True, timeout=timeout, shell=True)
                    return True, result.stdout + '\n' + result.stderr
                except Exception as e:
                    return False, str(e)
        return False, 'fetch_resources.bat not found'
    except Exception as e:
        return False, str(e)

def extract_archive(file_path, target_dir):
    """
    Extracts zip, rar, or 7z files using 7-Zip CLI.
    """
    # We will assume 7za.exe is in the same directory or bundled
    seven_zip_path = get_resource_path("7za.exe")
    
    if not os.path.exists(seven_zip_path):
        # Fallback for dev if not bundled yet
        seven_zip_path = "7za.exe" 

    ext = os.path.splitext(file_path)[1].lower()

    # 1) Handle ZIP natively
    if ext == '.zip':
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.extractall(target_dir)
            return True, None
        except Exception as e:
            return False, f"zipfile error: {e}"

    # 2) Try Python libraries for rar/7z if available
    if ext == '.7z':
        try:
            import py7zr
            try:
                with py7zr.SevenZipFile(file_path, mode='r') as archive:
                    archive.extractall(path=target_dir)
                return True, None
            except Exception as e:
                # fall through to external 7za
                py7zr_err = str(e)
        except Exception:
            py7zr_err = None

    if ext == '.rar':
        try:
            import rarfile
            try:
                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(path=target_dir)
                return True, None
            except Exception as e:
                rarfile_err = str(e)
        except Exception:
            rarfile_err = None

    # 3) Fallback to external 7za.exe — if missing, try to run fetch_resources.bat
    seven_err = None
    try:
        if not os.path.exists(seven_zip_path):
            # try project-local resources folder
            proj_res = os.path.join(os.path.dirname(get_resource_path('.')), 'resources', '7za.exe')
            if os.path.exists(proj_res):
                seven_zip_path = proj_res
        if not os.path.exists(seven_zip_path):
            # try to auto-fetch resources via helper script
            ok, out = try_run_fetch_resources()
            if ok:
                # try again from resources
                proj_res = os.path.join(os.path.dirname(get_resource_path('.')), 'resources', '7za.exe')
                if os.path.exists(proj_res):
                    seven_zip_path = proj_res

        cmd = [seven_zip_path, "x", file_path, f"-o{target_dir}", "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, None
        seven_err = result.stderr or result.stdout
    except FileNotFoundError:
        seven_err = "7za executable not found"
    except Exception as e:
        seven_err = str(e)

    # 4) If RAR specifically, try unrar.exe as last resort
    if ext == '.rar':
        unrar_path = get_resource_path("unrar.exe")
        if not os.path.exists(unrar_path):
            # try project resources
            proj_unrar = os.path.join(os.path.dirname(get_resource_path('.')), 'resources', 'unrar.exe')
            if os.path.exists(proj_unrar):
                unrar_path = proj_unrar
            else:
                # try to auto-fetch resources
                ok, out = try_run_fetch_resources()
                if ok and os.path.exists(proj_unrar):
                    unrar_path = proj_unrar
                else:
                    unrar_path = "unrar.exe"

        try:
            # Use syntax: unrar x -y <archive> <output_dir>
            cmd2 = [unrar_path, "x", "-y", file_path, target_dir]
            res2 = subprocess.run(cmd2, capture_output=True, text=True)
            if res2.returncode == 0:
                return True, None
            unrar_err = res2.stderr or res2.stdout
        except FileNotFoundError:
            unrar_err = "unrar executable not found"
        except Exception as e:
            unrar_err = str(e)

        # Build combined error message
        parts = []
        if 'rarfile_err' in locals() and rarfile_err:
            parts.append(f"rarfile: {rarfile_err}")
        if 'py7zr_err' in locals() and py7zr_err:
            parts.append(f"py7zr: {py7zr_err}")
        parts.append(f"7za: {seven_err}")
        parts.append(f"unrar: {unrar_err}")
        return False, "\n".join(parts)

    # If we reach here, non-rar extraction failed
    parts = []
    if ext == '.7z' and 'py7zr_err' in locals() and py7zr_err:
        parts.append(f"py7zr: {py7zr_err}")
    parts.append(f"7za: {seven_err}")
    return False, "\n".join(parts)

def check_for_update(github_repo_url, current_version, timeout=5):
    """
    Check GitHub latest release for updates. github_repo_url can be a repo URL
    like https://github.com/owner/repo or a full release URL. Returns tuple:
    (is_newer: bool, latest_tag: str or None, html_url: str or None, error: str or None)
    """
    try:
        # Extract owner/repo
        parts = github_repo_url.rstrip('/').split('/')
        if len(parts) < 2:
            return False, None, None, "Invalid GitHub URL"

        owner = parts[-2]
        repo = parts[-1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

        req = urllib.request.Request(api_url, headers={"User-Agent": "SCT-Update-Checker"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return False, None, None, f"HTTP {resp.status}"
            data = json.loads(resp.read().decode('utf-8'))
            tag = data.get('tag_name') or data.get('name')
            html_url = data.get('html_url')

            if not tag:
                return False, None, None, "No tag found"

            # Normalize versions by stripping leading 'v' and whitespace
            def norm(v):
                return v.strip().lstrip('vV')

            def compare_versions(a, b):
                """Return -1 if a<b, 0 if equal, 1 if a>b."""
                try:
                    # split by dots and compare integer parts when possible
                    pa = [int(x) if x.isdigit() else x for x in a.split('.')]
                    pb = [int(x) if x.isdigit() else x for x in b.split('.')]
                    for xa, xb in zip(pa, pb):
                        if xa == xb:
                            continue
                        # numeric vs numeric
                        if isinstance(xa, int) and isinstance(xb, int):
                            return -1 if xa < xb else 1
                        # fallback to string compare
                        return -1 if str(xa) < str(xb) else 1
                    # all equal so far; longer one is greater
                    if len(pa) == len(pb):
                        return 0
                    return -1 if len(pa) < len(pb) else 1
                except Exception:
                    # final fallback
                    if a == b:
                        return 0
                    return -1 if a < b else 1

            try:
                cur = norm(current_version)
                latest = norm(tag)
                cmp = compare_versions(cur, latest)
                if cmp < 0:
                    return True, latest, html_url, None
                else:
                    return False, latest, html_url, None
            except Exception:
                return False, latest, html_url, None

    except urllib.error.URLError as e:
        return False, None, None, str(e)
    except socket.timeout:
        return False, None, None, "Timeout"
    except Exception as e:
        return False, None, None, str(e)

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
