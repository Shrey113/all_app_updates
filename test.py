import requests
import zipfile
import io
from pathlib import Path

# ---------------- CONFIG ----------------
VERSION_URL = "https://shrey113.github.io/flutter_app_updates/version.json"
APP_NAME = "Adb-Device-Manager"

BASE_DIR = Path.home() / "ADBDeviceManager"
ZIP_DIR = BASE_DIR / "downloads"
EXTRACT_DIR = BASE_DIR / "tools"

ZIP_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- FETCH VERSION ----------------
resp = requests.get(VERSION_URL, timeout=15)
resp.raise_for_status()
data = resp.json()[APP_NAME]

zip_url = data["download_url"]
zip_name = data["zip_name"]
expected_size = data["size"]

zip_path = ZIP_DIR / zip_name

# ---------------- DOWNLOAD ZIP ----------------
print("Downloading update...")
with requests.get(zip_url, stream=True, timeout=30) as r:
    r.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# ---------------- VERIFY SIZE ----------------
actual_size = zip_path.stat().st_size
if actual_size != expected_size:
    raise RuntimeError("ZIP size mismatch – download corrupted")

# ---------------- EXTRACT ZIP ----------------
print("Extracting...")
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(EXTRACT_DIR)

print("✅ Update installed successfully")
print(f"📂 Location: {EXTRACT_DIR}")
