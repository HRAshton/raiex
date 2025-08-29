@echo off
REM Activate venv and run main.py
set VENV_DIR=%~dp0venv
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found in %VENV_DIR%. Please create it first.
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"
python -m src.main
