@echo off
timeout 120

rem ****powershell.exe -ExecutionPolicy Bypass -File assets\mail\reboot-server.ps1***

rem ****Set here your delays****
set delay_startscript=10
set delay_checkwatchdogfile=60
set delay_startpatch=440
set hh=%TIME:~0,2%
set open=09
set close=23

:setup

set CRASHCOUNTER=0
mode con:cols=70 lines=12
color E0
echo 0 > watchdog
echo Please, keep this window alive !
echo =====================================================================
echo starting script in %delay_startscript% seconds
echo =====================================================================
timeout %delay_startscript%
cls

set hh=%TIME:~0,2%
set /p VAR= < watchdog
set start=%TIME%


if %hh% geq %open% (

	if %hh% leq %close% (

		if %VAR% equ 0 (

			goto startVvvv

			) else (
			goto main
			)

	) else (
	goto main
	)

) else (
goto main
)

:startVvvv
color E0
echo Please, keep this window alive !
echo =====================================================================
echo Starting Vvvv...
echo Enabling watchdog in %delay_startpatch% seconds
echo =====================================================================
"C:\Users\sw\AppData\Local\Microsoft\WindowsApps\python.exe" "E:\VOITH\wol.py" /showexceptions false /allowmultiple
timeout 10
start E:\VOITH\_Fluidstone\vvvv_50alpha38.2_x64\vvvv.exe /o "E:\VOITH\_Fluidstone\SYSTEM\CONTENT.v4p" /showexceptions false /allowmultiple 
timeout 10
start E:\VOITH\_Fluidstone\vvvv_50alpha38.2_x64\vvvv.exe /o "E:\VOITH\_video_fun\01_video_delay.v4p" /showexceptions false /allowmultiple 
timeout 10
start E:\VOITH\_eternal-dream\vvvv_beta_40_x64\vvvv.exe /o "E:\VOITH\_eternal-dream\Eternal-Dream_ROOT.v4p" /showexceptions false /allowmultiple
timeout %delay_startpatch%
cls
goto main

:Vvvvpresent
color A0
echo Please, keep this window alive !
echo =====================================================================
echo Vvvv started since %start%
echo PID %VAR%
echo TIME %TIME%
echo Patch has crashed %CRASHCOUNTER% times
echo Checking watchdog file in %delay_checkwatchdogfile% seconds
echo =====================================================================
echo 0 > watchdog
timeout %delay_checkwatchdogfile%
cls
goto main

:Vvvvabsent
color C0
set /a CRASHCOUNTER+=1
rem **** powershell.exe -ExecutionPolicy Bypass -File assets\mail\watchdog-crash-server.ps1 ***
echo Please, keep this window alive !
echo =====================================================================
echo Vvvv crashed, freezed or Watchdog (Windows) are not in your patch !
echo Restarting Vvvv in 5 seconds
echo =====================================================================
taskkill /F /IM vvvv.exe
taskkill /F /IM python.exe
timeout 5
rem *** shutdown.exe /r /t 00 ***
cls
goto startVvvv



:main
set hh=%TIME:~0,2%
set /p VAR= < watchdog 

if %hh% geq %open% (

	if %hh% leq %close% (

		if %VAR% gtr 0 (

			goto Vvvvpresent
			) else (
			goto Vvvvabsent
			)

	) else (
	goto main
	)

) else (
goto main
)

goto main