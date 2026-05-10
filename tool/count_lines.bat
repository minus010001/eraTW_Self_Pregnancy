@echo off
setlocal

echo Counting matching lines...
echo.

python "d:\eratw-chs\tool\count_matching_lines.py" "."

echo.
echo Press any key to exit...
pause >nul
