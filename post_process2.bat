@echo off
@REM python post_process.py  --num_workers 4^
@REM                         --gpu 0^
@REM                         --batch_size 4^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\test_scene\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:XDrive\raw_data\test_scene2"^
@REM                         --save_dir "H:\test_scene2\post_data"
@REM set scene=calibration
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 4^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:\%scene%\raw_data"^
@REM                         --save_dir "H:\%scene%\post_data"

set scene=fence01
python post_process.py  --num_workers 2^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
                        --raw_data_dir "H:Fence\raw_data\%scene%"^
                        --save_dir "H:Fence\post_data\%scene%"

@REM set scene=random_scene09
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 4^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:\%scene%\raw_data"^
@REM                         --save_dir "H:\%scene%\post_data"

@REM set scene=random_scene10
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 4^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:\%scene%\raw_data"^
@REM                         --save_dir "H:\%scene%\post_data"