@echo off
cd /d "%~dp0..\ai-models"
"%~dp0..\.venv\Scripts\python.exe" -m uvicorn service.main:app --host 127.0.0.1 --port 8001 --reload
