@echo off

@REM Variables
set MAP=Town10
set ROOT_PATH=output/%MAP%_demo3

start python tools/sim_run.py   --sync_mode^
                                --fixed_delta_time 0.05^
                                --save_data_path "%ROOT_PATH%"^
                                --sensor_config_path "configs/demo3/sensor_config.json"^
                                --scene_config_path "configs/demo3/scene_config.json"

pause
