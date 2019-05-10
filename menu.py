from tkinter import Menu as tkMenu
from webbrowser import open


class Menu:
    def __init__(self, root, cache) -> None:
        super().__init__()
        self.menu = menubar = tkMenu(root)
        root.config(menu=menubar)

        helpmenu = tkMenu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=helpmenu)

        helpmenu.add_command(label="清空输入框的缓存", command=lambda: cache.clear())
        helpmenu.add_command(label="报告软件问题(QQ群)", command=lambda: open(
            'https://shang.qq.com/wpa/qunwpa?idkey=c93fa2d0819d8405ed6468d48126e7ac2644a716dec65b4353355944ec6a426f'))
        helpmenu.add_command(label="本软件开源(Github)", command=lambda: open(
            'https://github.com/gzlock/mrplayer_mainland_live_server'))
        helpmenu.add_command(label="百度吴宗宪贴吧", command=lambda: open(
            'http://tieba.baidu.com/f?kw=%E5%90%B4%E5%AE%97%E5%AE%AA&ie=utf-8'))
