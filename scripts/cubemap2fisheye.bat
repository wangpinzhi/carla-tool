@echo off

python tools/cubemap2fisheye.py --fov 210 --cubemap_dir "output_invisiable_data_frame100/cubemap" --output_dir "output_invisiable_data_frame100/output_fisheye" --external_path "output_invisiable_data_frame100/external.txt"

pause