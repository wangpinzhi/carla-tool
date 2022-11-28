@echo off

start python tools/sim_run.py   --frames 500^
                                --fixed_delta_time 0.09^
                                --save_data_path "output/Town04_frames_500"^
                                --sensor_config_path "configs/sensor_config.json"^
                                --reload_map^
                                --map "Town04"

pause
