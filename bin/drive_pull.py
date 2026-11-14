#!/usr/bin/env python3
"""クラウド側：Googleドライブの元動画を sources/<ID>/ に取り込む

使い方:
  python3 bin/drive_pull.py <動画ID> video.mp4=<ファイルID> [video.ja.vtt=<ファイルID> ...]

ファイルIDは Claude がドライブのコネクタで soshina-clip/sources/<動画ID>/ を検索して調べる。
動画は大きくコネクタでは運べないため、リンク共有（閲覧のみ）されたファイルを直接ダウンロードする。
"""
import os, subprocess, sys

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    vid = sys.argv[1]
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sources", vid)
    os.makedirs(root, exist_ok=True)
    for pair in sys.argv[2:]:
        name, fid = pair.split("=", 1)
        out = os.path.join(root, os.path.basename(name))
        url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
        subprocess.run(["curl", "-sSfL", "--retry", "3", "-o", out, url], check=True)
        with open(out, "rb") as f:
            head = f.read(64)
        if head.lstrip().lower().startswith((b"<!doctype html", b"<html")):
            os.remove(out)
            sys.exit(f"NG: {name} を取得できません（ドライブのリンク共有がオフの可能性）")
        print(f"OK: {out} ({os.path.getsize(out) / 1e6:.1f} MB)")

if __name__ == "__main__":
    main()
