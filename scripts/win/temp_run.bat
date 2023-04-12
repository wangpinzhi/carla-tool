@echo off

@REM 获取采集文件根目录
set VERSION=%1
set SCENE=%2
set NUM_WORKERS=%3

echo "VERSION is %VERSION%"
echo "SCENE is %SCENE%"
echo "NUM_WORKERS is %NUM_WORKERS%"

echo "start collecting part1, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part1.json"
python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                            --num_workers %NUM_WORKERS%^
                            --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part1.json"

echo "start collecting part2, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part2.json"
python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                            --num_workers %NUM_WORKERS%^
                            --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part2.json"

echo "start collecting part3, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part3.json"
python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                            --num_workers %NUM_WORKERS%^
                            --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part3.json"

echo "start collecting part4, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part4.json"
python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                            --num_workers %NUM_WORKERS%^
                            --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part4.json"

echo "start collecting part5, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part5.json"
python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                            --num_workers %NUM_WORKERS%^
                            --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part5.json"



