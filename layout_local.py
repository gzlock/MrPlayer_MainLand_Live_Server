import os
import subprocess
import tkinter
from sys import platform
from tkinter import filedialog, messagebox
from tkinter import ttk

from base_layout import Frame as baseFrame


class Frame(baseFrame):

    def __init__(self, root, my_cache) -> None:
        super().__init__()

        # 视频 缓存 目录
        self.layout = layout = ttk.LabelFrame(root, text='本地设置')
        layout.config(padding=5)
        layout.pack(fill=tkinter.BOTH, pady=5)

        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Label(frame, text='缓存目录').pack(side=tkinter.LEFT)

        self.__video_cache = tkinter.StringVar()
        my_cache.tkVariable(self.__video_cache, 'video_cache_dir')
        input = ttk.Entry(frame, state='readonly', textvariable=self.__video_cache)
        input.pack(fill=tkinter.X, side=tkinter.LEFT,
                   expand=True)
        self.without_disable.append(input)

        frame = ttk.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Button(frame, text='选择目录', command=self.__select_folder).pack(side=tkinter.RIGHT, padx=2)

        button = ttk.Button(frame, text='打开目录', command=self.__open_video_dir)
        button.pack(side=tkinter.RIGHT, padx=2)
        self.without_disable.append(button)

        # 服务 端口
        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Label(frame, text='网站端口').pack(side=tkinter.LEFT)

        self.__port = tkinter.StringVar()
        my_cache.tkVariable(self.__port, 'website_port', '2333')
        ttk.Entry(frame, textvariable=self.__port).pack(fill=tkinter.BOTH, padx=2, expand=True)

        # 隐藏功能
        self.__show_create_damaku_layout_count = 0

        self.layout.bind('<Button-1>', self.__hidden_func)

        self.__create_damaku = tkinter.IntVar()
        self.__create_damaku.set(0)

        self.__only_video = tkinter.IntVar()
        self.__only_video.set(0)

    def __hidden_func(self, event):
        print('event', event, {'create_damaku': self.create_danmaku(), 'only_video': self.only_video()})
        if event.x < 50 and event.y < 50:
            self.__show_create_damaku_layout_count += 1
        if self.__show_create_damaku_layout_count == 5:
            self.__show_create_danmaku_layout()

    def __select_folder(self):
        dir = tkinter.filedialog.askdirectory(title='选择要存放视频缓存的目录')
        if len(dir) > 0:
            self.__video_cache.set(dir)

    def __open_video_dir(self):
        dir = self.__video_cache.get()
        if len(dir) == 0:
            return messagebox.showerror('错误', '没有选择视频缓存文件夹')
        if not os.path.exists(dir):
            return messagebox.showerror('错误', '不存在的视频缓存文件夹，无法打开')

        if platform == 'win32':
            os.startfile(dir)
        elif platform == 'darwin':
            subprocess.Popen(['open', dir])

    def port(self) -> str:
        return self.__port.get()

    def video_cache_dir(self) -> str:
        return self.__video_cache.get()

    def create_danmaku(self) -> bool:
        return self.__create_damaku.get() == 1

    def only_video(self) -> bool:
        return self.__only_video.get() == 1

    def __show_create_danmaku_layout(self):
        frame = ttk.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        self.__create_damaku.set(1)
        ttk.Checkbutton(frame, text='自建弹幕池(覆盖弹幕源)', variable=self.__create_damaku, onvalue=1).pack(
            side=tkinter.LEFT, padx=5)

        frame = ttk.Frame(self.layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Checkbutton(frame, text='禁止打开首页(只允许访问 /video 资源)', variable=self.__only_video).pack(
            side=tkinter.LEFT, padx=5)
