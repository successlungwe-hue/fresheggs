@echo off
REM Starts FreshEggs so phones on the same Wi-Fi can use it (for the Android app).
cd /d "%~dp0"
if not exist .venv ( py -m venv .venv && call .venv\Scripts\activate.bat && python -m pip install -r requirements.txt ) else ( call .venv\Scripts\activate.bat )
python run_desktop.py --lan
pause
