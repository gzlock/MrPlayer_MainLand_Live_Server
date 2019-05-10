from os import popen
from requests import get
from urllib.parse import urlparse
import socket


def has_ffmpeg() -> bool:
    check_ffmpeg = popen('ffmpeg -version').read()
    return 'ffmpeg version' in check_ffmpeg


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
    x = int((width - target.winfo_reqwidth()) / 2)
    y = int((height - target.winfo_reqheight()) / 2)
    target.geometry('+{}+{}'.format(x, y))