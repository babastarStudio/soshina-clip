#!/usr/bin/env bash
# Claude Code のクラウド環境「soshi」のセットアップスクリプト欄に貼る内容
# （環境の起動時に1回実行される想定。何度実行しても安全）
set -e
pip install -q --break-system-packages Pillow webvtt-py yt-dlp
command -v ffmpeg >/dev/null 2>&1 || (apt-get update -q && apt-get install -y -q ffmpeg)
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc ]; then
  apt-get update -q && apt-get install -y -q fonts-noto-cjk fonts-noto-cjk-extra
fi
