@echo off
setlocal

REM ======= KONFIGURATION =======
set "ENV_NAME=Stimmenfaenger"
set "WORKDIR=C:\Users\simon\Documents\Heidenheim\Stimmenfaenger\RealTimeSTT-"

REM ======= Conda initialisieren (activate.bat) =======
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"

REM WICHTIG: conda ist eine .bat -> immer mit CALL aufrufen!
call conda activate %ENV_NAME%

REM ======= Optional: kurz zeigen, welches Python aktiv ist =======
where python
python --version
echo.

REM ======= Arbeitsverzeichnis wechseln =======
cd /d "%WORKDIR%"

REM ======= Python-Skript starten =======
python tests\simple_test_UDP.py

REM ======= Fenster offen halten =======
echo.
echo ==============================
echo Python-Skript wurde beendet.
pause

endlocal
