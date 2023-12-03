@echo off
@title Doctorate - Game Update

git config core.sparseCheckout true

call env\scripts\activate.bat

python3 update_config.py
python3 update_game.py

git clone -n --depth=1 --filter=tree:0 https://github.com/Kengxxiao/ArknightsGameData.git
cd ArknightsGameData/
git sparse-checkout set --no-cone zh_CN/gamedata/excel/
git checkout

mv zh_CN/gamedata/excel data/

rm -r ArknightsGameData/