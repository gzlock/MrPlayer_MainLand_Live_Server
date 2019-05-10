from tempfile import gettempdir
from os import path as osPath
from diskcache import Cache
from tkinter import Variable

__temp_dir = osPath.normpath(osPath.join(gettempdir(), 'mrplayer_temp'))

print('cache dir', __temp_dir)

cache = Cache(__temp_dir)


def tkVariable(var: Variable, key: str, default=None):
    """
    将tkinter的var绑定到缓存
    :param var:
    :param key:
    :param default:
    :return:
    """
    _cache = cache.get(key, default=None)
    if _cache is None:
        if default is not None:
            var.set(default)
    else:
        var.set(_cache)
    var.trace('w', lambda a, b, c: cache.set(key, var.get()))
