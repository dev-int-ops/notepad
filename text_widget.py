import tkinter as tk

class TextWidget(tk.Text):
    """
    Optimized proxy pattern utilizing fast Python sets for event tracking.
    """
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        # action for the underlying widget
        self._first = self._w + "_first"
        self.tk.call("rename", self._w, self._first)
        self.tk.createcommand(self._w, self._icursor_agent)
        
        # Lookups are hashed sets to prevent sequential if/elif bottlenecks
        self._mod_cmds = {"insert", "replace", "delete"}
        self._scroll_cmds = {("xview", "moveto"), ("xview", "scroll"), 
                             ("yview", "moveto"), ("yview", "scroll")}

    def _icursor_agent(self, *args):
        command = (self._first,) + args
        try:
            result = self.tk.call(command)
        except Exception:
            return None

        if not args:
            return result

        cmd = args[0]
        # Evaluated natively with minimal overhead
        if (cmd in self._mod_cmds or 
            (cmd == "mark" and len(args) >= 3 and args[1:3] == ("set", "insert")) or
            (cmd in ("xview", "yview") and len(args) >= 2 and args[0:2] in self._scroll_cmds)):
            self.event_generate("<<IcursorModify>>", when="tail")

        return result