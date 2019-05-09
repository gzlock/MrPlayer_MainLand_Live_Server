import os
import shutil
import socket
import sys
import tkinter
from multiprocessing import freeze_support, Process
from time import sleep
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from webbrowser import open

from fake_useragent import UserAgent
from pyperclip import copy
import requests

import client_server
import create_list
import m3u8
import mul_process_package

mul_process_package.ok()


# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_number(s) -> bool:
    try:
        int(s)
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


def start_server():
    global is_working
    is_working = True
    port.config(state='readonly')
    start_btn.config(state=tkinter.DISABLED)
    stop_btn.config(state=tkinter.NORMAL)
    video_url.config(state='readonly')
    danmaku_url.config(state='readonly')

    ip_frame.pack()


def stop_server():
    global is_working
    is_working = False
    port.config(state=tkinter.NORMAL)
    start_btn.config(state=tkinter.NORMAL)
    stop_btn.config(state=tkinter.DISABLED)
    video_url.config(state=tkinter.NORMAL)
    danmaku_url.config(state=tkinter.NORMAL)

    ip_frame.pack_forget()


# 广域网ip
def get_wan_ip() -> str:
    res = requests.get('http://ip.360.cn/IPShare/info')
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


def has_ffmpeg() -> bool:
    check_ffmpeg = os.popen('ffmpeg -version').read()
    return 'ffmpeg version' in check_ffmpeg


def disable_child(frame: tkinter.Widget, state, without: list):
    for child in frame.winfo_children():
        if type(child) == tkinter.Frame:
            disable_child(child, state, without=without)
        elif child not in without:
            child.config(state=state)


def is_url(_url: str) -> bool:
    _url = urlparse(_url)
    if _url.scheme not in ['http', 'https'] or len(_url.netloc) < 5:
        return False
    return True


def test_connect(video_url: str, proxy: str) -> str:
    """
    :param video_url:
    :param proxy:
    :return: 'ok'||'NeedTWIP'||'NotM3u8'||'ProxyError'||'ConnectError'
    """
    has_proxy = len(proxy) > 0
    proxies = {}
    if has_proxy:
        proxies = {'http': proxy, 'https': proxy}
    headers = {
        "User-Agent": UserAgent().random,
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded",
        "Pragma": "no-cache",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    }
    try:
        if video_url == '1':
            res = requests.request("POST",
                                   "https://api2.4gtv.tv/Channel/GetChannelUrl",
                                   data='"fnCHANNEL_ID=4&fsASSET_ID=4gtv-4gtv040&fsDEVICE_TYPE=pc&clsIDENTITY_VALIDATE_ARUS%5BfsVALUE%5D=123"',
                                   headers=headers,
                                   proxies=proxies,
                                   timeout=5)
            if res.status_code is not 200 or 'flstURLs' not in res.text:
                return 'NeedTWIP'
            print(res.json()['Data']['flstURLs'][0])

            return 'ok'
        else:
            res = requests.get(video_url, proxies=proxies, headers=headers)
            if res.status_code is not 200 or '#EXTM3U' not in res.text:
                return 'NotM3u8'
            return 'ok'

    except Exception as e:
        print(e.__str__())
        if 'ProxyError' in e.__str__():
            return 'ProxyError'
        return 'ConnectError'


class BaseLayout:
    layout: tkinter.Widget
    without_disable: list = []

    def disable(self, disabled: bool):
        state = tkinter.NORMAL
        if disabled:
            state = tkinter.DISABLED
        disable_child(self.layout, state=state, without=self.without_disable)


