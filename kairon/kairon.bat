@echo off
setlocal enabledelayedexpansion

REM kairon entry point
REM 1. dispatcher.md を claude -p に投げて、動かすべき agent 名のリストを得る
REM 2. 各 agent を run-agent.bat 経由で fire-and-forget で起動する

cd /d "%~dp0"

set "TMPLIST=%TEMP%\kairon_agents_%RANDOM%.txt"

claude -p --permission-mode dontAsk --allowedTools "Read" "Glob" < dispatcher.md > "%TMPLIST%"

for /f "usebackq delims=" %%a in ("%TMPLIST%") do (
    if exist "agents\%%a.md" (
        start "" /b "%~dp0run-agent.bat" "%%a"
    )
)

del "%TMPLIST%" 2>nul
endlocal
