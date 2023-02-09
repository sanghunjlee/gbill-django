import tkinter as tk

from ..tools.tools import center

class Window(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ret = None

    def show(self):
        center(self)
        self.wm_transient(self.parent)
        self.grab_set()
        self.focus_set()
        self.deiconify()
        self.wm_protocol('WM_DELETE_WINDOW', self.destroy)
        self.wait_window(self)
        return self.ret