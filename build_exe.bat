@echo off
REM Builds dist\FreshEggs.exe on Windows (Python 3.10+ required).
cd /d "%~dp0"
py -m venv .venv || goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller || goto :error
pyinstaller --noconfirm --clean --onefile --name FreshEggs --icon icon.ico ^
  --add-data "templates;templates" --add-data "static;static" desktop.py || goto :error
echo.
echo Done. Your program is: %cd%\dist\FreshEggs.exe
pause
exit /b 0
:error
echo Build failed. See the messages above.
pause
exit /b 1
