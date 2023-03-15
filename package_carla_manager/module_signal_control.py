import signal

all = [
    'function_get_global_signal',
]

# global exit signal
__global_val_signal_exit = False

def function_handler(parameter_signum,
                     parameter_frame):
    global __global_val_signal_exit
    __global_val_signal_exit = True


def function_get_global_signal():
    return __global_val_signal_exit

signal.signal(signal.SIGINT, function_handler)
signal.signal(signal.SIGTERM, function_handler)