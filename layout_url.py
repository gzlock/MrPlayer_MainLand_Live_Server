import tkinter
from tkinter import ttk
from webbrowser import open

from pyperclip import copy

from base_layout import Frame as baseFrame

import utils


class Frame(baseFrame):

    def __init__(self, root) -> None:
        super().__init__()
        self.layout = layout = ttk.LabelFrame(root, text='向其他人分享您的：')
        layout.config(padding=5)
        layout.pack(fill=tkinter.BOTH, pady=5)
        self.lan_ip = tkinter.StringVar()
        self.wan_ip = tkinter.StringVar()

        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Label(frame, text='局域网网址').pack(side=tkinter.LEFT)
        input = ttk.Entry(frame, textvariable=self.lan_ip, state='readonly')
        input.pack(fill=tkinter.BOTH)
        self.without_disable.append(input)

        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Button(frame, text='打开', command=lambda: open(self.lan_ip.get())).pack(side=tkinter.RIGHT)
        ttk.Button(frame, text='复制', command=lambda: copy(self.lan_ip.get())).pack(side=tkinter.RIGHT, padx=5)

        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Label(frame, text='广域网网址').pack(side=tkinter.LEFT)
        input = ttk.Entry(frame, textvariable=self.wan_ip, state='readonly')
        input.pack(fill=tkinter.BOTH)
        self.without_disable.append(input)

        frame = ttk.Frame(layout)
        frame.pack(fill=tkinter.BOTH, pady=5)
        ttk.Button(frame, text='打开', command=lambda: open(self.wan_ip.get())).pack(side=tkinter.RIGHT)
        ttk.Button(frame, text='复制', command=lambda: copy(self.wan_ip.get())).pack(side=tkinter.RIGHT, padx=5)

    def show(self):
        self.layout.pack()

    def hide(self):
        self.layout.pack_forget()

    def set_ip(self, port: str):
        url = 'http://{}:{}'
        self.lan_ip.set(url.format(utils.get_lan_ip(), port))
        self.wan_ip.set(url.format(utils.get_wan_ip(), port))

    def clear_ip(self):
        self.lan_ip.set('')
        self.wan_ip.set('')
