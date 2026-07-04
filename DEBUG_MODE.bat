for /F "tokens=*" %%a in ('dir Emuera_skiaV*.exe /B /O-D') do (start "" "%%a" -Debug & exit /B)
pause