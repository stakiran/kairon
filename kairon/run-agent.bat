@echo off
REM 内部用 wrapper: kairon.bat から呼ばれる
REM 引数 %1 に agent 名を受け取り、agents/<name>.md を claude -p に渡して実行する

cd /d "%~dp0"

claude -p --permission-mode dontAsk --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "WebSearch" "WebFetch" "Bash(echo:*)" < "agents\%~1.md"
