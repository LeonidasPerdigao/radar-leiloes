@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  🏎️  RADAR DE LEILÕES - Iniciando...                  ║
echo ╚════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo.
    echo ❌ ERRO: Python não está instalado!
    echo.
    echo Instale em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Criar ambiente virtual
if not exist "venv" (
    echo 📦 Criando ambiente virtual (primeira vez)...
    python -m venv venv
)

REM Ativar
echo ✅ Ativando ambiente...
call venv\Scripts\activate.bat

REM Instalar
echo 📥 Instalando dependências...
pip install -q streamlit pandas

REM Rodar
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  ✅ Pronto! Abrindo em http://localhost:8501          ║
echo ║  Pressione Ctrl+C para parar                          ║
echo ╚════════════════════════════════════════════════════════╝
echo.

streamlit run app.py

pause
