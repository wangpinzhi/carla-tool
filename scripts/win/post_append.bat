@echo off

set ROOT_PATH=output/%1_%2

python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                --cubeW 2560^
                                --format "npz"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/erp"^
                                --camera "cm_depth11"^
                                --use_cuda