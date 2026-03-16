#!/usr/bin/env python3
"""
Upload image atau video ke Cloudinary, return URL publik.

Usage:
  python3 upload_cloudinary.py --file /path/to/media.jpg
  python3 upload_cloudinary.py --file /path/to/video.mp4
  python3 upload_cloudinary.py --file /path/to/video.mp4 --thumb

Output JSON:
  { "success": true, "url": "https://res.cloudinary.com/...", "type": "image|video", "thumbnail": "..." }
"""

import sys
import json
import argparse
import os
import hashlib
import time
import mimetypes
from urllib import request, parse, error
from urllib.request import Request

# Load .env jika ada
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "YOUR_CLOUD_NAME")
API_KEY    = os.environ.get("CLOUDINARY_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "YOUR_API_SECRET")


def detect_type(file_path: str) -> str:
    mime, _ = mimetypes.guess_type(file_path)
    if mime and mime.startswith("video"):
        return "video"
    return "image"


def make_signature(params: dict, api_secret: str) -> str:
    """Generate Cloudinary API signature."""
    sorted_params = "&".join(
        f"{k}={v}" for k, v in sorted(params.items()) if k not in ("file", "api_key")
    )
    to_sign = sorted_params + api_secret
    return hashlib.sha1(to_sign.encode("utf-8")).hexdigest()


def upload_file(file_path: str, generate_thumb: bool = False) -> dict:
    resource_type = detect_type(file_path)
    timestamp = str(int(time.time()))

    params = {
        "timestamp": timestamp,
        "folder": "openclaw",
    }

    signature = make_signature(params, API_SECRET)

    # Build multipart form
    boundary = "----CloudinaryBoundary" + timestamp

    with open(file_path, "rb") as f:
        file_data = f.read()

    filename = os.path.basename(file_path)

    body_parts = []
    for key, val in {**params, "api_key": API_KEY, "signature": signature}.items():
        body_parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{val}\r\n".encode()
        )

    body_parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode()
        + file_data
        + b"\r\n"
    )
    body_parts.append(f"--{boundary}--\r\n".encode())

    body = b"".join(body_parts)

    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/{resource_type}/upload"
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            code = resp.getcode()
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        code = e.code

    try:
        decoded = json.loads(raw)
    except Exception:
        return {"success": False, "error": raw}

    if not (200 <= code < 300) or decoded.get("error"):
        return {"success": False, "error": decoded.get("error", decoded)}

    media_url = decoded.get("secure_url", "")

    # Generate thumbnail URL for video
    thumbnail = media_url
    if resource_type == "video":
        # Cloudinary auto-generates thumbnail: change extension to jpg and add /so_0/
        public_id = decoded.get("public_id", "")
        thumbnail = f"https://res.cloudinary.com/{CLOUD_NAME}/video/upload/so_0/{public_id}.jpg"

    return {
        "success": True,
        "url": media_url,
        "type": resource_type,
        "thumbnail": thumbnail,
        "public_id": decoded.get("public_id", ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path file lokal (image atau video)")
    parser.add_argument("--thumb", action="store_true", help="Generate thumbnail (untuk video)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(json.dumps({"success": False, "error": f"File tidak ditemukan: {args.file}"}))
        sys.exit(1)

    result = upload_file(args.file, generate_thumb=args.thumb)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
