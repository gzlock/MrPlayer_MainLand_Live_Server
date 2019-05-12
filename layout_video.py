import tkinter
from tkinter import ttk

from base_layout import Frame as baseFrame


class Frame(baseFrame):

    def __init__(self, root, my_cache) -> None:
        super().__init__()
        self.layout = layout = ttk.LabelFrame(root, text='网络源设置(*为必填)')
        layout.config(padding=5)
        layout.pack(fill=tkinter.BOTH, pady=5)

        # 直播源 选择
        self.__select = select = tkinter.StringVar()
        my_cache.tkVariable(select, 'video_source_select', '2')
        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH)
        ttk.Radiobutton(frame, text='四季TV视频源（需要台湾IP）', variable=select, value='1').pack(anchor=tkinter.W)
        ttk.Radiobutton(frame, text='软件开发者的视频源（每周六晚21点55分左右开启）', variable=select, value='2').pack(
            anchor=tkinter.W)
        ttk.Radiobutton(frame, text='自填', variable=select, value='3').pack(anchor=tkinter.W)
        select.trace('w', callback=self.__radio_change)

        # 直播源 输入框
        self.__video_frame = frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=2)

        ttk.Label(frame, text='直播源(*)', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT)
        self.__video = tkinter.StringVar()
        my_cache.tkVariable(self.__video, 'video_url')
        ttk.Entry(frame, textvariable=self.__video).pack(fill=tkinter.BOTH, expand=True)

        # 弹幕源 输入框
        self.__danmaku_frame = frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=2)

        ttk.Label(frame, text='弹幕源', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT)
        self.__danmaku = tkinter.StringVar()
        my_cache.tkVariable(self.__danmaku, 'damaku_url')
        ttk.Entry(frame, textvariable=self.__danmaku).pack(fill=tkinter.X, expand=True)

        # 代理 输入框
        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=2)
        ttk.Label(frame, text='网络代理', width=8, anchor=tkinter.E).pack(side=tkinter.LEFT)
        self.__proxy = tkinter.StringVar()
        my_cache.tkVariable(self.__proxy, 'proxy_url')
        ttk.Entry(frame, textvariable=self.__proxy).pack(fill=tkinter.X, expand=True)

        self.__radio_change()

    def __radio_change(self, *args):
        select = self.__select.get()
        if select == '1':
            self.__video.set('1')
            self.__danmaku.set('')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack(fill=tkinter.BOTH, pady=2)

        elif select == '2':
            self.__video.set('http://home.js2.me:2333/video/live.m3u8')
            self.__danmaku.set('http://home.js2.me:2333/danmaku')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack_forget()

        else:
            self.__video.set('')
            self.__danmaku.set('')
            self.__video_frame.pack(fill=tkinter.BOTH, pady=2)
            self.__danmaku_frame.pack(fill=tkinter.BOTH, pady=2)

    def video_url(self) -> str:
        return self.__video.get()

    def danmaku_url(self) -> str:
        return self.__danmaku.get()

    def proxy_url(self) -> str:
        return self.__proxy.get()
