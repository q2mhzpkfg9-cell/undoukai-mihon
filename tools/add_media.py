# 見本動画・音源を置き場に追加する（合言葉なし版）
# 使い方: python3 tools/add_media.py <ファイル> "<タイトル>" <日付YYYY-MM-DD>
# 拡張子から動画/音源を判定して media/ にコピーし、videos.json に登録する
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "videos.json")
AUDIO_EXT = {".m4a", ".mp3", ".wav", ".aac"}

def main():
    src, title, date = sys.argv[1], sys.argv[2], sys.argv[3]
    ext = os.path.splitext(src)[1].lower()
    is_audio = ext in AUDIO_EXT

    meta = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else {"audios": [], "videos": []}
    meta.setdefault("audios", []); meta.setdefault("videos", [])
    bucket = meta["audios"] if is_audio else meta["videos"]
    mid = ("a%02d" if is_audio else "v%02d") % (len(bucket) + 1)

    os.makedirs(os.path.join(ROOT, "media"), exist_ok=True)
    rel = "media/%s%s" % (mid, ext)
    shutil.copy(src, os.path.join(ROOT, rel))

    bucket.append({"id": mid, "title": title, "date": date, "src": rel})
    json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(mid, rel)

main()
