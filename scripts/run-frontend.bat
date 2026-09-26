@echo off
cd /d "%~dp0..\app\frontend"
if not exist node_modules (
	echo node_modules chua ton tai, dang cai dependency...
	call npm install
	if errorlevel 1 exit /b 1
)
npm run dev
