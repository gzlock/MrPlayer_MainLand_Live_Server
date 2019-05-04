import socketio
from sanic import Sanic
from sanic.response import file

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)

online = 0

namespace = '/danmaku'

app.static('/video', './test')


@app.route('/')
async def index(request):
    return await file('./index.html')


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2333, access_log=False)
