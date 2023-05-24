@echo off

set ROOT_PATH=output/%1_%2

@REM python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 30^
@REM                                         --format "npz"^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_depth"^
@REM                                         --camera "cm_depth9"^
@REM                                         --use_cuda
                                        

python tools/cubemap2fisheye.py   --fov 190^
                                  --cubeW 2560^
                                  --outW 2560^
                                  --r_x 42^
                                  --format "npz"^
                                  --external_path "%ROOT_PATH%/external.txt"^
                                  --cubemap_dir "%ROOT_PATH%/cubemap"^
                                  --output_dir "%ROOT_PATH%/fisheye190_depth"^
                                  --camera "cm_depth10"^
                                  --use_cuda
                                        

@REM start /WAIT python tools/cubemap2fisheye.py   --fov 190^
@REM                                         --cubeW 2560^
@REM                                         --outW 2560^
@REM                                         --r_x 42^
@REM                                         --format "npz"^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/fisheye190_depth"^
@REM                                         --camera "cm_depth12"^
@REM                                         --use_cuda