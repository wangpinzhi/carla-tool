@echo off
python post_process.py  --num_workers 4^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "output/huawei_parking16/configs/sensor_config.json"^
                        --raw_data_dir "output/huawei_parking16/raw_data"^
                        --save_dir "output/huawei_parking16/post_data_new"^       