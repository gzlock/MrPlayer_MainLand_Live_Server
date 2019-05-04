import os
import sys

from jinja2 import Environment, FileSystemLoader
from sanic import Sanic
from sanic.response import html

app = Sanic()

# todo 视频缓存目录地址
video_dir = './'

# todo 弹幕源 网址
socket_url = 'null'


# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 模版系统
env = Environment(loader=FileSystemLoader(resource_path('./')))


@app.route('/')
async def index(request):
    template = env.get_template('client_index.html')
    html_content = template.render(socket_url=socket_url)
    return html(html_content)


if __name__ == '__main__':
    app.static('/video', video_dir)
    app.run(host='0.0.0.0', port=2333, access_log=False)


def run(port: int, video_dir: str, _socket_url: str):
    global socket_url

    if len(_socket_url) == 0:
        socket_url = 'null'
    else:
        socket_url = '"{}"'.format(_socket_url)

    app.static('/video', os.path.normpath(video_dir))
    app.run(host='0.0.0.0', port=port, access_log=False)
    pass
