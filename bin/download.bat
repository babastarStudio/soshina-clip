@echo off
rem ダブルクリックで実行：fetch_list.txt の動画を sources へダウンロードする
chcp 65001 >nul
cd /d "%~dp0"
where yt-dlp >nul 2>nul || winget install -e --id yt-dlp.yt-dlp --accept-source-agreements --accept-package-agreements
where deno >nul 2>nul || winget install -e --id DenoLand.Deno --accept-source-agreements --accept-package-agreements
where ffmpeg >nul 2>nul || winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
where py >nul 2>nul || where python >nul 2>nul || winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
yt-dlp -U
where py >nul 2>nul && (py -3 pc_fetch.py) || (python pc_fetch.py)
echo.
echo 終わりました。この画面は閉じてかまいません。
pause
