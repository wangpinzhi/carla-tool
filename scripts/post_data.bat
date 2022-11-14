@echo off

python tools/cubemap2fisheye.py --fov 210 --cubemap_dir "output_invisiable_data/cubemap" --output_dir "output_invisiable_data/output_fisheye" --external_path "output_invisiable_data/external.txt"

pause