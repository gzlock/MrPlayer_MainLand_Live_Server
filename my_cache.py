from tkinter import Variable

import appdirs
from diskcache import Cache

__temp_dir = appdirs.user_data_dir(appname='mrplayer_live', appauthor='gzlock')

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
