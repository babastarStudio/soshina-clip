#!/usr/bin/env python3
"""PC側で実行する：元動画（720p）・日本語字幕・動画情報をまとめてダウンロード

使い方（PCの作業フォルダで）:
  python3 pc_fetch.py URL [URL ...]
  python3 pc_fetch.py --dest "G:/マイドライブ/soshina-clip/sources" URL ...

必要なもの: yt-dlp（最新版）, deno, ffmpeg
保存先: --dest（省略時は config.env の PC_SOURCES_DIR、それも空なら ./sources）の
        <動画ID>/ に video.mp4, *.vtt, info.json
--dest をパソコン版Googleドライブの「soshina-clip/sources」にすると、そのままクラウドへ渡る
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

def config_dest():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("PC_SOURCES_DIR="):
                return line.split("=", 1)[1].strip().strip('"')
    return ""


if __name__ == "__main__":
    args = sys.argv[1:]
    base = config_dest() or os.path.join(os.getcwd(), "sources")
    if args[:1] == ["--dest"] and len(args) >= 2:
        base, args = args[1], args[2:]
    if not args:
        sys.exit(__doc__)
    for u in args:
        try:
            run(u, base)
        except subprocess.CalledProcessError as e:
            print(f"NG: {u} ({e})")
