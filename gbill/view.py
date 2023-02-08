import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkm
from tkinter import filedialog as tkf
from tkinter import font as tkFont
import tkhtmlview as tkh
from typing import Dict, Any, List, Optional

from .model import Invoice, Transaction
from .tools import stof, rmv_dups, print_array
from .globals import APP_DIR

WIN_WIDTH = 600
WIN_HEIGHT = 400

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        _width = kw.get('width', None)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        if _width:
            self.canvas.config(width=_width)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscrollbar.config(command=self._yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(self.canvas)
        if _width:
            self.interior.config(width=_width)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                '''# Update the canvas's width to fit the inner frame.
                self.canvas.config(width=self.interior.winfo_reqwidth())'''
                # Update the interior's width to fit the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                #print('canvas', self.canvas.winfo_width())
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.interior.winfo_reqheight() > self.canvas.winfo_height():
            delta = (event.delta/120)
            self.canvas.yview_scroll(int(-1*delta), "units")

    def _yview(self, *args):
        if self.interior.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview(*args)

class MessageView(tk.Toplevel):
    def __init__(self, parent, message: str = '', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.msg = tk.StringVar(self, message)
        self.normal_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.normal_font.config(size=9, weight=tkFont.NORMAL)
        
        display_frame = VerticalScrolledFrame(self, width=580, height=500)
        button_frame = tk.Frame(self)
        msg_label = tk.Label(display_frame.interior, anchor='nw', justify='left', textvariable=self.msg, font=self.normal_font)
        close_btn = tk.Button(button_frame, text='Close', command=lambda: self.destroy())

        display_frame.pack(side='top', fill='both', expand=True, padx=4, pady=4)
        button_frame.pack(side='bottom', fill='both', expand=False, padx=4, pady=4)
        msg_label.pack(side='top', fill='both', expand=True)
        close_btn.pack(side='right', fill='x', expand=True)
    
    def add_msg(self, message: str = ''):
        _msg = self.msg.get()
        self.msg.set(_msg + '\n' + message)

    def show(self):
        center(self)
        self.resizable(False, False)
        self.wm_transient(self.parent)
        self.grab_set()
        self.focus_set()
        self.deiconify()
        self.wm_protocol('WM_DELETE_WINDOW', self.destroy)
        self.wait_window(self)
        return


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

class TransInputView(tk.Toplevel):
    ret: Transaction
    pifs: List[PayerInputFrame|tk.Button]
    ppl_list: List[str]
    def __init__(self, parent, init_val: Optional[Transaction] = None):
        super().__init__(parent)
        self.parent = parent
        self.ppl_list = self.parent.invoice.get_payers()
        self.sv_descr = tk.StringVar()
        self.sv_payee = tk.StringVar()
        self.sv_amount = tk.StringVar()
        self.ret = init_val
        self.pifs = []
        self.init_ui()
        self.bind_ui()
        self.grid_ui()
        if self.ret:
            self.sv_descr.set(self.ret.descr)
            self.sv_payee.set(self.ret.payee)
            self.sv_amount.set(str(self.ret.amount))
            for k,v in self.ret.distribution.items():
                self.add_new_payer(name=k, amount=str(v))

    def init_ui(self):
        instruction = '\n'.join((
            "Auto Calc button will do the following:",
            "\t* Automatically distribute the total amount amongst all the payer listed, and",
            "\t* Automatically calcuate and add the tips & tax if the payers' amounts are",
            "\t  filled out but sum to less than the total amount."
        ))

        self.main_frm = tk.Frame(self)
        self.descr_lbl = tk.Label(self.main_frm, text='Description:')
        self.descr_ent = tk.Entry(self.main_frm, textvariable=self.sv_descr)
        self.payee_lbl = tk.Label(self.main_frm, text='Payee Name:')
        self.payee_cbx = ttk.Combobox(self.main_frm, values=self.ppl_list, textvariable=self.sv_payee)
        self.amount_lbl = tk.Label(self.main_frm, text='Total Amount:', anchor='e')
        self.amount_ent = tk.Entry(self.main_frm, textvariable=self.sv_amount)
        self.payer_lfm = tk.LabelFrame(self.main_frm, text='PAYER(S)')
        self.new_payer_btn = tk.Button(self.payer_lfm, text='Add another payer', command=self.add_new_payer)
        self.instruction_lbl = tk.Label(self.main_frm, text=instruction, justify='left')
        self.bot_frm = tk.Frame(self)
        self.calc_btn = tk.Button(self.bot_frm, text='Auto Calc', command=self.calc)
        self.okay_btn = tk.Button(self.bot_frm, text='Okay', command=self.confirm)
        self.cancel_btn = tk.Button(self.bot_frm, text='Cancel', command=self.cancel)

    def bind_ui(self):
        self.payee_cbx.bind('<FocusIn>', self.update_ppllist)
        self.new_payer_btn.bind('<ButtonPress>', self.update_ppllist)

    def grid_ui(self):
        self.main_frm.grid(column=0, row=0, sticky='nsew', padx=4, pady=4)
        self.main_frm.columnconfigure(2, weight=9)
        self.descr_lbl.grid(column=0, row=0, sticky='ew', padx=4, pady=(0, 8))
        self.descr_ent.grid(column=1, columnspan=3, row=0, sticky='ew', padx=4, pady=(0,8))

        self.payee_lbl.grid(column=0, row=1, sticky='nsew', padx=4)
        self.payee_cbx.grid(column=1, row=1, sticky='nsew', padx=4)
        self.amount_lbl.grid(column=2, row=1, sticky='nsew', padx=4)
        self.amount_ent.grid(column=3, row=1, sticky='nsew', padx=4)

        self.payer_lfm.grid(column=0, columnspan=4, row=2, sticky='nsew', padx=4, pady=(16, 4))
        self.payer_lfm.columnconfigure(0, weight=9)
        self.new_payer_btn.grid(column=0, row=0, sticky='ew', padx=4, pady=4)

        self.instruction_lbl.grid(column=0, columnspan=4, row=3, sticky='ns', padx=4, pady=2)

        self.bot_frm.grid(column=0, row=1, sticky='ew', padx=4, pady=(2,8))
        self.bot_frm.columnconfigure(1, weight=9)
        self.calc_btn.grid(column=0, row=0, sticky='ew', padx=4)
        self.okay_btn.grid(column=2, row=0, sticky='ew', padx=4)
        self.cancel_btn.grid(column=3, row=0, sticky='ew', padx=4)

    def add_new_payer(self, **kwargs):
        r = max([_._index for _ in self.pifs] + [0]) + 1
        _name = self.ppl_list[0] if r ==1 else ''
        _ = PayerInputFrame(self.payer_lfm, values=self.ppl_list, index=r, **kwargs)
        _.bind('<<delpayer>>', self.del_payer)
        _.bind('<<PayerUpdate>>', self.update_ppllist)
        self.pifs.append(_)
        self.update_ui()

    def del_payer(self, *args):
        for _ in self.pifs:
            if _.state == False:
                self.pifs.remove(_)
                break
        self.update_ui()
    
    def update_ppllist(self, *args):
        new_ppllist = self.parent.invoice.get_payers()
        new_ppllist.append(self.sv_payee.get())
        for _ in self.pifs:
            new_person = _.name.get()
            new_person = new_person.strip()
            if new_person != '' and new_person not in new_ppllist:
                new_ppllist.append(new_person)
        self.ppl_list = rmv_dups(new_ppllist)
        for _ in self.pifs:
            _.name_cbx.config(values=self.ppl_list)

    def update_ui(self):
        for _ in self.payer_lfm.winfo_children():
            if type(_) is PayerInputFrame and _.state == False:
                _.destroy()
            else:
                _.grid_forget()
        for indx, pif in enumerate(self.pifs):
            pif.grid(column=0, row=indx, sticky='ew', padx=4)
        self.new_payer_btn.grid(column=0, row=len(self.pifs), sticky='ew', padx=4, pady=4)

    def calc(self):
        pif_amounts = [stof(_.amnt.get()) for _ in self.pifs]
        if len([_ for _ in self.pifs if _.amnt.get() == '']) > 0:
            new_amnt = str(stof(self.sv_amount.get()) / len(self.pifs))
            for _ in self.pifs:
                _.amnt.set(new_amnt)
        else:
            tot_amount = stof(self.sv_amount.get())
            if sum(pif_amounts) < tot_amount:
                leftover = tot_amount - sum(pif_amounts)
                percent = 1 + (leftover / sum(pif_amounts))
                for i, p in enumerate(self.pifs):
                    p.amnt.set(str(percent * pif_amounts[i]))


    def confirm(self):
        payer_amnt = {}
        for _ in [pif.get_values() for pif in self.pifs]:
            payer_amnt[_[0]] = _[1]
        descr = self.sv_descr.get()
        payee = self.sv_payee.get()
        payer = list(payer_amnt.keys())
        amount= stof(self.sv_amount.get())
        distribution = payer_amnt
        self.ret = Transaction(descr, payee, payer, amount, distribution)
        self.destroy()

    def cancel(self):
        self.ret = None
        self.destroy()

    def show(self):
        center(self)
        self.wm_transient(self.parent)
        self.grab_set()
        self.focus_set()
        self.deiconify()
        self.wm_protocol('WM_DELETE_WINDOW', self.destroy)
        self.wait_window(self)
        return self.ret

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
        mmsg = print_array(self.invoice.list_matrix(), 'c/cr', padx=2, top='F R O M', left='TO', header='Total Amount Owed')
        mv.add_msg(mmsg)
        amsg = print_array(self.invoice.list_all(), 'c/lr', footer='\n')
        mv.add_msg(amsg)
        for i, t in enumerate(self.invoice.invoice()):
            mv.add_msg(f'{str(i).zfill(2)} : {t.descr}')
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

def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + (height // 1.5)

    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('+{}+{}'.format(int(x), int(y)))
    win.deiconify()

def init_app(app_name, version):
    root = tk.Tk()
    root.title(f"{app_name} v.{version}")
    app = MainView(root)
    app.mainloop()

def test():
    root = tk.Tk()
    mv = MessageView(root)
    mv.show()

if __name__ == '__main__':
    init_app('test', '0.0.dev')
