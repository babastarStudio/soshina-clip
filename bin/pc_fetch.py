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
import json, os, re, subprocess, sys, time

BASE = None
COMMENT_ARGS = ["--get-comments", "--extractor-args", "youtube:max_comments=300,all,0,0;comment_sort=top"]
TS = re.compile(r"(?<!\d)(\d{1,2}):([0-5]\d)(?::([0-5]\d))?(?!\d)")


def fetch_info(url, d, common):
    """info.json（heatmap 含む）と comments.json（上位コメント）を書く。heatmap の有無を返す"""
    info = json.loads(subprocess.run(common + ["-J", "--skip-download", *COMMENT_ARGS, url],
                                     capture_output=True, text=True, check=True).stdout)
    vid = info["id"]
    d = d or os.path.join(BASE, vid)
    os.makedirs(d, exist_ok=True)
    keep = {k: info.get(k) for k in ("id", "title", "channel", "upload_date", "duration",
                                     "view_count", "comment_count", "webpage_url", "chapters", "heatmap")}
    ver = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True).stdout.strip()
    keep["fetched"] = {"at": time.strftime("%Y-%m-%d %H:%M"), "yt_dlp": ver,
                       "heatmap_points": len(info.get("heatmap") or []),
                       "comments": len(info.get("comments") or [])}
    json.dump(keep, open(os.path.join(d, "info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 場面探し用：いいね順の上位コメント。時刻（例 17:10）を含むものに印をつける
    cs = []
    for c in info.get("comments") or []:
        if c.get("parent", "root") != "root":
            continue
        t = c.get("text") or ""
        stamps = [int(h) * 3600 + int(m) * 60 + int(x) if x else int(h) * 60 + int(m)
                  for h, m, x in TS.findall(t)]
        cs.append({"likes": c.get("like_count") or 0, "text": t, "stamps": stamps})
    cs.sort(key=lambda c: -c["likes"])
    json.dump(cs[:300], open(os.path.join(d, "comments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hm = bool(info.get("heatmap"))
    print(f"  info: heatmap {'あり' if hm else 'なし'} / コメント {len(cs)} 件 / 時刻つき {sum(1 for c in cs if c['stamps'])} 件")
    return vid, d, hm


def run(url, base):
    common = ["yt-dlp", "--no-playlist", "--remote-components", "ejs:github"]
    vid, d, _ = fetch_info(url, None, common)
    subprocess.run(common + [
        "-f", "bv*[height<=720][vcodec^=avc1]+ba[ext=m4a]/bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720]/b",
        "--merge-output-format", "mp4",
        "--write-subs", "--write-auto-subs", "--sub-langs", "ja,ja-orig", "--sub-format", "vtt",
        "-o", os.path.join(d, "video.%(ext)s"), url], check=True)
    print(f"OK: {vid}")


def refresh_info(url, d):
    """取得済みでも heatmap が無ければ、情報だけ取り直す（新しい動画は後から付くことがある）"""
    common = ["yt-dlp", "--no-playlist", "--remote-components", "ejs:github"]
    fetch_info(url, d, common)


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
    BASE = base
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
            vd = os.path.join(base, vid)
            if os.path.exists(os.path.join(vd, "video.mp4")):
                try:
                    has_hm = bool(json.load(open(os.path.join(vd, "info.json"), encoding="utf-8")).get("heatmap"))
                except (OSError, ValueError):
                    has_hm = False
                if has_hm and os.path.exists(os.path.join(vd, "comments.json")):
                    print(f"skip（取得済み）: {line}")
                else:
                    print(f"情報だけ取り直し: {line}")
                    try:
                        refresh_info(line, vd)
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        print(f"NG: {line} ({e})")
                continue
            args.append(line)
        print(f"fetch_list.txt から {len(args)} 本を取得します")
    for u in args:
        try:
            run(u, base)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"NG: {u} ({e})")
