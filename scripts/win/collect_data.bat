@echo off

set ROOT_PATH=output/huawei_parking03

start /WAIT python tools/sim_run.py     --save_data_path "%ROOT_PATH%"^
                            --num_workers 2^
                            --config_path "%ROOT_PATH%/huawei_parking03_part2.json"

start /WAIT python tools/sim_run.py     --save_data_path "%ROOT_PATH%"^
                            --num_workers 2^
                            --config_path "%ROOT_PATH%/huawei_parking03_part3.json"

start /WAIT python tools/sim_run.py     --save_data_path "%ROOT_PATH%"^
                            --num_workers 2^
                            --config_path "%ROOT_PATH%/huawei_parking03_part4.json"

