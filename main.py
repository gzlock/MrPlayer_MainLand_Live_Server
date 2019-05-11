import sys
import tkinter
from multiprocessing import freeze_support
from tkinter import messagebox
from sys import platform

import layout_button
import layout_local
import layout_url
import layout_video
import menu
import mul_process_package
import my_cache
import resource_path
import utils

mul_process_package.ok()

cache = my_cache.cache

if __name__ == '__main__':
    freeze_support()

    cache.set('m3u8_stop', False)

    root = tkinter.Tk()
    root.title('综艺玩很大 转播程序 v0.6')
    # 设置windows窗口图标
    if platform == 'win32':
        icon = resource_path.path('icon.ico')
        print('icon', icon)
        root.iconbitmap(icon)

    # 禁止改变窗口大小
    root.resizable(False, False)
    root.minsize(450, 550)

    # 流程开始

    menu = menu.Menu(root=root, cache=cache)

    local = layout_local.Frame(root=root, my_cache=my_cache)

    video = layout_video.Frame(root=root, my_cache=my_cache)

    url = layout_url.Frame(root=root)

    buttons = layout_button.Frame(root=root, local_frame=local, video_frame=video, url_frame=url, my_cache=my_cache)

    root.after(100, utils.move_to_screen_center, root)


    def on_closing():
        if buttons.is_start:
            if messagebox.askokcancel('警告', '转播程序正在工作，确认退出？'):
                buttons.stop()
                root.destroy()
        else:
            root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.update()

    # 进入消息循环
    root.mainloop()
    print('退出程序')
    cache.set('m3u8_stop', True)
    sys.exit(0)
