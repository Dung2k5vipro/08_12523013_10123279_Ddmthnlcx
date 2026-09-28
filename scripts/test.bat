@echo off
chcp 65001 > nul
echo ========================================================
echo   CHẠY KIỂM THỬ TỰ ĐỘNG & SPAM LOAD TEST CHO API
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe scripts\test_api.py %*
) else (
    python scripts\test_api.py %*
)

echo.
pause
