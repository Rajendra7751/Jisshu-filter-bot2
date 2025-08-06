import os
import requests

PIXELDRAIN_KEY = os.getenv("PIXELDRAIN_KEY")
UPLOAD_URL = "https://pixeldrain.com/api/file"

def upload_file(filepath, filename=None, progress_cb=None):
    total_size = os.path.getsize(filepath)
    with open(filepath, "rb") as f:
        files = {'file': (filename or os.path.basename(filepath), f)}
        headers = {"Authorization": f"Bearer {PIXELDRAIN_KEY}"} if PIXELDRAIN_KEY else {}
        response = requests.post(UPLOAD_URL, files=files, headers=headers)
    res = response.json()
    if not res.get("success"):
        raise Exception(res.get("message", "Unknown PixelDrain error"))
    return res["id"]
