@echo off

@REM Variables
set ROOT_PATH=output\huawei_driving06

python tools/generate_video.py  --input_dir "%ROOT_PATH%/erpVis"^
                                --output_dir "./video"^
                                --camera "erpVis_depth0"^
                                --format "jpg"^
                                --output_width 5120^
                                --output_height 2560^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --fps 20

python tools/generate_video.py  --input_dir "%ROOT_PATH%/fisheye190"^
                                --output_dir "./video"^
                                --camera "fe_rgb9"^
                                --format "jpg"^
                                --output_width 2560^
                                --output_height 2560^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --fps 20

python tools/generate_video.py  --input_dir "%ROOT_PATH%/pinhole"^
                                --output_dir "./video"^
                                --camera "ph_rgb1"^
                                --format "jpg"^
                                --output_width 2880^
                                --output_height 1856^
                                --external_path "%ROOT_PATH%/external.txt"^
                                --fps 20

pause
