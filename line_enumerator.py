import tkinter as tk


class LineEnumerator(tk.Canvas):
    """
    Canvas class for displaying line numbers.
    https://stackoverflow.com/a/16375233
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('bg', '#1e1e1e')
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        """Associating a text widget with main widget."""
        self.textwidget = text_widget

    def redraw(self, *args):
        """Redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            try:
                dline= self.textwidget.dlineinfo(i)
                if dline is None: break
                y = dline[1]
                line_num = str(i).split(".")[0]
                self.create_text(31,y,anchor="ne", text=line_num, 
                                 font=("Consolas", 11), fill="#858585")
                i = self.textwidget.index("%s+1line" % i)
            except Exception as e:
                raise e