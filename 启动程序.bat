@echo off
:: Set terminal code page to UTF-8
chcp 65001 > nul
:: Force Python to use UTF-8 for everything
set PYTHONUTF8=1
python main.py
pause
