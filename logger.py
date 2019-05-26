import sys
import tkinter
import os
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from my_cache import log_file


class Logger:
    def __init__(self, root):
        self.printer = sys.stdout
        sys.stdout = self
        self.__root = root
        self.__is_open: bool = False
        self.__window: tkinter.Toplevel = None
        self.__text_view: tkinter.Text = None

        # 是否滚动到底部，默认滚动
        self.__is_scroll_to_bottom = tkinter.IntVar()
        self.__is_scroll_to_bottom.set(1)

        self.__read_line = 0

    def loop(self):
        if os.path.exists(log_file) and self.__is_open:
            with open(log_file, 'r+') as file:
                lines = file.readlines()[self.__read_line:]
                if lines:
                    self.__read_line += len(lines)
                    self.__text_view.config(state=tkinter.NORMAL)

                    line = ''
                    for text in lines:
                        # if text.endswith('\r') or text.endswith('\n'):
                        #     self.__text_view.insert(tkinter.END, line + text + '\n')
                        #     line = ''
                        # else:
                        #     line += text
                        self.__text_view.insert(tkinter.END, text + '\n')

                    self.__text_view.config(state=tkinter.DISABLED)

                    if self.__is_scroll_to_bottom.get() == 1:
                        self.__text_view.see('end')

        self.__root.after(100, self.loop)

    def open(self):
        if not self.__is_open:
            self.__window = tkinter.Toplevel(self.__root)
            self.__window.title('日志窗口')
            self.__window.geometry('500x500')
            self.__window.protocol("WM_DELETE_WINDOW", self.close)
            frame = ttk.Frame(self.__window)
            frame.pack(fill=tkinter.BOTH, expand=True)
            ttk.Button(frame, text='清空日志', command=lambda: self.clear()).pack()
            ttk.Checkbutton(frame, text='自动滚动到底部', variable=self.__is_scroll_to_bottom).pack()
            self.__text_view = ScrolledText(frame, state=tkinter.DISABLED)
            self.__text_view.pack(fill=tkinter.BOTH, expand=True)
            self.__text_view.bind("<1>", lambda event: self.__text_view.focus_set())
            self.__is_open = True

    def close(self):
        self.__read_line = 0
        self.__is_open = False
        try:
            self.__window.destroy()
        except:
            pass

    def write(self, args):
        args = str(args)
        self.printer.write(args)
        with open(log_file, 'a+') as file:
            file.write(args)

    def flush(self):
        pass

    def clear(self):
        self.printer.write('清空日志')
        self.__read_line = 0
        with open(log_file, 'w') as file:
            file.write('')
        if self.__is_open:
            self.__text_view.config(state=tkinter.NORMAL)
            self.__text_view.delete(1.0, tkinter.END)
            self.__text_view.config(state=tkinter.DISABLED)

    def is_open(self):
        return self.__is_open
