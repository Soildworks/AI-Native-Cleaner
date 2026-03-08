@echo off
echo Starting data cleaning...
python clean.py
echo.
echo Checking output files...
dir /b *.csv *.png
echo.
echo Done!
pause
