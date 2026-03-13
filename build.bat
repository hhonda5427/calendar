@echo off
REM 休日カレンダーアプリを exe にビルドします
REM 初回のみ: pip install pyinstaller

cd /d "%~dp0"

pip install pyinstaller --quiet
pyinstaller --onefile --windowed --name "HolidayCalendar" --clean holiday_calendar_app.py

echo.
echo ビルド完了: dist\HolidayCalendar.exe
pause
