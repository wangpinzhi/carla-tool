@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb7 cm_rgb3 cm_depth0"

start python tools/cubemap2fisheye.py   --fov 180^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye180"^
                                        --camera "cm_rgb7"^
                                        

start python tools/cubemap2fisheye.py   --fov 180^
                                        --cubeW 2560^
                                        --outW 2560^
                                        --r_x 0^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/fisheye180"^
                                        --camera "cm_rgb3"^
                                        

start /WAIT python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                            --cubeW 2560^
                                            --format "npz"^
                                            --cubemap_dir "%ROOT_PATH%/cubemap"^
                                            --output_dir "%ROOT_PATH%/erp"^
                                            --camera "cm_depth0"^
                                            

