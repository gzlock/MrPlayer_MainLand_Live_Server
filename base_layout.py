import tkinter
from tkinter import ttk

frameList = [tkinter.Frame, tkinter.LabelFrame, ttk.Frame, ttk.LabelFrame, tkinter.Toplevel]


class Frame:
    layout: tkinter.Widget
    without_disable: list = []

    def disable(self, disabled: bool):
        state = tkinter.NORMAL
        if disabled:
            state = tkinter.DISABLED
        Frame.disable_child(self.layout, state=state, without=self.without_disable)

    @staticmethod
    def disable_child(frame: tkinter.Widget, state, without: list):
        for child in frame.winfo_children():
            if type(child) in frameList:
                Frame.disable_child(child, state, without=without)
            elif child not in without:
                child.config(state=state)
