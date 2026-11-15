# 粗品切り抜き 運用キット

## 分担
- PC（週1回だけ起動）: `bin/pc_fetch.py` で元動画・字幕・情報を丸ごとダウンロード → クラウドへ取り込み
- クラウド（いつでも）: 場面探し → 切り出し → 型Aで書き出し → iPhoneへ送付
- あなた: ヘッダーの一言 / 最終チェック / 投稿 / 出典をコメント欄へ

## ルール
- 尺 20〜40秒（B型：前振りからオチまで）。検証用に60秒前後（C型）を4本に1本。エンディングなし
- ヘッダー = YouTubeタイトル。「〜な粗品／〜する粗品」で終える。1行10文字×2行まで
- 2行目（〜な粗品）は黄色。改行位置はClaudeが決め、文言は勝手に変えない
- 画面下には元動画タイトルだけ（「〇〇」より）。出典（チャンネル名・URL）はコメント欄
- ラベル: 失礼な粗品(6) / やられる粗品(3) / いい粗品(1)
- 公式「粗品のロケ」が既に切り抜いた場面は避ける

## ファイル
- config.env … 設定
- CLAUDE.md … Claude向けの運用ルール（セッション開始時に自動で読まれる）
- setup.sh … 環境確認とテスト書き出し（セッションの最初に実行）
- scripts/env_setup.sh … Claude Codeの環境「soshi」のセットアップスクリプト欄に貼る内容
- bin/make_short.py … 型Aの書き出し
- bin/pc_fetch.py … PC用ダウンローダー（--dest でドライブのフォルダへ保存）
- bin/drive_pull.py … クラウド側でドライブから sources/ へ取り込む
- bin/transcript.py … 字幕→タイムスタンプ付きテキスト
- logs/posts.csv … 投稿ログ（分析用）

## 書き出し例
python3 bin/make_short.py --src sources/<ID>/video.mp4 --start 1030 --end 1042 \
  --header "日本一のツッコミで殴られた粗品" --label やられる粗品 \
  --source-title "タクシーの運転手に殴られた" --subs subs.json --out out/<ID>_1.mp4
