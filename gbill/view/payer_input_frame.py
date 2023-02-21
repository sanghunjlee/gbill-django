from typing import List
import tkinter as tk
import tkinter.ttk as ttk

from ..tools.tools import stof

class PayerInputFrame(tk.Frame):
    _index: int
    state: bool
    values: List[str]
    name: tk.StringVar
    amnt: tk.StringVar
    def __init__(self, parent, index: int, values: List[str] = [], name: str = '', amount: str = '', *args, **kwargs):
        self._index = index
        self.state = True
        self.values = values
        self.parent = parent
        super().__init__(parent, *args, **kwargs)
        self.name = tk.StringVar(self, name if len(values) > 0 else f'Name {self._index}')
        self.amnt = tk.StringVar(self, amount)
        
        del_btn = tk.Button(self, text='X', anchor='w', relief='flat', command=self.del_this)
        name_lbl = tk.Label(self, text='Payer Name:')
        self.name_cbx = ttk.Combobox(self, values=self.values, textvariable=self.name)
        amnt_lbl = tk.Label(self, text='Amount: ')
        amnt_ent = tk.Entry(self, textvariable=self.amnt)

        self.name_cbx.bind('<FocusIn>', self.payer_update)

        self.columnconfigure(2, weight=9)
        del_btn.grid(column=0, row=0, padx=4)
        name_lbl.grid(column=1, row=0, sticky='ew', padx=2)
        self.name_cbx.grid(column=2, row=0, sticky='ew', padx=2)
        amnt_lbl.grid(column=3, row=0, sticky='ew', padx=2)
        amnt_ent.grid(column=4, row=0, sticky='ew', padx=2)
    
    def get_values(self):
        return (self.name.get(), stof(self.amnt.get()))

    def payer_update(self, *args):
        self.event_generate('<<PayerUpdate>>')

    def del_this(self):
        self.state = False
        self.event_generate('<<delpayer>>')
