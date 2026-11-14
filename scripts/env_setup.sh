#!/usr/bin/env bash
# Claude Code のクラウド環境「soshi」のセットアップスクリプト欄に貼る内容
# （環境の起動時に1回実行される想定。何度実行しても安全）
set -e
pip install -q --break-system-packages Pillow webvtt-py yt-dlp
command -v ffmpeg >/dev/null 2>&1 || (apt-get update -q && apt-get install -y -q ffmpeg)
if [ "$(fc-list :lang=ja 2>/dev/null | grep -c 'Noto Sans CJK')" -eq 0 ]; then
  apt-get update -q && apt-get install -y -q fonts-noto-cjk
fi
