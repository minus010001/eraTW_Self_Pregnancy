@echo off
:: Launch eraTW Debug Mode


START "" "%~dp0Emuera1824+v18+EMv17+EEv38+SRW.exe" -debug -quickstart
::START "" "%~dp0Emuera1824+v18+EMv17+EEv38+SRW.exe" -debug
wmic process where name="Emuera1824+v18+EMv17+EEv38+SRW.exe" CALL setpriority 128
:: wmic process where name="Emuera" CALL setpriority 128