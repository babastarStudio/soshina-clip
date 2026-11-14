#!/usr/bin/env python3
"""PC側で実行する：元動画（720p）・日本語字幕・動画情報をまとめてダウンロード

使い方（PCの作業フォルダで）:
  python3 pc_fetch.py URL [URL ...]

必要なもの: yt-dlp（最新版）, deno, ffmpeg
保存先: ./sources/<動画ID>/ に video.mp4, *.vtt, info.json
"""
import json, os, subprocess, sys

def run(url, base):
    common = ["yt-dlp", "--no-playlist", "--remote-components", "ejs:github"]
    # 動画情報だけ先に取得してIDを決める
    info = json.loads(subprocess.run(common + ["-J", "--skip-download", url],
                                     capture_output=True, text=True, check=True).stdout)
    vid = info["id"]
    d = os.path.join(base, vid)
    os.makedirs(d, exist_ok=True)
    keep = {k: info.get(k) for k in ("id", "title", "channel", "upload_date", "duration",
                                     "view_count", "webpage_url", "chapters", "heatmap")}
    json.dump(keep, open(os.path.join(d, "info.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    subprocess.run(common + [
        "-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720]/b",
        "--merge-output-format", "mp4",
        "--write-subs", "--write-auto-subs", "--sub-langs", "ja,ja-orig", "--sub-format", "vtt",
        "-o", os.path.join(d, "video.%(ext)s"), url], check=True)
    print(f"OK: {vid} {info.get('title')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = os.path.join(os.getcwd(), "sources")
    for u in sys.argv[1:]:
        try:
            run(u, base)
        except subprocess.CalledProcessError as e:
            print(f"NG: {u} ({e})")
