# 見本動画を暗号化して置き場に追加する
# 使い方: python3 tools/add_video.py <動画.mp4> "<タイトル>" <日付YYYY-MM-DD>
# 合言葉は環境変数 MIHON_PASS で渡す（ファイルに残さないため）
import json, os, sys, base64, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "videos.json")
CHUNK = 15 * 1024 * 1024  # GitHubのWebアップロード上限(25MB)未満に分割
ITER = 250000
CHECK_TEXT = b"mihon-ok"

b64 = lambda b: base64.b64encode(b).decode()

def main():
    src, title, date = sys.argv[1], sys.argv[2], sys.argv[3]
    pw = os.environ["MIHON_PASS"].encode("utf-8")

    if os.path.exists(META):
        meta = json.load(open(META, encoding="utf-8"))
        salt = base64.b64decode(meta["salt"])
    else:
        salt = os.urandom(16)
        meta = {"salt": b64(salt), "iter": ITER, "videos": []}
    key = hashlib.pbkdf2_hmac("sha256", pw, salt, meta["iter"], 32)
    aes = AESGCM(key)

    if "check" in meta:  # 既存の合言葉と一致するか確認
        aes.decrypt(base64.b64decode(meta["check"]["iv"]), base64.b64decode(meta["check"]["data"]), None)
    else:
        iv = os.urandom(12)
        meta["check"] = {"iv": b64(iv), "data": b64(aes.encrypt(iv, CHECK_TEXT, None))}

    vid = "v%02d" % (len(meta["videos"]) + 1)
    iv = os.urandom(12)
    enc = aes.encrypt(iv, open(src, "rb").read(), None)
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    parts = []
    for i in range(0, len(enc), CHUNK):
        name = "data/%s.%d.bin" % (vid, i // CHUNK)
        open(os.path.join(ROOT, name), "wb").write(enc[i:i + CHUNK])
        parts.append(name)

    meta["videos"].append({"id": vid, "title": title, "date": date, "iv": b64(iv), "size": len(enc), "parts": parts})
    json.dump(meta, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(vid, len(enc), parts)

main()
