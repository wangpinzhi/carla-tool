@echo off

@REM Variables
set WORLD_MAP=Town05
set FRAMES=500
set ROOT_PATH=output/%WORLD_MAP%_frames_%FRAMES%

start python tools/sim_run.py   --frames %FRAMES%^
                                --fixed_delta_time 0.09^
                                --save_data_path "%root_path%"^
                                --sensor_config_path "configs/sensor_config.json"^
                                --reload_map^
                                --map "%map%"

pause
