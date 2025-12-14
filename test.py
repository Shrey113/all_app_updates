import requests
import zipfile
import shutil
import time
from pathlib import Path

# ---------------- CONFIG ----------------
VERSION_URL = "https://shrey113.github.io/all_app_updates/version.json"
APP_NAME = "Adb-Device-Manager"

BASE_DIR = Path.home() / "ADBDeviceManager"
ZIP_DIR = BASE_DIR / "downloads"
TOOLS_DIR = BASE_DIR / "tools"

ZIP_DIR.mkdir(parents=True, exist_ok=True)
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- FETCH VERSION ----------------
resp = requests.get(VERSION_URL, timeout=15)
resp.raise_for_status()
data = resp.json()[APP_NAME]

zip_url = data["download_url"]
zip_name = data["zip_name"]
expected_size = data["size"]
extract_name = data["after_extract_name"]
exe_rel_path = data["after_extract_exe_path"]

zip_path = ZIP_DIR / zip_name
extract_base = TOOLS_DIR / extract_name

# ---------------- DOWNLOAD ZIP (WITH PROGRESS) ----------------
print("⬇ Downloading update...")

start_time = time.time()
downloaded = 0

with requests.get(zip_url, stream=True, timeout=30) as r:
    r.raise_for_status()
    total = int(r.headers.get("Content-Length", expected_size))

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                continue

            f.write(chunk)
            downloaded += len(chunk)

            elapsed = time.time() - start_time
            speed = downloaded / elapsed / 1024 if elapsed > 0 else 0
            percent = (downloaded / total) * 100

            print(
                f"\r{percent:5.1f}% | "
                f"{downloaded // (1024*1024)}MB / {total // (1024*1024)}MB | "
                f"{speed:6.1f} KB/s",
                end=""
            )

print("\n✔ Download complete")

# ---------------- VERIFY SIZE ----------------
if zip_path.stat().st_size != expected_size:
    raise RuntimeError("❌ ZIP size mismatch – download corrupted")

# ---------------- EXTRACT ZIP ----------------
print("📦 Extracting...")

temp_extract = TOOLS_DIR / "__temp_extract__"
if temp_extract.exists():
    shutil.rmtree(temp_extract)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(temp_extract)

# ---------------- FIX DOUBLE FOLDER ISSUE ----------------
inner_dirs = [p for p in temp_extract.iterdir() if p.is_dir()]

if len(inner_dirs) == 1:
    inner_root = inner_dirs[0]
else:
    inner_root = temp_extract

if extract_base.exists():
    shutil.rmtree(extract_base)

shutil.move(str(inner_root), extract_base)
shutil.rmtree(temp_extract)

# ---------------- FINAL VALIDATION ----------------
final_exe = extract_base / exe_rel_path.replace("./", "")
if not final_exe.exists():
    raise RuntimeError(f"❌ Expected exe not found: {final_exe}")

print("✅ Update installed successfully")
print(f"📂 Tool path : {extract_base}")
print(f"▶ Executable: {final_exe}")
