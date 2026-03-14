@echo off
echo === SIP Realtime Call Handler Startup ===
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
echo Dependencies installed

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: ngrok is not installed!
    echo Please install ngrok from: https://ngrok.com/download
    echo Or run: choco install ngrok
    pause
    exit /b 1
)

REM Start Flask app in background
echo.
echo Starting Flask application...
start /B python app.py
timeout /t 3 /nobreak >nul

REM Start ngrok
echo.
echo Starting ngrok tunnel...
start /B ngrok http 8000
timeout /t 3 /nobreak >nul

REM Get ngrok URL
echo.
echo Fetching ngrok URL...
timeout /t 2 /nobreak >nul

curl -s http://localhost:4040/api/tunnels > ngrok_response.json
for /f "tokens=*" %%i in ('powershell -Command "(Get-Content ngrok_response.json | ConvertFrom-Json).tunnels[0].public_url"') do set NGROK_URL=%%i
del ngrok_response.json

if "%NGROK_URL%"=="" (
    echo ERROR: Could not get ngrok URL
    taskkill /F /IM python.exe /T >nul 2>nul
    taskkill /F /IM ngrok.exe /T >nul 2>nul
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Service is running!
echo ==========================================
echo.
echo Ngrok Public URL: %NGROK_URL%
echo Webhook Endpoint: %NGROK_URL%/webhook/incoming
echo Health Check: %NGROK_URL%/health
echo.
echo ==========================================
echo.
echo Configure this webhook URL in OpenAI platform:
echo %NGROK_URL%/webhook/incoming
echo.
echo Press Ctrl+C to stop all services
echo.

REM Keep window open
pause
