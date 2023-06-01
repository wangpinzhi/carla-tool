@echo off
python post_process.py  --num_workers 2^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\test_scene\configs\sensor_config.json"^
                        --raw_data_dir "H:\test_scene\raw_data"^
                        --save_dir "H:\test_scene\ocam_post_data"^