@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Stickman Video Studio

echo ==================================================
echo        STICKMAN VIDEO STUDIO  -  offline
echo ==================================================

rem --- gaseste Python (py launcher sau python din PATH) ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY goto :nopython

rem --- 1. creeaza mediul virtual (doar prima data) ---
if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creez mediul virtual venv ...
    %PY% -m venv venv
    if errorlevel 1 goto :nopython
)

call "venv\Scripts\activate.bat"

rem --- 2. instaleaza dependintele (prima data sau cand requirements.txt se schimba) ---
set "NEED_INSTALL=1"
if exist "venv\installed_requirements.txt" (
    fc /b "requirements.txt" "venv\installed_requirements.txt" >nul 2>nul && set "NEED_INSTALL=0"
)
if "%NEED_INSTALL%"=="1" (
    echo [2/3] Instalez dependintele - poate dura cateva minute prima data ...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 goto :piperror
    copy /y "requirements.txt" "venv\installed_requirements.txt" >nul
) else (
    echo [2/3] Dependintele sunt deja instalate.
)

rem --- 3. porneste aplicatia ---
echo [3/3] Pornesc Stickman Video Studio in browser: http://localhost:8501
echo        Inchide aceasta fereastra pentru a opri aplicatia.
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
exit /b 0

:nopython
echo.
echo [EROARE] Python 3.10+ nu a fost gasit.
echo Instaleaza-l de pe https://www.python.org/downloads/ si bifeaza "Add python.exe to PATH".
pause
exit /b 1

:piperror
echo.
echo [EROARE] Instalarea dependintelor a esuat. Verifica conexiunea la internet (necesara DOAR la prima instalare)
echo si ruleaza din nou START_STUDIO.bat. Daca problema persista, sterge folderul venv si reincearca.
del /q "venv\installed_requirements.txt" >nul 2>nul
pause
exit /b 1
