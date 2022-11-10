@echo off

python tools/cubemap2fisheye.py --fov 210 --cubemap_dir "output_raw_data/cubemap" --output_dir "output_raw_data/output_fisheye" --external_path "output_raw_data/external.txt"

pause