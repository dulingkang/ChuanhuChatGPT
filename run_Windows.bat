@echo off
echo Opening SdbChatGPT...

if not exist "%~dp0\SdbChat\Scripts" (
    echo Creating venv...
    python -m venv SdbChat

    cd /d "%~dp0\SdbChat\Scripts"
    call activate.bat

    cd /d "%~dp0"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

goto :activate_venv

:launch
%PYTHON% SdbChatbot.py %*
pause

:activate_venv
set PYTHON="%~dp0\SdbChat\Scripts\Python.exe"
echo venv %PYTHON%
goto :launch
