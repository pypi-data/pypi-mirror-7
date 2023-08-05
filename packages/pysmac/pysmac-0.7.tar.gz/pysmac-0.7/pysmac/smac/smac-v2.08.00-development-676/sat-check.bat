@echo off
set SMACMEM=1024
IF NOT "%SMAC_MEMORY%"=="" (set SMACMEM=%SMAC_MEMORY%)
set DIR=%~dp0
set EXEC=ca.ubc.cs.beta.aclib.example.satisfiabilitychecker.SatisfiabilityChecker
set jarconcat=
SETLOCAL ENABLEDELAYEDEXPANSION
for /F "delims=" %%a IN ('dir /b /s "%DIR%\*.jar"') do set jarconcat=%%a;!jarconcat!
for /F "delims=" %%a IN ('dir /b /s "%DIR%\lib\*.jar"') do set jarconcat=%%a;!jarconcat!
echo Starting sat-check with %SMACMEM% MB of RAM
java -Xmx%SMACMEM%m -cp "%DIR%conf\;%DIR%patches\;%jarconcat%%DIR%patches\ " %EXEC% %*
