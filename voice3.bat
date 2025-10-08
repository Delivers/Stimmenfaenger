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
python stt_de_keywords_top5_unigrams-fallback-log.py --device 1 --model "C:\Users\User\Documents\Stimmenfaenger\stt\vosk-model-small-de-0.15" --quotes-file "C:\Users\User\Documents\Stimmenfaenger\stt\kunst_und_sprache_zitate.txt" --log-file "C:\Users\User\Documents\Stimmenfaenger\live_inputs_log.txt"


REM ======= Fenster offen halten =======
echo.
echo ==============================
echo Python-Skript wurde beendet.
pause

endlocal
