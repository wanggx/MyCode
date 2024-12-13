
import threading


def decroator_func(original_func):
    def wrapper(*args, **kwargs):
        print("before")
        original_func(*args, **kwargs)
        print("after")
    return wrapper


#@decroator_func
def module_test(module):
    print(module + " module test")
    print(threading.current_thread().name)


module_func = decroator_func(module_test)

module_func('decorator')


