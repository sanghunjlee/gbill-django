from typing import Any, List
import tkinter as tk
from tkinter import font as tkFont

from .vertical_scrolled_frame import VerticalScrolledFrame

class BillListBox(VerticalScrolledFrame):
    listvariable: List[Any]
    cur_selection: tk.IntVar
    normal_font: tkFont.Font
    bold_font: tkFont.Font

    def __init__(self, parent, listvariable: List[Any]=[], *args, **kw):
        super().__init__(parent, *args, **kw)
        self.normal_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.normal_font.config(size=9, weight=tkFont.NORMAL)
        self.bold_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.bold_font.config(size=9, weight=tkFont.BOLD)
        self.cur_selection = tk.IntVar(self, -1)
        self.cur_selection.trace_add('write', self.update_selection)
        self.listvariable = listvariable
        self.update_list()

    def update_list(self):
        for _ in self.interior.winfo_children():
            _.destroy()
        _header = ' '.join(('#'.ljust(3), 'DESCR'.ljust(32), 'PAYEE'.ljust(16), 'AMOUNT'.rjust(9)))
        header_lbl = tk.Label(self.interior, anchor='w', font=self.bold_font, text=_header, padx=4, pady=4)
        header_lbl.pack(side=tk.TOP, fill=tk.X, expand=True, pady=1)
        for indx, var in enumerate(self.listvariable):
            _txt = ' '.join((str(indx+1).ljust(3), var.descr[:32].ljust(32), var.payee[:16].ljust(16), str(var.amount).rjust(9)))
            self.__setattr__(
                f'BTN{indx}', 
                tk.Button(self.interior, anchor='w', text=_txt, padx=4, pady=4, command=lambda i=indx: self.btn_pressed(i))
            )
            self.__getattribute__(f'BTN{indx}').pack(side=tk.TOP, fill=tk.X, expand=True, pady=1)

    def set_list(self, listvariable: List[Any]):
        self.listvariable = listvariable
        self.update_list()
        self.cur_selection.set(-1)

    def btn_pressed(self, indx):
        if self.cur_selection.get() != indx:
            self.cur_selection.set(indx)
        else:
            self.cur_selection.set(-1)

    def update_selection(self, *args):
        sel = self.cur_selection.get()
        for i in range(len(self.listvariable)):
            if i == sel:
                self.__getattribute__(f'BTN{i}').config(font=self.bold_font)
            else:
                self.__getattribute__(f'BTN{i}').config(font=self.normal_font)
