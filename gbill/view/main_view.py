#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkm
from tkinter import filedialog as tkf
from tkinter import font as tkFont
from typing import Dict, Any, List, Optional

from .bill_list_box import BillListBox
from .message_view import MessageView
from .trans_input_view import TransInputView

from ..model.invoice import Invoice, Transaction
from ..tools.tools import stof, rmv_dups, print_array
from ..globals import APP_DIR

WIN_WIDTH = 600
WIN_HEIGHT = 400


class MainView(tk.Frame):
    _state: int
    _loaded: bool
    _edited: bool
    filepath: Optional[str]
    invoice: Invoice
    sv_bill: tk.StringVar
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self._state = 0
        self._loaded = False
        self._edited = False
        self.filepath = None
        self.parent = parent
        self.invoice = Invoice()
        
        self.init_ui()
        self.grid_ui()
        self.update_ui()

    def init_ui(self):
        # Menu setup
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=False)
        filemenu.add_command(label='New', command=self.do_new, underline=0)
        filemenu.add_command(label='Open', command=self.do_open, underline=0)
        filemenu.add_command(label='Save', command=self.do_save, underline=0)
        filemenu.add_command(label='Close', command=self.do_close, underline=0)
        menubar.add_cascade(label='File', menu=filemenu, underline=0)

        # Widgets setup
        self.top = tk.Frame(self)
        self.ppl_lfm = tk.LabelFrame(self.top, text="Group")
        # TODO: Change ppl_disp from Label to Canvas to allow graphics
        self.ppl_disp = tk.Label(self.ppl_lfm, anchor='w')
        self.lfrm = tk.LabelFrame(self, text="Transactions")
        self.bill_lbx = BillListBox(self.lfrm, width=500)
        self.rfrm = tk.Frame(self)
        self.add_btn = tk.Button(self.rfrm, width=10, text='Add', command=self.add_btn_pressed)
        self.mod_btn = tk.Button(self.rfrm, width=10, text='Edit', command=self.mod_btn_pressed)
        self.del_btn = tk.Button(self.rfrm, width=10, text='Delete', command=self.del_btn_pressed)
        self.clr_btn = tk.Button(self.rfrm, width=10, text='Clear', command=self.clr_btn_pressed)
        self.bot = tk.Frame(self)
        self.inv_btn = tk.Button(self.bot, height=2 , text='INVOICE', command=self.inv_btn_pressed)


    def grid_ui(self):
        self.grid(column=0, row=0, padx=4, pady=4)
        self.top.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=4, pady=(0, 16))
        self.ppl_lfm.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.ppl_disp.pack(side=tk.TOP, fill=tk.X, expand=True, padx=8, pady=4)
        self.lfrm.grid(column=0, row=1, sticky='nsew', padx=4, pady=0)
        self.bill_lbx.grid(column=0, row=0, sticky='ns', padx=4, pady=(4, 8))
        self.rfrm.grid(column=1, row=1, sticky='nsew', padx=4, pady=0)
        self.add_btn.grid(column=0, row=0, sticky='ew')
        self.mod_btn.grid(column=0, row=1, sticky='ew')
        self.del_btn.grid(column=0, row=2, sticky='ew')
        self.clr_btn.grid(column=0, row=3, sticky='ew')
        self.bot.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=4, pady=(8, 4))
        self.inv_btn.pack(fill=tk.X, side=tk.TOP, expand=True)

    def add_btn_pressed(self):
        tiv = TransInputView(self)
        resp = tiv.show()
        if resp:
            self.invoice.add_transaction(resp)
            self._state = 1

    def mod_btn_pressed(self):
        selection = self.bill_lbx.cur_selection.get()
        if selection >= 0:
            old_trans = self.invoice[selection]
            tiv = TransInputView(self, init_val=old_trans)
            new_trans = tiv.show()
            if new_trans:
                self.invoice[selection] = new_trans
                self._state = 1
            
    def del_btn_pressed(self):
        selection = self.bill_lbx.cur_selection.get()
        if selection >= 0:
            self.invoice.pop(selection)
            self._state = 1

    def clr_btn_pressed(self):
        self.invoice.clear()
        self._state = 1

    def inv_btn_pressed(self):
        mv = MessageView(self)
        mmsg = print_array(self.invoice.list_matrix(), 'c/cr', padx=2, top='F R O M', left='TO', title='Total Amount Owed')
        mv.add(mmsg)
        amsg = print_array(self.invoice.list_all(), 'c/lr', footer='\n')
        mv.add(amsg)
        for i, t in enumerate(self.invoice.invoice()):
            mv.add(f'{str(i).zfill(2)} : {t.descr}' + '\n')
        mv.show()

    def do_new(self):
        do_continue = tkm.askyesno(
            title='Confirmation',
            message='This will clear any unsaved progress. Do you wish to continue?',
        )
        if do_continue:
            self._loaded = False
            self._edited = False
            self.filepath = None
            self.clr_btn_pressed()

    def do_save(self):
        if not self._edited:
            return

        if self.filepath is None:
            fpath = tkf.asksaveasfilename(parent=self, title='Save', initialdir=APP_DIR, filetypes=(('Save File', '*.gbs'),))
            if not fpath.endswith('.gbs'):
                fpath = fpath + '.gbs'
            print(fpath)
            self.filepath = fpath
        print(self.invoice.save())
        try:
            with open(self.filepath, mode='w') as wf:
                save_data = self.invoice.save()
                wf.write(save_data)
            self._edited = False
        except OSError:
            print('do_save: oserror')

    def do_open(self):
        if self._edited or self._loaded:
            _msg = 'This will clear any unsaved progress. Do you wish to continue?'
            if self._loaded:
                _msg = 'This will clear the current bills. Do you with to continue?'
            do_continue = tkm.askyesno(
                title='Confirmation',
                message=_msg,
            )
            if not do_continue:
                return
        fpath = tkf.askopenfilename(parent=self, title='Open', initialdir=APP_DIR, filetypes=(('Save File', '*.gbs'),))
        try:
            with open(fpath, mode='r') as rf:
                load_data = '\n'.join(rf.readlines())
            if self.invoice.load(load_data):
                self._edited = False
                self._loaded = True
                self.filepath = fpath
                self._state = 1
        except OSError:
            print('do_open: oserror')
                

    def do_close(self):
        pass

    def update_ui(self):
        if self._state == 1:
            self.ppl_disp.config(text=','.join(self.invoice.get_payers()))
            self.bill_lbx.set_list(self.invoice.trans)
            self._edited = True
            self._state = 0
        self.after(50, self.update_ui)

""" def draw_roundRect(canvas: tk.Canvas, x: int, y: int, w: int, h: int, radius=25, **kwargs):
        x1, x2 = x+radius, x+w-radius
        y1, y2 = y+radius, y+h-radius

        points = (
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        )
        return canvas.create_polygon(points, **kwargs, smooth=True) """

def init_app(app_name, version):
    root = tk.Tk()
    root.title(f"{app_name} v.{version}")
    app = MainView(root)
    app.mainloop()

def test():
    root = tk.Tk()
    mv = MessageView(root)
    testmsg = '''Hello **world** this is *exciting* feature for ***you***!'''
    mv.add(testmsg)
    mv.show()

if __name__ == '__main__':
    test()
    #init_app('test', '0.0.dev')
