@echo off
@title Doctorate - Game Update

git config core.sparseCheckout true

call env\scripts\activate.bat

python3 update_config.py
python3 update_game.py