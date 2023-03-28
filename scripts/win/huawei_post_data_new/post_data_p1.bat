@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb8 cm_rgb13 cm_rgb11 cm_depth0"

start python tools/cubemap2pinhole.py   --fov 120^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb8"^
                                        --use_cuda
                                        

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 15^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190_new"^
                                        --camera "cm_rgb13"^
                                        --use_cuda
                                        

start /WAIT python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 15^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190_new"^
                                        --camera "cm_rgb11"^
                                        --use_cuda
                                        
