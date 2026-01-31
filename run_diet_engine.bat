@echo off
echo Starting Diet Engine...

:: Start Backend
start "Backend" cmd /c "cd backend && venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: Start Frontend
start "Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ==========================================
echo  Diet Engine is starting up!
echo  Backend: http://127.0.0.1:8000
echo  Frontend: http://localhost:5173
echo ==========================================
echo Keep these windows open to keep the site running.
pause
