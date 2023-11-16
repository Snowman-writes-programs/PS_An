@echo off
@title OpenDoctoratePy - Frida Hook

cls
call env\scripts\activate.bat
pypy fridahook.py
