@echo off
rem Abre o app (bandeja + bolinha + painel) sem janela de terminal.
set PYTHONIOENCODING=utf-8
start "" "%~dp0.venv\Scripts\pythonw.exe" -m linear ui
