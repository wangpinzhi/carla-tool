@echo off
python post_process.py  --num_workers 2^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "output/huawei_parking15_cmp/configs/sensor_config.json"^
                        --raw_data_dir "output/huawei_parking15_cmp/raw_data"^
                        --save_dir "output/huawei_parking15_cmp/post_data_new"^