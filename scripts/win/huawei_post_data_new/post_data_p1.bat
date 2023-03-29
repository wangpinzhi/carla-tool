@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb8 cm_rgb13 cm_rgb11 cm_depth0"

@REM start python tools/cubemap2pinhole.py   --fov 120^
@REM                                         --cubeW 2560^
@REM                                         --outH 1080^
@REM                                         --outW 1920^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_new"^
@REM                                         --camera "cm_rgb8"^
@REM                                         --use_cuda
                                        

@REM start python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 15^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_new"^
@REM                                         --camera "cm_rgb13"^
@REM                                         --use_cuda
                                        

@REM start /WAIT python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 15^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_new"^
@REM                                         --camera "cm_rgb11"^
@REM                                         --use_cuda
                                        
