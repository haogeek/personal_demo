# coding=utf-8

from functools import wraps, partial


__mapper__ = {}


def register(name):
    def decorator(cls):
        __mapper__[name] = cls
        return cls
    return decorator


def dependency(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cls = __mapper__[name]
            kwargs[name] = cls
            new_func = partial(func, **kwargs)
            new_func(*args)
        return wrapper
    return decorator
