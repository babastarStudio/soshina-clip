#!/usr/bin/env python3
"""字幕(vtt)を「[mm:ss] セリフ」の読みやすいテキストにする（場面探し用）

使い方: python3 transcript.py sources/<ID>/video.ja.vtt > sources/<ID>/transcript.txt
自動字幕の重複行（ローリング表示）は除去する。
"""
import re, sys
import webvtt

def ts(sec):
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"

def main(path):
    last = ""
    for c in webvtt.read(path):
        text = re.sub(r"\s+", " ", c.text.replace("\n", " ")).strip()
        if not text:
            continue
        # 自動字幕は前の行を含んで繰り返すので、新しい部分だけ残す
        if last and text.startswith(last):
            text = text[len(last):].strip()
        if text and text != last:
            print(f"[{ts(c.start_in_seconds)}] {text}")
            last = c.text.split("\n")[-1].strip() or text

if __name__ == "__main__":
    main(sys.argv[1])
