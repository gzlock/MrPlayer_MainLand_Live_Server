import os

import socketio
from jinja2 import Environment, FileSystemLoader
from sanic import Sanic
from sanic.response import html

import resource_path

online = 0

namespace = '/danmaku'


def create_danmaku(app):
    sio = socketio.AsyncServer(async_mode='sanic')
    sio.attach(app)

    @sio.on('connect', namespace=namespace)
    async def connect(sid, environ):
        global online
        online += 1
        await sio.emit('online', str(online), namespace=namespace)

    @sio.on('disconnect', namespace=namespace)
    async def disconnect(sid):
        global online
        online -= 1
        await sio.emit('online', str(online), namespace=namespace)

    @sio.on('send_danmaku', namespace=namespace)
    async def send_danmaku(sid, message):
        # print('发送弹幕', message)

        # 广播给其他人
        await sio.emit('get_danmaku', message, namespace=namespace, skip_sid=sid)


def run(port: int, video_dir: str, socket_url: str, only_video: bool):
    # 模版系统
    env = Environment(loader=FileSystemLoader(resource_path.path('./')))

    app = Sanic()

    app.static('/video', os.path.normpath(video_dir))
    app.static('/favicon.ico', resource_path.path('./icon.ico'))

    if len(socket_url) == 0:
        socket_url = 'null'
    elif socket_url == '1':
        socket_url = '1'
        create_danmaku(app)

    if not only_video:
        @app.route('/')
        async def index(request):
            template = env.get_template('index.html')
            html_content = template.render(socket_url=socket_url)
            return html(html_content)

    app.run(host='0.0.0.0', port=port, access_log=False)
