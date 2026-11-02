@echo off
REM Builds dist\FreshEggs.exe  (run this on Windows, with Python 3.10+ installed)
cd /d "%~dp0"
py -m venv .venv || goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller || goto :error
pyinstaller --noconfirm --clean --onefile --name FreshEggs ^
  --add-data "templates;templates" --add-data "static;static" run_desktop.py || goto :error
echo.
echo Done. Your program is: %cd%\dist\FreshEggs.exe
echo Double-click it to start FreshEggs. Its database is created in dist\instance.
pause
exit /b 0
:error
echo Build failed. See the messages above.
pause
exit /b 1
