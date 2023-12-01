@echo off
@title Doctorate - Local Server

call env\scripts\activate.bat
python3 server\app.py
