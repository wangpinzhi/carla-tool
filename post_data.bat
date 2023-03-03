@echo off

set VERSION=%1
set SCENE=%2
set ROOT_DIR="output/%VERSION%_%SCENE%"

@REM echo "Process Fisheye"
@REM python tools/cubemap2fisheye.py     --fov 190^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --camera "rgb9"^
@REM                                     --cubeW 2560^
@REM                                     --outW 2560^
@REM                                     --r_x 30^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --use_cuda

@REM python tools/cubemap2fisheye.py     --fov 190^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --camera "rgb10"^
@REM                                     --cubeW 2560^
@REM                                     --outW 2560^
@REM                                     --r_x 42^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --use_cuda

@REM python tools/cubemap2fisheye.py     --fov 190^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --camera "rgb11"^
@REM                                     --cubeW 2560^
@REM                                     --outW 2560^
@REM                                     --r_x 30^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --use_cuda

@REM python tools/cubemap2fisheye.py     --fov 190^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --camera "rgb12"^
@REM                                     --cubeW 2560^
@REM                                     --outW 2560^
@REM                                     --r_x 42^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --use_cuda

@REM python tools/cubemap2fisheye.py     --fov 190^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --camera "rgb13"^
@REM                                     --cubeW 2560^
@REM                                     --outW 2560^
@REM                                     --r_x 0^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --use_cuda
@REM echo "Process Pinhole"
@REM python tools/cubemap2pinhole.py     --fov 100^
@REM                                     --cubeW 2560^
@REM                                     --outH 1856^
@REM                                     --outW 2880^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb1"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 30^
@REM                                     --cubeW 2560^
@REM                                     --outH 1856^
@REM                                     --outW 2880^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb2"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 100^
@REM                                     --cubeW 2560^
@REM                                     --outH 1856^
@REM                                     --outW 2880^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb4"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 100^
@REM                                     --cubeW 2560^
@REM                                     --outH 1080^
@REM                                     --outW 1920^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb5"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 100^
@REM                                     --cubeW 2560^
@REM                                     --outH 1080^
@REM                                     --outW 1920^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb6"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 100^
@REM                                     --cubeW 2560^
@REM                                     --outH 1856^
@REM                                     --outW 2880^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb7"^
@REM                                     --use_cuda

@REM python tools/cubemap2pinhole.py     --fov 60^
@REM                                     --cubeW 2560^
@REM                                     --outH 1080^
@REM                                     --outW 1920^
@REM                                     --cubemap_dir "%ROOT_DIR%/raw_data"^
@REM                                     --output_dir "%ROOT_DIR%/post_data"^
@REM                                     --camera "rgb8"^
@REM                                     --use_cuda


echo "Process ERP"
python tools/cubemap2erp.py    --cubemap_dir "%ROOT_DIR%/raw_data"^
                            --camera "depth0"^
                            --output_dir "%ROOT_DIR%/post_data"^
                            --cubeW 2560^
                            --out_height 2560^
                            --use_cuda

python tools/cubemap2erp.py    --cubemap_dir "%ROOT_DIR%/raw_data"^
                            --camera "depth11"^
                            --output_dir "%ROOT_DIR%/post_data"^
                            --cubeW 2560^
                            --out_height 2560^
                            --use_cuda
