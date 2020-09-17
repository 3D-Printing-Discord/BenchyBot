import datetime
import inspect 
import builtins
import os

true_print = print
def my_print(*args, **kwargs):

    # HANDLE MEMORY LEAK
    stack = inspect.stack()
    last_frame = stack[1]
    filename = last_frame.filename
    filename = os.path.split(filename)[-1]
    del stack, last_frame

    return true_print(f"{filename:>15} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'):>19}:", *args, **kwargs)
builtins.print = my_print

# _print = print
# def print(*args, **kw):
#     _print(f"{inspect.stack()[0][1]:<15}{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}:", *args, **kw)