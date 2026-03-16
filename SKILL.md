---
name: ig-story
description: Post atau schedule konten ke Instagram Story via Repliz API. User bisa kirim gambar/video langsung ke Telegram, bot upload ke ImgBB lalu post ke story IG. Triggered by /story command atau user kirim media ke bot.
---

# IG Story Skill — Post ke Instagram Story

## Command trigger

Skill ini HANYA aktif jika ada kata kunci berikut dalam pesan atau caption:

| Trigger | Contoh |
|---|---|
| `/story` | `/story` |
| `/story jam X` | `/story jam 15:00` |
| `/story besok jam X` | `/story besok jam 09:00` |
| caption gambar/video berisi `story` | kirim foto + caption `story jam 15:00` |
| "post ke story" | "post ke story IG ini" |
| "upload story" | "upload story besok jam 9" |

**Jika user kirim gambar/video TANPA kata kunci di atas → JANGAN gunakan skill ini.**

## Workflow

### 1. Terima media dari Telegram

Ketika user kirim gambar atau video ke chat:
- Telegram menyimpan file ke disk lokal (biasanya di `/tmp/` atau path tools)
- Baca path file dari tool result

Jika user hanya kirim URL (bukan file), lanjut ke langkah 2b.

### 2a. Upload file lokal ke ImgBB

```bash
python3 /root/.openclaw/skills/ig-story/scripts/upload_imgbb.py --file "/path/to/file.jpg"
```

Output: `{ "success": true, "url": "https://i.ibb.co/..." }`

### 2b. Upload dari URL ke ImgBB (jika user kirim URL)

```bash
python3 /root/.openclaw/skills/ig-story/scripts/upload_imgbb.py --url "https://example.com/image.jpg"
```

### 3. Konversi waktu ke ISO8601 Asia/Jakarta

- Jika tidak ada waktu → jadwal 1 menit dari sekarang
- "jam 15:00" → `2026-03-16T15:00:00+07:00`
- "besok jam 09:00" → besok tanggal ISO `T09:00:00+07:00`

### 4. Post ke Instagram Story via Repliz

```bash
python3 /root/.openclaw/skills/ig-story/scripts/post_story.py \
  --url "https://i.ibb.co/..." \
  --type "image" \
  --schedule "2026-03-16T15:00:00+07:00"
```

Untuk video:
```bash
python3 /root/.openclaw/skills/ig-story/scripts/post_story.py \
  --url "https://i.ibb.co/video.mp4" \
  --type "video" \
  --thumb "https://i.ibb.co/thumb.jpg" \
  --schedule "2026-03-16T15:00:00+07:00"
```

### 5. Balas ke user

Jika berhasil:
```
✅ Story IG dijadwalkan!
📅 Waktu: <jam WIB>
```

Jika gagal upload ImgBB:
```
❌ Gagal upload media. Coba kirim ulang gambarnya.
```

Jika gagal post Repliz:
```
❌ Gagal jadwalkan story. Error: <pesan>
```

### 6. Simpan ke state

```python
import json, datetime
state_path = "/root/.openclaw/skills/ig-story/state/history.json"
try:
    with open(state_path) as f:
        state = json.load(f)
except FileNotFoundError:
    state = {"history": []}

state["history"] = ([{
    "url": "<imgbb_url>",
    "type": "<image|video>",
    "schedule_at": "<ISO8601>",
    "posted_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
}] + state["history"])[:20]

with open(state_path, "w") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
```

## Catatan

- ImgBB API key: tersimpan di `scripts/upload_imgbb.py`
- Account ID Instagram diambil dari `/root/autopost-threads/config.json` → `accounts.instagram`
- Format didukung: JPG, PNG, MP4
- Rasio ideal story IG: 9:16 (1080×1920px)
