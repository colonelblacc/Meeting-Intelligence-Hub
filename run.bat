@echo off
echo Installing dependencies...
cd backend
call .venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
echo Starting Meeting Intelligence Hub...
echo You can access the application at http://localhost:8000
call .venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000
pause
