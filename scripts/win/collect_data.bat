@echo off

@REM Variables
set WORLD_MAP=Town10
set FRAMES=50
set ROOT_PATH=output/%WORLD_MAP%_frames_%FRAMES%

start python tools/sim_run.py   --frames %FRAMES%^
                                --fixed_delta_time 0.02^
                                --save_data_path "%root_path%"^
                                --sensor_config_path "configs/sensor_config.json"^
                                --number-of-vehicles 200^
                                --number-of-walkers 50^
                                --seedw 26

pause
