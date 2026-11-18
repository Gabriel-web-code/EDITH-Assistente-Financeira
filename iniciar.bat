@echo off
cd /d "%~dp0"
set EDITH_LOCAL=1
if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv
)
echo Verificando dependencias...
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
echo Iniciando EDITH...
".venv\Scripts\python.exe" -m streamlit run app.py
pause
