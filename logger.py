import sys
import tkinter
from tkinter import ttk
from multiprocessing import Manager
from tkinter.scrolledtext import ScrolledText


class Logger:
    def __init__(self, root):
        self.printer = sys.stdout
        sys.stdout = self
        self.__root = root
        self.__is_open: bool = False
        self.__window: tkinter.Toplevel = None
        self.__text_view: tkinter.Text = None
        self.__message_list = Manager().list()
        self.__is_scroll_to_bottom = tkinter.IntVar()
        self.__is_scroll_to_bottom.set(1)
        self.__inserted_line = 0

    def loop(self):
        lines = len(self.__message_list)
        if self.__is_open and self.__inserted_line < lines:
            # self.printer.write('有新的日志\n')

            self.__text_view.config(state=tkinter.NORMAL)

            i = 0
            line = ''
            for text in self.__message_list[self.__inserted_line:]:
                i += 1
                if text.endswith('\r') or text.endswith('\n'):
                    self.__text_view.insert(tkinter.INSERT, line + text + '\n')
                    line = ''
                else:
                    line += text

            self.__text_view.config(state=tkinter.DISABLED)

            # self.printer.write('写入:' + str(i) + ' 行\n')

            if self.__is_scroll_to_bottom.get() == 1:
                self.__text_view.see('end')

            self.__inserted_line = lines
            self.__text_view.update()

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
            self.__is_open = True

    def close(self):
        self.__inserted_line = 0
        self.__is_open = False
        try:
            self.__window.destroy()
        except:
            pass

    def write(self, args):
        args = str(args)
        self.printer.write(args)
        self.__message_list.append(args)

    def flush(self):
        pass

    def clear(self):
        self.__message_list[:] = []
        self.__inserted_line = 0
        if self.__is_open:
            self.printer.write('清空日志')
            self.__text_view.config(state=tkinter.NORMAL)
            self.__text_view.delete(1.0, tkinter.END)
            self.__text_view.config(state=tkinter.DISABLED)

    def is_open(self):
        return self.__is_open
