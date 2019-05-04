import multiprocessing
import os
import socket
import sys
import webbrowser
from urllib.parse import urlparse
from sys import platform

import PySimpleGUI as sg
import requests

import client_server
import client_m3u8
import create_list

font = ''

if platform == "darwin":
    font = 'a'
elif platform == "win32":
    font = 'Msyh'


# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_number(s) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def is_dir_empty(dir: str) -> bool:
    return len(os.listdir(dir)) == 0


def get_wan_ip() -> str:
    res = requests.get('http://ip.360.cn/IPShare/info')
    return res.json()['ip']


def get_lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def is_full_url(_url: str) -> bool:
    _url = urlparse(_url)
    if _url.scheme not in ['http', 'https'] or len(_url.netloc) < 5:
        return False
    return True


def create_final_mp4(video_dir: str) -> bool:
    check_ffmpeg = os.popen('ffmpeg -version').read()

    if 'ffmpeg version' not in check_ffmpeg:
        return False
    os.system('sh {}/create_mp4.sh'.format(video_dir))
    return True


def stop_process():
    if is_working:
        m3u8_process.kill()
        server_process.kill()


layout = [
    [sg.Text('欢迎使用玩很大转播程序', )],
    [
        sg.Image(filename=resource_path('./logo.gif')),
        sg.Text('home.js2.me这个源每周六夜晚9点55分钟左右会开启\n在这个时间打开这个软件即可\n周六夜晚12点后就可以关闭了'),
    ],
    [
        sg.Text('视频缓存目录', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('', disabled=True, key='video_dir_input'),
        sg.FolderBrowse(button_text='设置目录', key='folder_btn')
    ],
    [
        sg.Text('网站端口', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('2334', key='port_input'),
    ],
    [
        sg.Text('视频源', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('http://home.js2.me:2333/video/live.m3u8', key='video_url_input'),
        sg.Text('必填', font='Helvetica 10'),
    ],
    [
        sg.Text('弹幕源', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('http://home.js2.me:2333/danmaku', key='danmaku_url_input'),
        sg.Text('可为空', font='Helvetica 10'),
    ],
    [
        sg.Text('HTTP代理', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('', key='proxy_input'),
        sg.Text('可为空', font='Helvetica 10'),
    ],
    [
        sg.Text('广域网网址', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('', key='wan_url_input', disabled=True, ),
        sg.Butt('打开', key='wan_url_btn', font='Helvetica 10', disabled=True),
    ],
    [
        sg.Text('局域网网址', size=(15, 1), auto_size_text=False, justification='right'),
        sg.InputText('', key='lan_url_input', disabled=True),
        sg.Butt('打开', key='lan_url_btn', font='Helvetica 10', disabled=True),
    ],
    [
        sg.Button('开启服务', key='start_server_btn'),
        sg.Button('关闭服务', disabled=True, key='stop_server_btn'),
        sg.Button('清空缓存', key='clear_video_cache'),
        sg.Button('合并视频', key='create_final_mp4'),
    ],
    [
        sg.Text('本软件的愿景：让宪迷都可以每周六22点准时收看玩很大\n'
                '在此希望：请向其他人分享你的广域网网址(很多人都可以看到)或局域网网址(同一个局域网的人都可以看到)', font=font + ' 10'),
    ],
    # [
    #     sg.Text('在此希望：运行本软件的宪迷向其他人分享您的广域网网址，前提是你需要有公网IP', font='Helvetica 10'),
    # ],
    [
        sg.Button('联系开发者(QQ群)', key='chat_with_developer', font=font + ' 10'),
        sg.Button('百度吴宗宪吧', key='open_tieba', font=font + ' 10'),
    ],
]

server_process = None
m3u8_process = None
is_working = False

if __name__ == '__main__':

    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    window = sg.Window('玩很大转播程序 v0.2', layout, font=font + ' 14', resizable=False)

    while True:  # Event Loop
        event, values = window.Read()
        print(event, values)

        if event in [None, 'Exit']:
            print('is_working', is_working)
            if is_working:
                if sg.PopupOKCancel('转播程序正在运作，确认退出？', '警告') is 'OK':
                    stop_process()
                    break
            else:
                break

        video_dir = values['video_dir_input']
        video_url = values['video_url_input']
        danmaku_url = values['danmaku_url_input']
        port = values['port_input']
        proxy = values['proxy_input']

        if event == 'start_server_btn':

            if len(video_dir) is 0:
                sg.Popup('请选择缓存目录', title='错误', font='Helvetica 14')
                continue

            video_dir = os.path.abspath(video_dir)

            if is_number(port) is False:
                sg.Popup('端口只能使用数字', title='错误', font='Helvetica 14')
                continue

            port = int(port)
            if port < 2000:
                sg.Popup('端口必须要大于2000', title='错误', font='Helvetica 14')
                continue

            if is_full_url(video_url) is False:
                sg.Popup('视频源网址有误', title='错误', non_blocking=False, font='Helvetica 14')
                continue

            if len(danmaku_url) > 0 and is_full_url(danmaku_url) is False:
                sg.Popup('弹幕源网址有误', title='错误', non_blocking=False, font='Helvetica 14')
                continue

            if is_dir_empty(video_dir) is False:
                goon = sg.PopupOKCancel('视频缓存目录有文件，还要继续使用吗？\n这个目录有可能会被清空！', title='警告')
                print('goon', goon, type(goon))
                if goon is 'Cancel':
                    continue

            window.Element('start_server_btn').Update(disabled=True)
            window.Element('stop_server_btn').Update(disabled=False)
            window.Element('folder_btn').Update(disabled=True)
            window.Element('port_input').Update(disabled=True)
            window.Element('video_url_input').Update(disabled=True)
            window.Element('danmaku_url_input').Update(disabled=True)
            window.Element('proxy_input').Update(disabled=True)

            url = 'http://{}:{}'
            window.Element('lan_url_input').Update(url.format(get_lan_ip(), port))
            window.Element('wan_url_input').Update(url.format(get_wan_ip(), port))
            window.Element('lan_url_btn').Update(disabled=False)
            window.Element('wan_url_btn').Update(disabled=False)

            m3u8_process = multiprocessing.Process(target=client_m3u8.run, args=(video_dir, video_url, proxy,))
            m3u8_process.start()

            server_process = multiprocessing.Process(target=client_server.run, args=(port, video_dir, danmaku_url,))
            server_process.start()

            is_working = True

        elif event == 'stop_server_btn':
            window.Element('start_server_btn').Update(disabled=False)
            window.Element('stop_server_btn').Update(disabled=True)
            window.Element('folder_btn').Update(disabled=False)
            window.Element('folder_btn').Update(disabled=False)
            window.Element('port_input').Update(disabled=False)
            window.Element('video_url_input').Update(disabled=False)
            window.Element('danmaku_url_input').Update(disabled=False)
            window.Element('proxy_input').Update(disabled=False)

            window.Element('lan_url_input').Update('')
            window.Element('wan_url_input').Update('')
            window.Element('lan_url_btn').Update(disabled=True)
            window.Element('wan_url_btn').Update(disabled=True)

            stop_process()
            is_working = False

        elif event == 'wan_url_btn':
            webbrowser.open(values['wan_url_input'])

        elif event == 'lan_url_btn':
            webbrowser.open(values['lan_url_input'])

        elif event == 'clear_video_cache' and len(video_dir) > 0:
            confirm = sg.PopupOKCancel('确认清空视频缓存目录？\n' + video_dir, '危险操作')
            if confirm is 'OK':
                print('清空目录')

        elif event == 'create_final_mp4':
            create_list.run(video_dir)
            if create_final_mp4(video_dir) is False:
                sg.Popup('没有安装FFmpeg，无法合并视频', '错误')
                continue
            print('合并视频中')

        elif event == 'chat_with_developer':
            webbrowser.open(
                'https://shang.qq.com/wpa/qunwpa?idkey=c93fa2d0819d8405ed6468d48126e7ac2644a716dec65b4353355944ec6a426f')
        elif event == 'open_tieba':
            webbrowser.open(
                'http://tieba.baidu.com/f?kw=吴宗宪&ie=utf-8')

    window.Close()
