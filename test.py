import requests
import zipfile
import shutil
import time
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
VERSION_URL = "https://shrey113.github.io/all_app_updates/version.json"
APP_NAME = "Adb-Device-Manager"

BASE_DIR = Path.home() / "ADBDeviceManager"
ZIP_DIR = BASE_DIR / "downloads"
TOOLS_DIR = BASE_DIR / "tools"

ZIP_DIR.mkdir(parents=True, exist_ok=True)
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# FETCH VERSION JSON
# =========================================================
print("🔍 Checking for updates...")

resp = requests.get(VERSION_URL, timeout=15)
resp.raise_for_status()

json_data = resp.json()
if APP_NAME not in json_data:
    raise RuntimeError(f"❌ App '{APP_NAME}' not found in version.json")

data = json_data[APP_NAME]

zip_url = data["download_url"]
zip_name = data["zip_name"]
extract_name = data["after_extract_name"]
exe_rel_path = data["after_extract_exe_path"].replace("./", "")

zip_path = ZIP_DIR / zip_name
final_extract_dir = TOOLS_DIR / extract_name

# =========================================================
# DOWNLOAD ZIP WITH PROGRESS
# =========================================================
print("⬇ Downloading update...")

start_time = time.time()
downloaded = 0

with requests.get(zip_url, stream=True, timeout=30) as r:
    r.raise_for_status()
    total = int(r.headers.get("Content-Length", 0))

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                continue

            f.write(chunk)
            downloaded += len(chunk)

            elapsed = time.time() - start_time
            speed = (downloaded / elapsed) / 1024 if elapsed > 0 else 0
            percent = (downloaded / total) * 100 if total else 0

            print(
                f"\r{percent:6.2f}% | "
                f"{downloaded // (1024*1024)}MB | "
                f"{speed:7.1f} KB/s",
                end=""
            )

print("\n✔ Download completed")

# =========================================================
# EXTRACT ZIP SAFELY
# =========================================================
print("📦 Extracting...")

temp_dir = TOOLS_DIR / "__temp_extract__"
if temp_dir.exists():
    shutil.rmtree(temp_dir)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(temp_dir)

# =========================================================
# FIX DOUBLE-FOLDER ZIP STRUCTURE
# =========================================================
inner_dirs = [p for p in temp_dir.iterdir() if p.is_dir()]

# If ZIP has a single root folder → flatten it
source_dir = inner_dirs[0] if len(inner_dirs) == 1 else temp_dir

if final_extract_dir.exists():
    shutil.rmtree(final_extract_dir)

shutil.move(str(source_dir), final_extract_dir)
shutil.rmtree(temp_dir)

# =========================================================
# FINAL VALIDATION
# =========================================================
exe_path = final_extract_dir / exe_rel_path

if not exe_path.exists():
    raise RuntimeError(f"❌ Executable not found:\n{exe_path}")

# =========================================================
# SUCCESS
# =========================================================
print("✅ Update installed successfully")
print(f"📂 Installed at : {final_extract_dir}")
print(f"▶ Executable   : {exe_path}")
