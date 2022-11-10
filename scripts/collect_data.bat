@echo off
start python tools/sim_run.py   --frames 100^
                                --fixed_delta_time 0.09^ 
                                --save_data_path output_raw_data^
                                --reload_map^
                                --map Town03^
                                --server_up 192.168.1.207