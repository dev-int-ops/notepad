import tkinter as tk
from tkinter import ttk


class AutoScrollbar(ttk.Scrollbar):
    """Create a scrollbar that hides iteself if it's not needed. Only
    works if you use the pack geometry manager from tkinter.

    https://stackoverflow.com/questions/57030781/auto-hiding-scrollbar-not-showing-as-expected-with-tkinter-pack-method
    """
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            if str(self.cget("orient")) == tk.HORIZONTAL:
                self.pack(fill=tk.X, side=tk.BOTTOM)
            else:
                self.pack(fill=tk.Y, side=tk.RIGHT)
        ttk.Scrollbar.set(self, low, high)
    def grid(self, **kw):
        raise tk.TclError("cannot use grid with this widget")
    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")
