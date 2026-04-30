import tkinter as tk

class LineTextWidget(tk.Text):
    """
    A lag-free line number widget using a native Tkinter Text widget.
    This eliminates the CPU overhead of drawing Canvas shapes.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('width', 4)
        kwargs.setdefault('bg', '#1e1e1e')
        kwargs.setdefault('fg', '#858585')
        kwargs.setdefault('font', ("Consolas", 11))
        kwargs.setdefault('state', 'disabled')
        kwargs.setdefault('highlightthickness', 0)
        kwargs.setdefault('borderwidth', 0)
        tk.Text.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget
        
    def redraw(self, *args):
        if not self.textwidget:
            return

        self.config(state='normal')
        self.delete("1.0", "end")
        
        # Get the first and last visible lines
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            
            line_num = str(i).split(".")[0]
            self.insert("end", f"{line_num}\n")
            i = self.textwidget.index(f"{i}+1line")

        self.config(state='disabled')