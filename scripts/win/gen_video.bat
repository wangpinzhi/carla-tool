@echo off

@REM Variables
set ROOT_PATH=output/huawei/huawei_parking02

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/erpVis"^
                                        --output_dir "./video"^
                                        --camera "erpVis_depth0"^
                                        --format "jpg"^
                                        --output_width 5120^
                                        --output_height 2560^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/fisheye190"^
                                        --output_dir "./video"^
                                        --camera "fe_rgb11"^
                                        --format "jpg"^
                                        --output_width 2560^
                                        --output_height 2560^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/fisheye190"^
                                        --output_dir "./video"^
                                        --camera "fe_rgb13"^
                                        --format "jpg"^
                                        --output_width 2560^
                                        --output_height 2560^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

start python tools/generate_video.py    --input_dir "%ROOT_PATH%/pinhole_1080p_60"^
                                        --output_dir "./video"^
                                        --camera "ph_rgb8"^
                                        --format "jpg"^
                                        --output_width 1920^
                                        --output_height 1080^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --fps 20

pause