class LocalForm(BaseLayout):

    def __init__(self, root) -> None:
        super().__init__()

        # 视频 缓存 目录
        self.layout = layout = tkinter.LabelFrame(root, text='本地设置')
        layout.pack(fill=tkinter.BOTH, padx=5, pady=5)

        frame = tkinter.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        tkinter.Label(frame, text='缓存目录', width=7, anchor=tkinter.E).pack(side=tkinter.LEFT)

        self.__video_cache = tkinter.StringVar()
        input = tkinter.Entry(frame, state='readonly', textvariable=self.__video_cache)
        input.pack(fill=tkinter.X, side=tkinter.LEFT,
                   expand=True)
        tkinter.Button(frame, text='选择目录', command=self.__select_folder).pack(side=tkinter.RIGHT, padx=2)
        self.without_disable.append(input)

        # 服务 端口
        frame = tkinter.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)

        tkinter.Label(frame, text='网站端口', width=7, anchor=tkinter.E).pack(side=tkinter.LEFT)

        self.__port = tkinter.StringVar()
        self.__port.set('2333')
        tkinter.Entry(frame, textvariable=self.__port).pack(fill=tkinter.BOTH, padx=2, expand=True)

    def __select_folder(self):
        self.__video_cache.set(filedialog.askdirectory(title='选择要存放视频缓存的目录'))

    def port(self):
        return self.__port.get()

    def video_cache_dir(self):
        return self.__video_cache.get()


class VideoUrlForm(BaseLayout):

    def __init__(self, root) -> None:
        super().__init__()
        self.layout = layout = tkinter.LabelFrame(root, text='网络源设置(*为必填)')
        layout.pack(fill=tkinter.BOTH, padx=5, pady=5)

        # 直播源 选择
        self.__select = select = tkinter.StringVar()
        select.set('1')
        frame = tkinter.Frame(layout)
        frame.pack(fill=tkinter.BOTH)
        tkinter.Radiobutton(frame, text='四季TV视频源（需要台湾IP）', variable=select, value='1').pack(anchor=tkinter.W)
        tkinter.Radiobutton(frame, text='软件开发者的视频源（每周六晚21点55分左右开启）', variable=select, value='2').pack(
            anchor=tkinter.W)
        tkinter.Radiobutton(frame, text='自填', variable=select, value='3').pack(anchor=tkinter.W)
        select.trace('w', callback=self.__radio_change)

        # 直播源 输入框
        self.__video_frame = frame = tkinter.Frame(layout)

        tkinter.Label(frame, text='直播源(*)', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT, padx=5, pady=5)
        self.__video = tkinter.StringVar()
        tkinter.Entry(frame, textvariable=self.__video).pack(fill=tkinter.X, padx=5, expand=True)

        # 弹幕源 输入框
        self.__danmaku_frame = frame = tkinter.Frame(layout)

        tkinter.Label(frame, text='弹幕源', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT, padx=5, pady=5)
        self.__danmaku = tkinter.StringVar()
        tkinter.Entry(frame, textvariable=self.__danmaku).pack(fill=tkinter.X, padx=5, expand=True)

        # 代理 输入框
        frame = tkinter.Frame(layout)
        frame.pack(fill=tkinter.BOTH)
        tkinter.Label(frame, text='网络代理', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT, padx=5, pady=5)
        self.__proxy = tkinter.StringVar()
        tkinter.Entry(frame, textvariable=self.__proxy).pack(fill=tkinter.X, padx=5, expand=True)

        self.__radio_change()

    def __radio_change(self, *args):
        select = self.__select.get()
        if select == '1':
            self.__video.set('1')
            self.__danmaku.set('')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack(fill=tkinter.BOTH)

        elif select == '2':
            self.__video.set('http://home.js2.me:2333/video/live.m3u8')
            self.__danmaku.set('http://home.js2.me:2333/danmaku')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack_forget()

        else:
            self.__video.set('')
            self.__danmaku.set('')
            self.__video_frame.pack(fill=tkinter.BOTH)
            self.__danmaku_frame.pack(fill=tkinter.BOTH)

    def video_url(self) -> str:
        return self.__video.get()

    def danmaku_url(self) -> str:
        return self.__danmaku.get()

    def proxy_url(self) -> str:
        return self.__proxy.get()


