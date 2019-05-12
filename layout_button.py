import os
import subprocess
import tkinter
from tkinter import ttk
from multiprocessing import Process
from shutil import rmtree
from sys import platform
from time import sleep
from tkinter import messagebox

import create_list
import layout_local
import layout_url
import layout_video
import m3u8
import server
import utils
from test_connect import test_connect


class Frame:
    __m3u8_process = None
    __server_process = None

    def __init__(self, root, local_frame: layout_local.Frame, video_frame: layout_video.Frame,
                 url_frame: layout_url.Frame, my_cache) -> None:
        super().__init__()
        self.my_cache = my_cache
        self.root = root

        frame = ttk.Frame(root)
        frame.pack(fill=tkinter.X, padx=5, pady=5, side=tkinter.BOTTOM)

        self.local_frame = local_frame
        self.video_frame = video_frame
        self.url_frame = url_frame

        # 启动 服务
        self.start_btn = start_btn = ttk.Button(frame, text='启动转播', command=self.start)
        start_btn.pack(side=tkinter.LEFT)

        # 停止 服务
        self.stop_btn = stop_btn = ttk.Button(frame, text='停止转播', command=self.stop, state=tkinter.DISABLED)
        stop_btn.pack(side=tkinter.LEFT, padx=5, pady=5)

        # 合并视频文件
        self.create_mp4_btn = create_mp4_btn = ttk.Button(frame, text='合并视频', command=self.create_mp4)
        create_mp4_btn.pack(side=tkinter.LEFT)

        # 清空视频缓存
        self.clear_cache_btn = clear_cache_btn = ttk.Button(frame, text='清空缓存', command=self.clear_cache)
        clear_cache_btn.pack(side=tkinter.RIGHT)

        self.is_start = False

        self.stop()

    # 检查缓存目录
    def check_video_cache_dir(self):
        video_cache_dir = self.local_frame.video_cache_dir()
        if len(video_cache_dir) == 0:
            messagebox.showerror('错误', '请选择缓存目录')
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
        if not utils.is_int(port):
            return messagebox.showerror('错误', '端口只能是数字')
        port = int(port)
        if port < 2000 or port > 60000:
            return messagebox.showerror('错误', '端口只能从2000到60000')

        create_danmaku: bool = self.local_frame.create_danmaku()

        # print(video_cache_dir, port)

        # 检查 三个网址
        video_url = self.video_frame.video_url()
        danmaku_url = self.video_frame.danmaku_url()
        proxy_url = self.video_frame.proxy_url()

        if create_danmaku:
            print('自建弹幕')
            danmaku_url = '1'

        # print(video_url, danmaku_url, proxy_url)

        if len(video_url) == 0:
            return messagebox.showerror('错误', '请填写视频源网址')
        else:
            if video_url != '1' and not utils.is_url(video_url):
                return messagebox.showerror('错误', '视频源的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        if danmaku_url != '1':
            if len(danmaku_url) > 0 and not utils.is_url(danmaku_url):
                return messagebox.showerror('错误', '弹幕源的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        if len(proxy_url) > 0:
            if not utils.is_url(proxy_url):
                return messagebox.showerror('错误', '代理的格式错误，只接受:\nhttp:\\\\xxx\n的格式')

        check = test_connect(video_url, proxy_url)
        if check != 'ok':
            has_proxy = len(proxy_url) > 0
            title = '连接错误'
            if has_proxy:
                title = '代理服务器出现错误'
            message = title
            if check == 'NeedTWIP':
                message = '四季TV网络视频源 需要台湾IP'
            elif check == 'ProxyError':
                message = '连接不到代理服务器'
            elif check == 'NotM3u8':
                message = '网络视频源 返回的不是M3u8文件格式'
            elif check == 'TimeOut':
                message = '连接 网络视频源 超时(5秒)'
            return messagebox.showerror(title, message)

        self.__m3u8_process = Process(target=m3u8.run,
                                      args=(video_cache_dir, video_url, proxy_url, self.my_cache.cache))
        self.__m3u8_process.start()

        only_video = self.local_frame.only_video()
        self.__server_process = Process(target=server.run, args=(port, video_cache_dir, danmaku_url, only_video))
        self.__server_process.start()

        return '123ok'

    def start(self):
        self.my_cache.cache.set('m3u8_stop', False)
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
        self.my_cache.cache.set('m3u8_stop', True)

        if self.__server_process is not None:
            self.__m3u8_process.kill()
            self.__server_process.kill()
            self.__m3u8_process = None
            self.__server_process = None

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
            true = true and messagebox.askokcancel(title.format(i + 1),
                                                   dir + '\n将会清空视频缓存文件夹内所有文件，确认清空？')
            i += 1
        if not true:
            return
        if os.path.exists(dir):
            try:
                rmtree(dir)
                sleep(0.2)
                os.mkdir(dir)
                messagebox.showinfo('清理完成', '成功清空视频缓存文件夹')
            except Exception as e:
                messagebox.showerror('出现错误', '清空文件夹失败\n' + dir + '\n' + e.__str__())

    def create_mp4(self):
        if not utils.has_ffmpeg():
            return messagebox.showerror('错误', '没有安装 ffmpeg')

        video_cache_dir = self.check_video_cache_dir()
        if not video_cache_dir:
            return
        if not create_list.has_file(video_cache_dir):
            return messagebox.showerror('错误', '缓存文件夹内没有.ts文件')

        create_list.save(video_cache_dir)

        list_path = os.path.normpath(os.path.join(video_cache_dir, 'list.txt'))
        final_mp4_path = os.path.normpath(os.path.join(video_cache_dir, 'final.mp4'))

        command_line = 'ffmpeg -f concat -safe 0 -i {} -c copy {} -y'.format(list_path, final_mp4_path)

        if platform == 'win32':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(command_line, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, startupinfo=si)
        else:
            process = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       env=utils.popen_env())

        win = tkinter.Toplevel()
        tkinter.Label(win, text='正在合并视频文件中，请稍候', font=('times', 20, 'bold')).pack(padx=10, pady=10)
        win.resizable(0, 0)
        win.after(100, utils.move_to_screen_center, win)

        def check():
            return_code = process.poll()
            print('return_code', return_code)
            if return_code is None:
                win.after(100, check)
                return

            win.grab_release()
            win.destroy()
            if return_code == 0:
                if messagebox.askyesno('合并文件成功', '是否打开文件夹？'):
                    if platform == 'win32':
                        os.startfile(final_mp4_path)
                        # subprocess.Popen('explorer /select,"{}"'.format(final_mp4_path))
                    else:
                        subprocess.Popen(['open', '-R', final_mp4_path])
            else:
                messagebox.showinfo('合并视频文件错误', process.stdout.read())

        win.after(100, check)

        def on_closing():
            if messagebox.askokcancel('警告', '正在合并视频，关闭这个窗口将会中断合并视频'):
                process.kill()
                win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        win.grab_set()
