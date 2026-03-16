#!/usr/bin/env python3
"""
Upload image ke ImgBB, return URL publik.

Usage:
  python3 upload_imgbb.py --file /path/to/image.jpg
  python3 upload_imgbb.py --url https://example.com/image.jpg

Output JSON: { "success": true, "url": "https://i.ibb.co/...", "delete_url": "..." }
"""

import sys
import json
import argparse
import base64
import os
from urllib import request, parse, error

# Set via environment variable IMGBB_API_KEY atau ganti langsung di sini

IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "YOUR_IMGBB_API_KEY_HERE")
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"


def upload_file(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    payload = parse.urlencode({
        "key": IMGBB_API_KEY,
        "image": image_data,
        "name": os.path.basename(file_path),
    }).encode("utf-8")

    req = request.Request(IMGBB_UPLOAD_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            code = resp.getcode()
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        code = e.code

    try:
        decoded = json.loads(raw)
    except Exception:
        return {"success": False, "error": raw}

    if 200 <= code < 300 and decoded.get("success"):
        return {
            "success": True,
            "url": decoded["data"]["url"],
            "display_url": decoded["data"].get("display_url", ""),
            "delete_url": decoded["data"].get("delete_url", ""),
        }
    else:
        return {"success": False, "error": decoded}


def upload_from_url(source_url: str) -> dict:
    """Download dari URL lalu upload ke ImgBB."""
    import tempfile, urllib.request as ur
    suffix = os.path.splitext(source_url.split("?")[0])[-1] or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
    try:
        ur.urlretrieve(source_url, tmp_path)
        return upload_file(tmp_path)
    finally:
        os.unlink(tmp_path)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path file lokal")
    group.add_argument("--url", help="URL gambar untuk di-upload ulang ke ImgBB")
    args = parser.parse_args()

    if args.file:
        result = upload_file(args.file)
    else:
        result = upload_from_url(args.url)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
