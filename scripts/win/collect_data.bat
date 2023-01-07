@echo off

@REM Variables

set ROOT_PATH=output/parking_01

python tools/sim_run.py         --save_data_path "%ROOT_PATH%"^
                                --num_workers 8^
                                --config_path "%ROOT_PATH%/parking_01_config.json"
