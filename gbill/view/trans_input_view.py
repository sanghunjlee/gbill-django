import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional, List

from ..model.invoice import Transaction
from ..tools.tools import rmv_dups,stof, center
from .payer_input_frame import PayerInputFrame

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