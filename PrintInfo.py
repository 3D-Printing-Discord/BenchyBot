import datetime
import inspect
import builtins
import os


true_print = print


def my_print(*args, **kwargs):
    stack = inspect.stack()
    last_frame = stack[1]
    filename = last_frame.filename
    del stack, last_frame

    filename_string = os.path.split(filename)[-1]
    time_string = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    info_string = f"{filename_string:>15} | {time_string:>19}:"

    return true_print(
        info_string,
        *args,
        **kwargs
        )


def start():
    builtins.print = my_print
