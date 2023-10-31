@echo off

set scene=random_objects
set save_name=random_objects_8
python post_process.py  --num_workers 4^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
                        --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
                        --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects
@REM set save_name=random_objects_2
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=shipyard
@REM set save_name=shipyard
@REM python post_process.py  --num_workers 4^
@REM                         --gpu 0^
@REM                         --batch_size 4^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"