@echo off

set VERSION=%1
set SCENE=%2
set FRAMES=%3
set ROOT_DIR="output/%VERSION%_%SCENE%"


echo "Process Fisheye"
python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb9"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --r_x 30^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda

python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb10"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --r_x 42^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda

python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb11"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --r_x 30^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda

python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb12"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --r_x 42^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda

python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb13"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --r_x 0^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda
echo "Process Pinhole"
python tools/cubemap2pinhole.py     --fov 100^
                                    --cubeW 2560^
                                    --outH 1856^
                                    --outW 2880^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb1"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 30^
                                    --cubeW 2560^
                                    --outH 1856^
                                    --outW 2880^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb2"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 100^
                                    --cubeW 2560^
                                    --outH 1856^
                                    --outW 2880^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb4"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 100^
                                    --cubeW 2560^
                                    --outH 1080^
                                    --outW 1920^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb5"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 100^
                                    --cubeW 2560^
                                    --outH 1080^
                                    --outW 1920^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb6"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 100^
                                    --cubeW 2560^
                                    --outH 1856^
                                    --outW 2880^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb7"^
                                    --use_cuda

python tools/cubemap2pinhole.py     --fov 60^
                                    --cubeW 2560^
                                    --outH 1080^
                                    --outW 1920^
                                    --frames %FRAMES%^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --camera "rgb8"^
                                    --use_cuda


echo "Process ERP"
python tools/cubemap2erp.py    --cubemap_dir "%ROOT_DIR%/raw_data"^
                            --camera "depth0"^
                            --output_dir "%ROOT_DIR%/post_data"^
                            --cubeW 2560^
                            --out_height 2560^
                            --frames %FRAMES%^
                            --use_cuda

python tools/cubemap2erp.py    --cubemap_dir "%ROOT_DIR%/raw_data"^
                            --camera "depth11"^
                            --output_dir "%ROOT_DIR%/post_data"^
                            --cubeW 2560^
                            --out_height 2560^
                            --frames %FRAMES%^
                            --use_cuda