class UrlForm(BaseLayout):

    def __init__(self, root) -> None:
        super().__init__()
        self.layout = tkinter.LabelFrame(root, text='向其他人分享您的：')
        self.layout.pack(fill=tkinter.BOTH, padx=5, pady=5)
        self.lan_ip = tkinter.StringVar()
        self.wan_ip = tkinter.StringVar()

        frame = tkinter.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, padx=5, pady=5)
        tkinter.Label(frame, text='局域网网址').pack(side=tkinter.LEFT)
        input = tkinter.Entry(frame, textvariable=self.lan_ip, state='readonly')
        input.pack(fill=tkinter.BOTH)
        self.without_disable.append(input)

        frame = tkinter.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, padx=5, pady=5)
        tkinter.Button(frame, text='打开', command=lambda: UrlForm.open(self.lan_ip.get())).pack(side=tkinter.RIGHT)
        tkinter.Button(frame, text='复制', command=lambda: UrlForm.copy(self.lan_ip.get())).pack(side=tkinter.RIGHT)

        frame = tkinter.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, padx=5, pady=5)
        tkinter.Label(frame, text='广域网网址').pack(side=tkinter.LEFT)
        input = tkinter.Entry(frame, textvariable=self.wan_ip, state='readonly')
        input.pack(fill=tkinter.BOTH)
        self.without_disable.append(input)

        frame = tkinter.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, padx=5, pady=5)
        tkinter.Button(frame, text='打开', command=lambda: UrlForm.open(self.wan_ip.get())).pack(side=tkinter.RIGHT)
        tkinter.Button(frame, text='复制', command=lambda: UrlForm.copy(self.wan_ip.get())).pack(side=tkinter.RIGHT)

    def show(self):
        self.layout.pack()

    def hide(self):
        self.layout.pack_forget()

    def set_ip(self, port: str):
        url = 'http://{}:{}'
        self.lan_ip.set(url.format(get_lan_ip(), port))
        self.wan_ip.set(url.format(get_wan_ip(), port))

    def clear_ip(self):
        self.lan_ip.set('')
        self.wan_ip.set('')

    @staticmethod
    def copy(text: str):
        copy(text)

    @staticmethod
    def open(text: str):
        open(text)


