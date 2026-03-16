#!/usr/bin/env python3
"""
Post atau schedule Instagram Story via Repliz API.

Usage:
  python3 post_story.py --url <media_url> [--type image|video] [--thumb <thumb_url>] [--schedule <ISO8601>]

Examples:
  python3 post_story.py --url https://storage.repliz.com/image.png
  python3 post_story.py --url https://storage.repliz.com/video.mp4 --type video --thumb https://storage.repliz.com/thumb.png
  python3 post_story.py --url https://storage.repliz.com/image.png --schedule 2026-03-16T15:00:00+07:00
"""

import sys
import json
import argparse
import base64
from datetime import datetime, timedelta, timezone
from urllib import request, error


CONFIG_PATH = "/root/autopost-threads/config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def iso_in(minutes: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def post_story(media_url: str, media_type: str = "image", thumbnail: str = None, schedule_at: str = None) -> dict:
    config = load_config()
    access_key = config["access_key"]
    secret_key = config["secret_key"]
    base_url = config["base_url"].rstrip("/")
    account_id = config["accounts"]["instagram"]

    if not thumbnail:
        thumbnail = media_url  # fallback: pakai URL yang sama

    payload = {
        "title": "",
        "description": "",
        "type": "story",
        "medias": [
            {
                "type": media_type,
                "thumbnail": thumbnail,
                "url": media_url,
            }
        ],
        "scheduleAt": schedule_at or iso_in(1),
        "accountId": account_id,
    }

    body = json.dumps(payload).encode("utf-8")
    token = base64.b64encode(f"{access_key}:{secret_key}".encode()).decode()

    req = request.Request(
        url=f"{base_url}/schedule",
        data=body,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Basic {token}")

    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = resp.getcode()
    except error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        code = e.code

    try:
        decoded = json.loads(raw) if raw else {}
    except Exception:
        decoded = {"raw": raw}

    return {
        "success": 200 <= code < 300,
        "http_code": code,
        "schedule_at": payload["scheduleAt"],
        "account_id": account_id,
        "response": decoded,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL media (image/video)")
    parser.add_argument("--type", default="image", choices=["image", "video"], help="Tipe media")
    parser.add_argument("--thumb", default=None, help="URL thumbnail (untuk video)")
    parser.add_argument("--schedule", default=None, help="Waktu post ISO8601 (default: 1 menit)")
    args = parser.parse_args()

    result = post_story(
        media_url=args.url,
        media_type=args.type,
        thumbnail=args.thumb,
        schedule_at=args.schedule,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
