@echo off
python post_process.py  --num_workers 2^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "output/huawei_real_parking01/configs/sensor_config.json"^
                        --raw_data_dir "output/huawei_real_parking01/raw_data"^
                        --save_dir "output/huawei_real_parking01/post_data_new"^