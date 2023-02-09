import tkinter as tk
from tkinter import font as tkFont

from .window import Window

class MessageView(Window):
    def __init__(self, parent, message: str = '', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #self.resizable(False, False)
        self.parent = parent
        self.normal_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.normal_font.config(size=9, weight=tkFont.NORMAL, slant=tkFont.ROMAN)
        self.bold_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.bold_font.config(size=9, weight=tkFont.BOLD, slant=tkFont.ROMAN)
        self.italic_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.italic_font.config(size=9, weight=tkFont.NORMAL, slant=tkFont.ITALIC)
        self.bold_italic_font = tkFont.Font(**tkFont.nametofont('TkFixedFont').actual())
        self.bold_italic_font.config(size=9, weight=tkFont.BOLD, slant=tkFont.ITALIC)

        frame = tk.Frame(self)
        button_frame = tk.Frame(self)

        self.display = tk.Text(frame, bg='SystemButtonFace', cursor='arrow', font=self.normal_font)
        self.display.tag_configure('bold', font=self.bold_font)
        self.display.tag_configure('italic', font=self.italic_font)
        self.display.tag_configure('bold_italic', font=self.bold_italic_font)

        self.vbar = tk.Scrollbar(frame)
        close_btn = tk.Button(button_frame, text='Close', command=lambda: self.destroy())

        self.display.config(yscrollcommand=self.vbar.set)
        self.vbar.config(command=self.display.yview)
        self.display.config(state='disabled')

        frame.pack(side='top', fill='both', expand=True, padx=4, pady=4)
        button_frame.pack(side='bottom', fill='both', expand=False, padx=4, pady=4)
        self.display.pack(side='left', fill='both', expand=True)
        self.vbar.pack(side='right',fill='y', expand=True)
        close_btn.pack(side='right', fill='x', expand=True)
        
        if message != '':
            self.add(message)

    def add(self, message: str):
        self.display.config(state='normal')
        self.display.insert('end', message, '')
        self.display.config(state='disabled')

    def _add(self, message: str):
        self.display.config(state='normal')
        _msg = message.replace('_', '*')
        afont = ['', 'italic', 'bold', 'bold_italic']
        token = ''
        bucket = ''
        for i in range(len(_msg)):
            char = _msg[i]
            if char == '*':
                if bucket != '':
                    # release styled bucket
                    self.display.insert('end', bucket, afont[len(token)])
                    i += len(token)
                    token = ''
                else:
                    token += '*'
            else:
                bucket += char
        if bucket != '':
            self.display.insert('end', bucket, afont[0])
        self.display.config(state='disabled')
