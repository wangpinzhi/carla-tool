@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb4 cm_rgb5 cm_rgb2"

start python tools/cubemap2pinhole.py   --fov 150^
                                        --cubeW 2560^
                                        --outH 1856^
                                        --outW 2880^
                                        --format "jpg"^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb4"^
                                        --use_cuda
                                        

start python tools/cubemap2pinhole.py   --fov 150^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --format "jpg"^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb5"^
                                        --use_cuda
                                        

start /WAIT python tools/cubemap2pinhole.py   --fov 60^
                                        --cubeW 2560^
                                        --outH 1856^
                                        --outW 2880^
                                        --format "jpg"^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb2"^
                                        --use_cuda
                                        
