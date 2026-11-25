@echo off
REM Executa todo o pipeline. Uso: rodar_tudo.bat  (no terminal do VS Code, na pasta do projeto)
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"

if not exist .venv (
    echo [1/6] Criando ambiente virtual...
    python -m venv .venv || goto erro
)
call .venv\Scripts\activate.bat || goto erro

echo [2/6] Instalando dependencias (a 1a vez demora)...
python -m pip install -r requirements.txt || goto erro

echo [3/6] Validando base e tokens (1a vez baixa o modelo)...
python src\validar_base.py || goto erro

echo [4/6] Indexando no ChromaDB...
python src\indexar.py || goto erro

echo [5/6] Rodando experimentos...
python src\experimentos.py || goto erro

echo [6/6] Gerando casos de RAG...
python src\rag.py --casos > resultados\rag_saida_console.txt || goto erro

echo.
echo CONCLUIDO. Resultados em resultados\
exit /b 0

:erro
echo.
echo FALHOU na etapa acima. Veja a mensagem de erro e a secao "Como executar" do README.
exit /b 1
