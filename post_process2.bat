@echo off

python post_process.py  --num_workers 4^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\omnitest\configs\sensor_config.json"^
                        --raw_data_dir "D:\heterogenenous-data-carla-main\output\omnitest\raw_data"^
                        --save_dir "D:\heterogenenous-data-carla-main\output\omnitest\post_data"

@REM set scene=random_objects_2
@REM set save_name=random_objects_2
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects_3
@REM set save_name=random_objects_3
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects_5
@REM set save_name=random_objects_5
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects_6
@REM set save_name=random_objects_6
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects_7
@REM set save_name=random_objects_7
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=random_objects_8
@REM set save_name=random_objects_8
@REM python post_process.py  --num_workers 2^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\append.json"^
@REM                         --raw_data_dir "H:RandomObjects\raw_data\%save_name%"^
@REM                         --save_dir "H:RandomObjects\post_data\%save_name%"

@REM set scene=omni_huawei_drive

@REM setlocal enabledelayedexpansion
@REM for /l %%i in (1,1,9) do (
@REM     set "num=%%i"
@REM     if !num! lss 10 set "num=0!num!"
@REM     echo !num!
@REM     python post_process.py  --num_workers 4^
@REM                         --gpu 0^
@REM                         --batch_size 1^
@REM                         --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                         --raw_data_dir "H:\omni_huawei_drive\raw_data\!num!"^
@REM                         --save_dir "H:\omni_huawei_drive\post_data\!num!"
@REM )
@REM endlocal

@REM set scene=rail_test
@REM set save_name=34
@REM python post_process.py  --num_workers 4^
@REM                        --gpu 0^
@REM                        --batch_size 1^
@REM                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                        --raw_data_dir "D:\heterogenenous-data-carla-main\output\%scene%\raw_data\%save_name%"^
@REM                        --save_dir "D:\heterogenenous-data-carla-main\output\%scene%\post_data\%save_name%"
@REM set scene=indoor_4fisheye_gym
@REM set save_name=parking180
@REM python post_process.py  --num_workers 4^
@REM                        --gpu 0^
@REM                        --batch_size 1^
@REM                        --sensor_config_json "D:\heterogenenous-data-carla-main\output\%scene%\configs\sensor_config.json"^
@REM                        --raw_data_dir "D:\heterogenenous-data-carla-main\output\%scene%\raw_data\%save_name%"
                    @REM    --save_dir "D:\heterogenenous-data-carla-main\output\%scene%\post_data\test2"
