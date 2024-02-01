@echo off
echo Opening SDBChatGPT...

if not exist "%~dp0\SDBChat\Scripts" (
    echo Creating venv...
    python -m venv SDBChat

    cd /d "%~dp0\SDBChat\Scripts"
    call activate.bat

    cd /d "%~dp0"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

goto :activate_venv

:launch
%PYTHON% SDBChatbot.py %*
pause

:activate_venv
set PYTHON="%~dp0\SDBChat\Scripts\Python.exe"
echo venv %PYTHON%
goto :launch
