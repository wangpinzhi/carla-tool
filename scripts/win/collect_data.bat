@echo off

@REM Variables
set MAP=Town10
set ROOT_PATH=output/%MAP%_demo_100frames

start python tools/sim_run.py   --save_data_path "%ROOT_PATH%"^
                                --config_path "output/Town10_demo_100frames/demo_config.json"
