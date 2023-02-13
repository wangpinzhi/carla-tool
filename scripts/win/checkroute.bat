@echo off

@REM Variables
set VERSION=%1
set SCENE=%2

python tools/sim_checkroute.py  --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part1.json"
                
pause
