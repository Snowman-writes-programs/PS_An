@echo off

@title OpenDoctoratePy - Local Server

call env\scripts\activate.bat

pypy server\app.py
