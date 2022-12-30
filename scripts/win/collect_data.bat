@echo off

@REM Variables
set ROOT_PATH=output/erp2ph_demo

start python tools/sim_run.py   --save_data_path "%ROOT_PATH%"^
                                --config_path "%ROOT_PATH%/erp2ph_demo_config.json"
