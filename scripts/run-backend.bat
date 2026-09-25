cd /d "%~dp0..\app\backend"
if not exist node_modules (
	npm install
)
npm run dev
