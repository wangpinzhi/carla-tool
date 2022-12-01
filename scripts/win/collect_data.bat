@echo off

@REM Variables
set WORLD_MAP=Town10
set FRAMES=100
set ROOT_PATH=output/%WORLD_MAP%_demo

python tools/sim_run.py     --frames %FRAMES%^
                            --sync_mode^
                            --fixed_delta_time 0.05^
                            --save_data_path "%ROOT_PATH%"^
                            --sensor_config_path "configs/sensor_config.json"^
                            --scene_config_path "configs/scene_configs/demo1.json"

pause
