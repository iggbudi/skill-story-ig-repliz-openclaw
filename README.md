# ig-story — OpenClaw Skill

Skill untuk post atau schedule konten ke **Instagram Story** via [Repliz](https://repliz.com), dengan upload media otomatis ke **ImgBB**.

## Cara kerja

1. User kirim gambar/video ke bot Telegram dengan caption `story` atau `/story`
2. Bot upload media ke ImgBB → dapat URL publik
3. Bot post URL ke Repliz → terjadwal ke Instagram Story

## Setup

### 1. Salin skill ke OpenClaw

Letakkan folder ini di:
```
~/.openclaw/skills/ig-story/
```

### 2. Set API key ImgBB

Edit `scripts/upload_imgbb.py`, ganti:
```python
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "YOUR_IMGBB_API_KEY_HERE")
```

Atau set environment variable:
```bash
export IMGBB_API_KEY=your_api_key_here
```

Daftar gratis di [imgbb.com](https://imgbb.com) → Account → API.

### 3. Set kredensial Repliz

Pastikan file `/root/autopost-threads/config.json` berisi:
```json
{
  "access_key": "YOUR_REPLIZ_ACCESS_KEY",
  "secret_key": "YOUR_REPLIZ_SECRET_KEY",
  "base_url": "https://api.repliz.com/public",
  "accounts": {
    "instagram": "YOUR_INSTAGRAM_ACCOUNT_ID"
  }
}
```

## Trigger command (Telegram)

| Pesan | Aksi |
|-------|------|
| Kirim foto + caption `story` | Post segera |
| Kirim foto + caption `story jam 15:00` | Jadwalkan jam 15:00 WIB |
| Kirim foto + caption `story besok jam 09:00` | Jadwalkan besok jam 09:00 |
| `/story` | Post foto yang baru dikirim |

## Struktur file

```
ig-story/
├── SKILL.md                  ← instruksi untuk OpenClaw agent
├── README.md
├── scripts/
│   ├── upload_imgbb.py       ← upload media ke ImgBB
│   └── post_story.py         ← post story ke Repliz
└── state/                    ← diabaikan git (lokal saja)
    └── history.json
```

## Dependensi

- Python 3.11+
- Tidak ada library eksternal (pure stdlib)
