@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
set "PYTHONPATH=%PROJECT_ROOT%.python_packages;%PROJECT_ROOT%"
"C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe" -c "import os, sys; sys.path.insert(0, os.environ['PYTHONPATH'].split(';')[0]); sys.path.insert(0, os.environ['PYTHONPATH'].split(';')[1]); from streamlit.web import cli as stcli; app_path=os.path.join(os.environ['PYTHONPATH'].split(';')[1],'app.py'); sys.argv=['streamlit','run',app_path,'--global.developmentMode=false','--server.address=127.0.0.1','--server.port=8503']; raise SystemExit(stcli.main())"
