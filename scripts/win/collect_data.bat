@echo off

@REM Variables
set ROOT_PATH=output/huawei_demo

start python tools/sim_run.py   --save_data_path "%ROOT_PATH%"^
                                --config_path "%ROOT_PATH%/huawei_demo_config.json"
