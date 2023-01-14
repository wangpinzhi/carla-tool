@echo off

@REM 获取采集文件根目录
set VERSION=%1
set SCENE=%2

echo "VERSION is %VERSION%"
echo "SCENE is %SCENE%"

if "%VERSION%" == "huawei" (
    call scripts\win\huawei_post_data\post_data_p1.bat output/%VERSION%_%SCENE%
    call scripts\win\huawei_post_data\post_data_p2.bat output/%VERSION%_%SCENE%
    call scripts\win\huawei_post_data\post_data_p3.bat output/%VERSION%_%SCENE%
    call scripts\win\huawei_post_data\post_data_p4.bat output/%VERSION%_%SCENE%
)

if "%VERSION%" == "nju" (
    call scripts\win\nju_post_data\post_data_p1.bat output/%VERSION%_%SCENE%
    call scripts\win\nju_post_data\post_data_p2.bat output/%VERSION%_%SCENE%
    call scripts\win\nju_post_data\post_data_p3.bat output/%VERSION%_%SCENE%
)
