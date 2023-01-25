@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb8 cm_rgb13 cm_rgb11 cm_depth0"

start python tools/cubemap2pinhole.py   --fov 60^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole"^
                                        --camera "cm_rgb8"^
                                        

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190"^
                                        --camera "cm_rgb13"^
                                        

start python tools/cubemap2fisheye.py   --fov 190^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 30^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye190"^
                                        --camera "cm_rgb11"^
                                        

start /WAIT python tools/cubemap2erp.py       --external_path "%ROOT_PATH%/external.txt"^
                                        --cubeW 2560^
                                        --format "npz"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/erp"^
                                        --camera "cm_depth0"^
                                        