class ButtonsFrame:
    __m3u8_process = None
    __server_process = None

    def __init__(self, root, local_frame: LocalForm, video_frame: VideoUrlForm, url_frame: UrlForm) -> None:
        super().__init__()

        frame = tkinter.Frame(root)
        frame.pack(fill=tkinter.BOTH, padx=5, pady=5)

        self.local_frame = local_frame
        self.video_frame = video_frame
        self.url_frame = url_frame

        # 启动 服务
        self.start_btn = start_btn = tkinter.Button(frame, text='启动转播', command=self.start)  # 生成button1
        start_btn.pack(side=tkinter.LEFT)  # 将button1添加到root主窗口

        # 停止 服务
        self.stop_btn = stop_btn = tkinter.Button(frame, text='停止转播', command=self.stop, state=tkinter.DISABLED)
        stop_btn.pack(side=tkinter.LEFT, padx=5)

        # 合并视频文件
        self.create_mp4_btn = create_mp4_btn = tkinter.Button(frame, text='合并视频', command=self.create_mp4)
        create_mp4_btn.pack(side=tkinter.LEFT, padx=5)

        # 清空视频缓存
        self.clear_cache_btn = clear_cache_btn = tkinter.Button(frame, text='清空缓存', command=self.clear_cache)
        clear_cache_btn.pack(side=tkinter.RIGHT)

        self.is_start = False

        self.stop()

    # 检查缓存目录
    def check_video_cache_dir(self):
        video_cache_dir = self.local_frame.video_cache_dir()
        if len(video_cache_dir) == 0:
            tkinter.messagebox.showerror('错误', '请选择缓存目录')
            return False
        video_cache_dir = os.path.abspath(video_cache_dir)
        if not os.path.exists(video_cache_dir):
            os.mkdir(video_cache_dir)
        return video_cache_dir

    def start_process(self):

        video_cache_dir = self.check_video_cache_dir()
        if not video_cache_dir:
            return

        # 检查端口
        port = self.local_frame.port()
        if not is_number(port):
            return tkinter.messagebox.showerror('错误', '端口只能是数字')
        port = int(port)
        if port < 2000 or port > 60000:
            return tkinter.messagebox.showerror('错误', '端口只能从2000到60000')

        # print(video_cache_dir, port)

        # 检查 三个网址
        video_url = self.video_frame.video_url()
        danmaku_url = self.video_frame.danmaku_url()
        proxy_url = self.video_frame.proxy_url()
        # print(video_url, danmaku_url, proxy_url)

        if len(video_url) == 0:
            return tkinter.messagebox.showerror('错误', '请填写视频源网址')
        else:
            if video_url != '1' and not is_url(video_url):
                return tkinter.messagebox.showerror('错误', '视频源的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        if len(danmaku_url) > 0 and not is_url(danmaku_url):
            return tkinter.messagebox.showerror('错误', '弹幕源的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        if len(proxy_url) > 0:
            if not is_url(proxy_url):
                return tkinter.messagebox.showerror('错误', '代理的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        check = test_connect(video_url, proxy_url)
        if check != 'ok':
            has_proxy = len(proxy_url) > 0
            title = '连接错误'
            if has_proxy:
                title = '代理服务器出现错误'
            message = title
            if check == 'NeedTWIP':
                message = '需要台湾IP'
            elif check == 'ProxyError':
                message = '连接不到代理服务器'
            elif check == 'NotM3u8':
                message = '网络视频源返回的不是M3u8文件格式'
            return tkinter.messagebox.showerror(title, message)

        self.__m3u8_process = Process(target=m3u8.run, args=(video_cache_dir, video_url, proxy_url))
        self.__m3u8_process.start()

        self.__server_process = Process(target=client_server.run, args=(port, video_cache_dir, danmaku_url))
        self.__server_process.start()

        return '123ok'

    def start(self):
        if self.start_process() != '123ok':
            return
        self.is_start = True

        self.local_frame.disable(True)
        self.video_frame.disable(True)
        self.url_frame.disable(False)
        self.start_btn.config(state=tkinter.DISABLED)
        self.stop_btn.config(state=tkinter.NORMAL)
        self.clear_cache_btn.config(state=tkinter.DISABLED)
        self.create_mp4_btn.config(state=tkinter.DISABLED)

        self.url_frame.set_ip(port=self.local_frame.port())

    def stop(self):
        if self.__server_process is not None:
            self.__m3u8_process.kill()
            self.__server_process.kill()

        self.is_start = False

        self.local_frame.disable(False)
        self.video_frame.disable(False)
        self.url_frame.disable(True)
        self.start_btn.config(state=tkinter.NORMAL)
        self.stop_btn.config(state=tkinter.DISABLED)
        self.clear_cache_btn.config(state=tkinter.NORMAL)
        self.create_mp4_btn.config(state=tkinter.NORMAL)

        self.url_frame.clear_ip()

    def clear_cache(self):
        dir = self.check_video_cache_dir()
        if not dir:
            return
        i = 0
        true = True
        title = '高危操作，确认3次，当前第 {} 次'
        while true and i < 3:
            true = true and tkinter.messagebox.askokcancel(title.format(i + 1),
                                                           dir + '\n将会清空视频缓存文件夹内所有文件，确认清空？')
            i += 1
        if not true:
            return
        if os.path.exists(dir):
            try:
                shutil.rmtree(dir)
                sleep(0.2)
                os.mkdir(dir)
            except Exception as e:
                tkinter.messagebox.showerror('出现错误', '清空文件夹失败\n' + dir)

    def create_mp4(self):
        video_cache_dir = self.check_video_cache_dir()
        if not video_cache_dir:
            return
        if not create_list.has_file(video_cache_dir):
            return tkinter.messagebox.showerror('错误', '缓存文件夹内没有.ts文件')
        create_list.run(video_cache_dir)
        os.system('sh {}/create_mp4.sh'.format(video_cache_dir))
        pass


if __name__ == '__main__':
    freeze_support()

    root = tkinter.Tk()
    root.title('综艺玩很大 转播程序 v0.3')
    root.iconbitmap(resource_path('./icon.ico'))
    # 禁止改变窗口大小
    root.resizable(False, False)

    # 流程开始

    local = LocalForm(root=root)

    video = VideoUrlForm(root=root)

    url = UrlForm(root=root)

    buttons = ButtonsFrame(root=root, local_frame=local, video_frame=video, url_frame=url)


    def on_closing():
        if buttons.is_start:
            if messagebox.askokcancel('警告', '转播程序正在工作，确认退出？'):
                buttons.stop()
                root.destroy()
        else:
            root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 进入消息循环
    root.mainloop()
