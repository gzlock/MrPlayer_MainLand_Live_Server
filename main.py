import sys
import tkinter
from multiprocessing import freeze_support
from sys import platform
from tkinter import messagebox
from tkinter.ttk import Frame

import github_update
import layout_button
import layout_local
import layout_url
import layout_video
import menu
import mul_process_package
import my_cache
import resource_path
import utils
from logger import Logger

mul_process_package.ok()

cache = my_cache.cache

version: float = 0.85

if __name__ == '__main__':
    freeze_support()

    cache.set('m3u8_stop', False)

    root = tkinter.Tk()
    root.title('综艺玩很大 转播程序 v' + str(version))
    # 设置windows窗口图标
    if platform == 'win32':
        icon = resource_path.path('icon.ico')
        print('icon', icon)
        root.iconbitmap(icon)

    # 禁止改变窗口大小
    # root.resizable(False, False)
    root.minsize(450, 650)
    frame = Frame(root)
    frame.config(padding=5)
    frame.pack(fill=tkinter.BOTH, expand=True)

    # 流程开始

    logger = Logger(root)
    logger.loop()

    menu = menu.Menu(root=root, cache=cache, logger=logger)

    local = layout_local.Frame(root=frame, my_cache=my_cache)

    video = layout_video.Frame(root=frame, my_cache=my_cache)

    url = layout_url.Frame(root=frame)

    buttons = layout_button.Frame(root=frame, local_frame=local, video_frame=video, url_frame=url, my_cache=my_cache,
                                  logger=logger)

    root.after(100, utils.move_to_screen_center, root)


    def on_closing():
        if buttons.is_start:
            if messagebox.askokcancel('警告', '转播程序正在工作，确认退出？'):
                buttons.stop()
                root.destroy()
        else:
            root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)

    with open(my_cache.log_file, 'w+') as file:
        file.write('')

    # 检查 更新
    root.after(2000, lambda: github_update.UpdateSoftware(root=root, cache=cache, current_version=version))
    # 进入消息循环
    root.mainloop()
    # 关闭主窗口
    print('退出程序')
    cache.set('m3u8_stop', True)
    sys.exit(0)
