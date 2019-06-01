import hashlib
import os
import socket
import subprocess
from sys import platform
from urllib.parse import urlparse

from requests import get


def has_ffmpeg() -> bool:
    if platform == 'win32':
        p = subprocess.Popen('ffmpeg -version', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        msg = out.decode()
        p.terminate()
    else:
        p = subprocess.Popen('ffmpeg -version', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=popen_env())
        out, err = p.communicate()
        msg = out.decode()
        p.terminate()
    return 'ffmpeg version' in msg


def is_url(_url: str) -> bool:
    _url = urlparse(_url)
    if _url.scheme not in ['http', 'https'] or len(_url.netloc) < 5:
        return False
    return True


# 广域网ip
def get_wan_ip() -> str:
    res = get('http://ip.360.cn/IPShare/info')
    return res.json()['ip']


# 局域网ip
def get_lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def is_int(s) -> bool:
    try:
        int(s)
        return True
    except:
        pass

    return False


def move_to_screen_center(target):
    width = target.winfo_screenwidth()
    height = target.winfo_screenheight()
    w = target.winfo_width() + 1
    h = target.winfo_height() + 1
    x = int((width - w) / 2)
    y = int((height - h) / 2)
    target.geometry('{}x{}+{}+{}'.format(w, h, x, y))
    target.update()
    pass


def to_md5(string):
    """
    计算字符串md5值
    :param string: 输入字符串
    :return: 字符串md5
    """
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


def popen_env() -> dict:
    env = os.environ.copy()
    env['PATH'] = '/usr/local/bin:' + env['PATH']
    return env
