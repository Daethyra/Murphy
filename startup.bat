@echo off
set LOG_DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
set PYTHONIOENCODING=utf-8

:start
echo [%date% %time%] Starting Murphy... >> murphy_service_%LOG_DATE%.log
.venv\Scripts\python.exe -X utf8 -m murphy.chatbot >> murphy_output_%LOG_DATE%.log 2>&1

set exit_code=%errorlevel%
echo [%date% %time%] Murphy exited with code %exit_code% >> murphy_service_%LOG_DATE%.log

if %exit_code% == 0 (
    echo [%date% %time%] Clean shutdown. >> murphy_service_%LOG_DATE%.log
    exit /b 0
)

echo [%date% %time%] Unexpected exit, restarting in 5 seconds... >> murphy_service_%LOG_DATE%.log
timeout /t 5 /nobreak >nul
goto start