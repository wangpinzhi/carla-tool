"""
验证导出深度图数据是否正确
"""

import os
import json
import numpy as np
import cv2

def run():
    with open(os.path.join('_out_first', 'output1219.json'), 'r+', encoding='utf-8') as p:
        temp_list = json.load(p)
    temp_nplist = np.array(temp_list)
    temp_nplist = temp_nplist * 256 / 1000
    # temp_nplist = np.log2(1 + temp_nplist)
    cv2.imwrite(os.path.join('_out_first', 'output1219.jpg'), temp_nplist)


if __name__ == '__main__':
    run()
