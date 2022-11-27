@echo off
python tools/cubemap2fisheye.py --fov 210^
                                --external_path "output/Town02_frames_500/external.txt"^
                                --cubemap_dir "output/Town02_frames_500/cubemap"^
                                --output_dir "output/Town02_frames_500/fisheye"                  
pause