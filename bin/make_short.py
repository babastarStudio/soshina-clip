#!/usr/bin/env python3
"""粗品切り抜き Shorts 型A（黒背景）書き出しスクリプト

使い方:
  python3 make_short.py --src clip.mp4 --out out.mp4 \
      --header "日本一のツッコミで殴られた粗品" \
      --source-title "タクシーの運転手に殴られた" \
      [--start 0 --end 12] [--speed 1.1] [--subs subs.json] [--split 9] [--label やられる粗品]

subs.json は元クリップの時刻で [{"s":0.5,"e":2.0,"t":"1-2-4やないかぇー！"}, ...]
"""
import argparse, json, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
VID_Y = 660           # 元動画を置くY座標（16:9 → 1080x608）
FONT_DIRS = ["/usr/share/fonts/opentype/noto", "/System/Library/Fonts", "C:/Windows/Fonts"]

def load_config():
    cfg = {}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k] = v.strip().strip('"')
    return cfg


CFG = load_config()
YELLOW = CFG.get("ACCENT_COLOR", "#ffd400")


def font(weight, size):
    names = {"black": ["NotoSansCJK-Black.ttc", "ヒラギノ角ゴシック W9.ttc", "YuGothB.ttc"],
             "bold": ["NotoSansCJK-Bold.ttc", "ヒラギノ角ゴシック W6.ttc", "YuGothB.ttc"],
             "medium": ["NotoSansCJK-Medium.ttc", "ヒラギノ角ゴシック W4.ttc", "YuGothM.ttc"]}[weight]
    names = names + ["NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc"]  # 太さが無い環境での代替
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size, index=0)
    raise SystemExit("日本語フォントが見つかりません")


def ctext(d, y, t, f, fill, stroke=0):
    w = d.textlength(t, font=f)
    d.text(((W - w) / 2, y), t, font=f, fill=fill, stroke_width=stroke, stroke_fill="black")


def split_header(text, split=None):
    """2行に分割。split 指定がなければ「〜な粗品」部分が2行目に来るよう後ろから区切る"""
    if split is not None:
        return text[:split], text[split:]
    if len(text) <= 10:
        return "", text
    for tail in ("な粗品", "る粗品", "た粗品", "粗品"):
        if text.endswith(tail):
            break
    cut = max(len(text) - 10, len(text) // 2)
    for p in ("で", "が", "に", "を", "は", "と", "も"):  # 助詞の直後で切る
        i = text.rfind(p, 0, len(text) - 3)
        if i >= 0 and len(text) - (i + 1) <= 10 and i + 1 <= 11:
            cut = i + 1
            break
    return text[:cut], text[cut:]


def overlay_png(path, header, source_title, split, label):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tag, ft = label, font("bold", 34)
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([(W - tw) / 2 - 24, 250, (W + tw) / 2 + 24, 310], radius=30, fill=YELLOW)
    d.text(((W - tw) / 2, 254), tag, font=ft, fill="black")
    l1, l2 = split_header(header, split)
    fh = font("black", 84)
    for line in (l1, l2):
        if d.textlength(line, font=fh) > 1000:
            raise SystemExit(f"ヘッダーの1行が長すぎます: {line}（10文字目安）")
    if l1:
        ctext(d, 360, l1, fh, "white", 6)
    ctext(d, 470 if l1 else 415, l2, fh, YELLOW, 6)
    if source_title:
        ctext(d, 1440, f"「{source_title}」より", font("medium", 32), "#bdbdbd")
    im.save(path)


def sub_png(path, text):
    im = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("black", 70)
    while d.textlength(text, font=f) > 860 and f.size > 44:   # 右側のボタン領域を避ける
        f = font("black", f.size - 4)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, 20), text, font=f, fill="white", stroke_width=7, stroke_fill="black")
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--header", required=True); ap.add_argument("--source-title", default="")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float)
    ap.add_argument("--speed", type=float, default=float(CFG.get("DEFAULT_SPEED", 1.0))); ap.add_argument("--subs")
    ap.add_argument("--split", type=int)
    ap.add_argument("--label", default=CFG.get("LABEL_DEFAULT", "粗品切り抜き"))
    a = ap.parse_args()

    tmp = tempfile.mkdtemp()
    ov = os.path.join(tmp, "ov.png"); overlay_png(ov, a.header, a.source_title, a.split, a.label)
    subs = json.load(open(a.subs, encoding="utf-8")) if a.subs else []

    inputs = ["-ss", str(a.start)] + (["-to", str(a.end)] if a.end else []) + ["-i", a.src, "-i", ov]
    sp = a.speed
    fc = [f"[0:v]setpts=PTS/{sp},scale=1080:-2,pad=1080:1920:0:{VID_Y}:black,setsar=1[bg]",
          "[bg][1:v]overlay=0:0[v0]"]
    last = "v0"
    for i, s in enumerate(subs):
        p = os.path.join(tmp, f"s{i}.png"); sub_png(p, s["t"])
        inputs += ["-i", p]
        st, en = (s["s"] - a.start) / sp, (s["e"] - a.start) / sp
        fc.append(f"[{last}][{i + 2}:v]overlay=0:1280:enable='between(t,{st:.3f},{en:.3f})'[v{i + 1}]")
        last = f"v{i + 1}"
    fc.append(f"[0:a]atempo={sp}[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc),
           "-map", f"[{last}]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", CFG.get("VIDEO_CRF", "20"),
           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print("done:", a.out)


if __name__ == "__main__":
    main()
