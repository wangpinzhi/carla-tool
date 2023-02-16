@echo off

@REM 获取采集文件根目录
set VERSION=%1
set SCENE=%2
set NUM_WORKERS=%3

echo "VERSION is %VERSION%"
echo "SCENE is %SCENE%"
echo "NUM_WORKERS is %NUM_WORKERS%"

if "%VERSION%" == "huawei" (
    echo "start collecting part5, json file is output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part5.json"
    python tools/sim_run.py     --save_data_path "output/%VERSION%_%SCENE%"^
                                --num_workers %NUM_WORKERS%^
                                --config_path "output/%VERSION%_%SCENE%/%VERSION%_%SCENE%_part5.json"
)


