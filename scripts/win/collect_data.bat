@echo off

@REM Variables

set ROOT_PATH=output/huawei/huawei_parking02

start python tools/sim_run.py     --save_data_path "%ROOT_PATH%"^
                            --num_workers 2^
                            --config_path "%ROOT_PATH%/huawei_parking02_part1.json"
