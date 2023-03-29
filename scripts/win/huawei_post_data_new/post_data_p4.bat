@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb7 cm_rgb6 cm_rgb1"

@REM start python tools/cubemap2pinhole.py   --fov 150^
@REM                                         --cubeW 2560^
@REM                                         --outH 1856^
@REM                                         --outW 2880^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_new"^
@REM                                         --camera "cm_rgb7"^
@REM                                         --use_cuda
                                        

@REM start python tools/cubemap2pinhole.py   --fov 150^
@REM                                         --cubeW 2560^
@REM                                         --outH 1080^
@REM                                         --outW 1920^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_new"^
@REM                                         --camera "cm_rgb6"^
@REM                                         --use_cuda
                                        

@REM start /WAIT python tools/cubemap2pinhole.py   --fov 150^
@REM                                         --cubeW 2560^
@REM                                         --outH 1856^
@REM                                         --outW 2880^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_new"^
@REM                                         --camera "cm_rgb1"^
@REM                                         --use_cuda
                                        
