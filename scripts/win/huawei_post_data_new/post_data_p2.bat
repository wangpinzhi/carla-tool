@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb9 cm_rgb10 cm_rgb12"

@REM start python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 15^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_new"^
@REM                                         --camera "cm_rgb9"^
@REM                                         --use_cuda
                                        

@REM start python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 15^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_new"^
@REM                                         --camera "cm_rgb10"^
@REM                                         --use_cuda
                                        

@REM start /WAIT python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 15^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_new"^
@REM                                         --camera "cm_rgb12"^
@REM                                         --use_cuda
                                        

