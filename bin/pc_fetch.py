#!/usr/bin/env python3
"""PC側で実行する：元動画（720p）・日本語字幕・動画情報をまとめてダウンロード

使い方（PCの作業フォルダで）:
  python3 pc_fetch.py URL [URL ...]
  python3 pc_fetch.py --dest "G:/マイドライブ/soshina-clip/sources" URL ...
  python3 pc_fetch.py            ← URLを省くと、保存先の1つ上の fetch_list.txt を読む
                                   （クラウドの Claude がドライブ上で書く「今週取る動画」リスト）

必要なもの: yt-dlp（最新版）, deno, ffmpeg
保存先: --dest（省略時は config.env の PC_SOURCES_DIR、それも空なら ./sources）の
        <動画ID>/ に video.mp4, *.vtt, info.json
--dest をパソコン版Googleドライブの「soshina-clip/sources」にすると、そのままクラウドへ渡る
"""
import json, os, re, subprocess, sys

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
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, "fetch_list.txt")):   # ドライブの soshina-clip に置いた場合
        base = os.path.join(here, "sources")
    else:
        base = config_dest() or os.path.join(os.getcwd(), "sources")
    if args[:1] == ["--dest"] and len(args) >= 2:
        base, args = args[1], args[2:]
    if not args:
        lst = os.path.join(os.path.dirname(os.path.abspath(base)), "fetch_list.txt")
        if not os.path.exists(lst):
            sys.exit(__doc__)
        for line in open(lst, encoding="utf-8-sig"):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", line)
            vid = m.group(1) if m else line
            if os.path.exists(os.path.join(base, vid, "video.mp4")):
                print(f"skip（取得済み）: {line}")
                continue
            args.append(line)
        print(f"fetch_list.txt から {len(args)} 本を取得します")
    for u in args:
        try:
            run(u, base)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"NG: {u} ({e})")
