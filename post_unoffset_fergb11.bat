@echo off

set VERSION=%1
set SCENE=%2
set FRAMES=%3
set ROOT_DIR="output/%VERSION%_%SCENE%"


python tools/cubemap2fisheye.py     --fov 190^
                                    --cubemap_dir "%ROOT_DIR%/raw_data"^
                                    --camera "rgb11"^
                                    --cubeW 2560^
                                    --outW 2560^
                                    --frames %FRAMES%^
                                    --output_dir "%ROOT_DIR%/post_data"^
                                    --use_cuda