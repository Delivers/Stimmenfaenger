@echo off
setlocal

REM ======= KONFIGURATION =======
set "ENV_NAME=stt"
set "WORKDIR=C:\Users\User\Documents\Stimmenfaenger\stt"

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
python -u stt_de_keywords_top5_unigrams.py --device 1 --model "C:\Users\User\Documents\Stimmenfaenger\stt\vosk-model-small-de-0.15"


REM ======= Fenster offen halten =======
echo.
echo ==============================
echo Python-Skript wurde beendet.
pause

endlocal
