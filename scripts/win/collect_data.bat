@echo off

@REM Variables
set WORLD_MAP=Town10
set FRAMES=50
set ROOT_PATH=output/%WORLD_MAP%_frames_%FRAMES%

python tools/sim_run.py   --frames %FRAMES%^
                                --fixed_delta_time 0.05^
                                --save_data_path "%root_path%"^
                                --sensor_config_path "configs/ph_config.json"^
                                --seedw 26

pause
