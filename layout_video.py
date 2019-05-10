from tkinter import BOTH, Frame as tkFrame, Button as tkButton, LEFT, RIGHT, DISABLED, messagebox as msgbox, LabelFrame, \
    StringVar, Label as tkLabel, Entry, Radiobutton, W, X,E
from base_layout import Frame as baseFrame
from diskcache import Cache


class Frame(baseFrame):

    def __init__(self, root, my_cache) -> None:
        super().__init__()
        self.layout = layout = LabelFrame(root, text='网络源设置(*为必填)')
        layout.pack(fill=BOTH, padx=5, pady=5)

        # 直播源 选择
        self.__select = select = StringVar()
        my_cache.tkVariable(select, 'video_source_select', '2')
        frame = tkFrame(layout)
        frame.pack(fill=BOTH)
        Radiobutton(frame, text='四季TV视频源（需要台湾IP）', variable=select, value='1').pack(anchor=W)
        Radiobutton(frame, text='软件开发者的视频源（每周六晚21点55分左右开启）', variable=select, value='2').pack(
            anchor=W)
        Radiobutton(frame, text='自填', variable=select, value='3').pack(anchor=W)
        select.trace('w', callback=self.__radio_change)

        # 直播源 输入框
        self.__video_frame = frame = tkFrame(layout)

        tkLabel(frame, text='直播源(*)', width=8, anchor=E).pack(side=LEFT)
        self.__video = StringVar()
        my_cache.tkVariable(self.__video, 'video_url')
        Entry(frame, textvariable=self.__video).pack(fill=X, padx=5, expand=True)

        # 弹幕源 输入框
        self.__danmaku_frame = frame = tkFrame(layout)

        tkLabel(frame, text='弹幕源', width=8, anchor=E).pack(side=LEFT)
        self.__danmaku = StringVar()
        my_cache.tkVariable(self.__danmaku, 'damaku_url')
        Entry(frame, textvariable=self.__danmaku).pack(fill=X, padx=5, expand=True)

        # 代理 输入框
        frame = tkFrame(layout)
        frame.pack(fill=BOTH)
        tkLabel(frame, text='网络代理', width=8, anchor=E).pack(side=LEFT)
        self.__proxy = StringVar()
        my_cache.tkVariable(self.__proxy, 'proxy_url')
        Entry(frame, textvariable=self.__proxy).pack(fill=X, padx=5, expand=True)

        self.__radio_change()

    def __radio_change(self, *args):
        select = self.__select.get()
        if select == '1':
            self.__video.set('1')
            self.__danmaku.set('')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack(fill=BOTH)

        elif select == '2':
            self.__video.set('http://home.js2.me:2333/video/live.m3u8')
            self.__danmaku.set('http://home.js2.me:2333/danmaku')
            self.__video_frame.pack_forget()
            self.__danmaku_frame.pack_forget()

        else:
            self.__video.set('')
            self.__danmaku.set('')
            self.__video_frame.pack(fill=BOTH)
            self.__danmaku_frame.pack(fill=BOTH)

    def video_url(self) -> str:
        return self.__video.get()

    def danmaku_url(self) -> str:
        return self.__danmaku.get()

    def proxy_url(self) -> str:
        return self.__proxy.get()
