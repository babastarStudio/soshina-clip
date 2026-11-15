#!/usr/bin/env bash
# クラウド側の環境セットアップ（何度実行しても安全）
set -euo pipefail
cd "$(dirname "$0")"
source ./config.env

echo "== 依存関係"
command -v ffmpeg >/dev/null || { echo "ffmpeg がありません（apt で入れてください）"; exit 1; }
python3 -c "import PIL" 2>/dev/null || pip install -q --break-system-packages Pillow
python3 -c "import webvtt" 2>/dev/null || pip install -q --break-system-packages webvtt-py

echo "== 日本語フォント"
# 型Aは Black / Medium ウェイトを使う（標準の fonts-noto-cjk には入っていない）
if [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc ] || [ ! -f /usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc ]; then
  echo "Noto Sans CJK の Black/Medium を追加します"
  apt-get install -y -q fonts-noto-cjk fonts-noto-cjk-extra >/dev/null 2>&1 || \
    { apt-get update -q >/dev/null 2>&1 && apt-get install -y -q fonts-noto-cjk fonts-noto-cjk-extra >/dev/null; }
fi

echo "== フォルダ"
mkdir -p "$SOURCES_DIR" "$OUT_DIR" "$(dirname "$POST_LOG")"
[ -f "$POST_LOG" ] || echo "date,video_id,source_title,start,end,duration_sec,variant,label,header,shorts_url,views_48h,viewed_rate,avg_view_pct,subs_gained,notes" > "$POST_LOG"

echo "== 動作テスト"
tmp=$(mktemp -d)
ffmpeg -y -loglevel error -f lavfi -i "testsrc2=size=1280x720:rate=30:duration=3" \
  -f lavfi -i "sine=frequency=440:duration=3" -c:v libx264 -c:a aac -shortest "$tmp/src.mp4"
python3 -I bin/make_short.py --src "$tmp/src.mp4" --out "$tmp/out.mp4" \
  --header "セットアップが完了した粗品" --source-title "テスト" >/dev/null
rm -rf "$tmp"
echo "OK: 環境は準備できています"
