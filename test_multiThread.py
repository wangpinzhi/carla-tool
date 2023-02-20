import numpy as np
import time
import threading
from queue import Queue

np.random.seed(5)

global_q = Queue()


def save_data():
    i = 0
    while True:
        sim_cube_data = global_q.get()
        np.savez(
            f'test_save/{i}.npz',
            front   = sim_cube_data['front'],
            left    = sim_cube_data['left'],
            right   = sim_cube_data['right'],
            back    = sim_cube_data['back'],
            up      = sim_cube_data['up'],
            down    = sim_cube_data['down'],
        )
        i += 1
        global_q.task_done()

save_thread = threading.Thread(target=save_data)
save_thread.daemon=True
save_thread.start()

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
    global_q.put(sim_cube_data.copy())
    
global_q.join()

use_time = time.time() - start_time
print(use_time)