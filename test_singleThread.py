import numpy as np
import time
import threading
from queue import Queue

np.random.seed(5)
start_time = time.time()

for i in range(50):
    time.sleep(0.2)
    sim_cube_data = {
        'front' : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
        'left'  : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
        'right' : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
        'back'  : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
        'up'    : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
        'down'  : np.random.randint(0, 255, (2560,2560,3), dtype=np.uint8),
    }
    np.savez(
        f'test_save/{i}.npz',
        front   = sim_cube_data['front'],
        left    = sim_cube_data['left'],
        right   = sim_cube_data['right'],
        back    = sim_cube_data['back'],
        up      = sim_cube_data['up'],
        down    = sim_cube_data['down'],
    )

use_time = time.time() - start_time
print(use_time)