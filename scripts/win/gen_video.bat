@echo off

@REM Variables
set ROOT_PATH=output/Town10_demo3

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/erpVis"^
                                        --output_dir "./video"^
                                        --camera "erpVis_depth1"^
                                        --output_width 2048^
                                        --output_height 1024^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/fisheye"^
                                        --output_dir "./video"^
                                        --camera "fe_rgb1"^
                                        --output_width 1024^
                                        --output_height 1024^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/fisheye"^
                                        --output_dir "./video"^
                                        --camera "fe_rgb2"^
                                        --output_width 1024^
                                        --output_height 1024^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

pause
