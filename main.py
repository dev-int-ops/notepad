import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import os
import sys
import threading
import queue
import functools
import sv_ttk
from tkinter import ttk
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from text_widget import TextWidget
from line_enumerator import LineTextWidget 

class Notepad:
    def __init__(self):
        self.root = tk.Tk()
        
        self.Width = 800
        self.Height = 600

        self.notebook = ttk.Notebook(self.root)
        self.tabs = {}

        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.customize_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.vertical_marker_menu = tk.Menu(self.customize_menu, tearoff=0)
        self.line_bar_menu = tk.Menu(self.customize_menu, tearoff=0)
        self.statusbar_menu = tk.Menu(self.customize_menu, tearoff=0)
        self.theme_edit = tk.Menu(self.customize_menu, tearoff=0)
        self.s_bars_menu = tk.Menu(self.customize_menu, tearoff=0)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.popup_menu = tk.Menu(self.root, tearoff=0)
        self.word_wrap_menu = tk.Menu(self.customize_menu, tearoff=0)
        self.syntax_menu = tk.Menu(self.customize_menu, tearoff=0)

        self.search_box_label = ttk.Frame(self.root)

        self.file_options = [('All Files', '*.*'), ('Python Files', '*.py'), ('Text Document', '*.txt')]
        
        self.tab_width = 4

        self.drag_start_index = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_target_index = None
        self.drag_threshold = 5

        # Optimization variables for debouncing & state freezing
        self.is_resizing = False
        self._resize_timer = None
        self._root_prev_width = None
        self._root_prev_height = None
        self._highlight_timer = None

        self.variable_marker = tk.IntVar()
        self.variable_theme = tk.IntVar()
        self.variable_line_bar = tk.IntVar()
        self.variable_statusbar = tk.IntVar()
        self.variable_hide_menu = tk.BooleanVar()
        self.variable_statusbar_hide = tk.BooleanVar()
        self.variable_line_bar_hide = tk.BooleanVar(value=False)
        self.variable_search_box = tk.BooleanVar()
        self.variable_syntax_highlight = tk.StringVar(value="None")
        self.variable_word_wrap = tk.BooleanVar(value=0)
        
        self.statusbar = tk.Label(self.root, text=f"", font=("Consolas", 9),
            relief=tk.FLAT, anchor='e', highlightthickness=0, bg="#007acc", fg="white")
        
        self.os_platform = sys.platform
        self.root.title("Untitled")
        
        screen_width = self.root.winfo_screenwidth() 
        screen_height = self.root.winfo_screenheight() 
        left = int((screen_width / 2) - (self.Width / 2))
        top = int((screen_height / 2) - (self.Height / 2))
        self.root.geometry(f'{self.Width}x{self.Height}+{left}+{top}')
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        self.notebook.grid(column=0, columnspan=3, row=0, sticky='nsew')
        
        self.notebook.bind('<Configure>', self.on_window_resize)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.notebook.bind("<FocusIn>", self.on_notebook_focus)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
        self.notebook.bind("<Button-1>", self.on_tab_press, add=True)
        self.notebook.bind("<B1-Motion>", self.on_tab_drag, add=True)
        self.notebook.bind("<ButtonRelease-1>", self.on_tab_release, add=True)
        
        sv_ttk.set_theme("dark")
        
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.menu_bar.add_cascade(label='Customize', menu=self.customize_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.file_menu.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)
        self.file_menu.add_command(label='Open', accelerator='Ctrl+O', command=self.open_file)
        self.file_menu.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        self.file_menu.add_command(label='Save as ...', accelerator='Ctrl+Alt+S', command=self.save_file_as)
        self.file_menu.add_command(label='Close Tab', accelerator='Ctrl+W', command=self.close_tab)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit_app)
        
        self.edit_menu.add_command(label="Copy", accelerator='Ctrl+C', command=self.copy)
        self.edit_menu.add_command(label="Paste", accelerator='Ctrl+V', command=self.paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", accelerator='Ctrl+Z', command=self.undo)
        self.edit_menu.add_command(label="Redo", accelerator='Ctrl+R', command=self.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select all", accelerator='Ctrl+A', command=self.select_all)
        self.edit_menu.add_command(label="Search", accelerator='Ctrl+F', command=self.search_box)

        self.customize_menu.add_cascade(label='Vertical marker', menu=self.vertical_marker_menu)
        self.customize_menu.add_cascade(label='Color theme', menu=self.theme_edit)
        self.customize_menu.add_cascade(label='StatusBars', menu=self.s_bars_menu)
        self.customize_menu.add_cascade(label="Line bar color", menu=self.line_bar_menu)
        self.customize_menu.add_cascade(label="Statusbar color", menu=self.statusbar_menu)
        self.customize_menu.add_cascade(label="Word wrap", menu=self.word_wrap_menu)
        self.customize_menu.add_cascade(label="Highlight syntax", menu=self.syntax_menu)

        for lang in ["None", "Python", "JSON", "CSV", "Bash", "PowerShell", "YAML"]:
            self.syntax_menu.add_radiobutton(label=lang, variable=self.variable_syntax_highlight,
                value=lang, command=self.switch_syntax_highlight)

        self.word_wrap_menu.add_checkbutton(label="Turn On", onvalue=1, offvalue=0, 
            variable=self.variable_word_wrap, command=self.word_wrap)
            
        self.s_bars_menu.add_checkbutton(label='Statusbar', onvalue=1, offvalue=0, 
            variable=self.variable_statusbar_hide, command=self.statusbar_show_remove)
        self.s_bars_menu.add_checkbutton(label='Linebar', onvalue=1, offvalue=0, 
            variable=self.variable_line_bar_hide, command=self.line_bar_show_remove)

        for i, color in enumerate(['LightSteelBlue', 'Yellow', 'Dodger blue', 'Indian red'], 1):
            self.statusbar_menu.add_checkbutton(label=color, onvalue=i, offvalue=0, 
                variable=self.variable_statusbar, command=self.statusbar_color)
            self.line_bar_menu.add_checkbutton(label=color, onvalue=i, offvalue=0, 
                variable=self.variable_line_bar, command=self.line_bar_color)

        self.vertical_marker_menu.add_checkbutton(label="80", onvalue=1, offvalue=0, 
            variable=self.variable_marker, command=self.vertical_line)
        self.vertical_marker_menu.add_checkbutton(label="120", onvalue=2, 
            variable=self.variable_marker, command=self.vertical_line)

        themes = ["Default Dark", "Default Light", "Monokai", "Solarized Dark", 
                  "Solarized Light", "Dracula", "Nord", "GitHub Dark"]
        for i, theme in enumerate(themes):
            self.theme_edit.add_checkbutton(label=theme, onvalue=i, offvalue=0,
                variable=self.variable_theme, command=self.theme_activate)
        
        self.help_menu.add_command(label="About", command=self.about)
        
        for label, cmd, acc in [("Copy", self.copy, 'Ctrl+C'), ("Paste", self.paste, 'Ctrl+V'), 
                                ("Cut", self.cut, 'Ctrl+X'), ("Undo", self.undo, 'Ctrl+Z'), 
                                ("Redo", self.redo, 'Ctrl+R')]:
            self.popup_menu.add_command(label=label, accelerator=acc, command=cmd)
        self.popup_menu.add_command(label='Hide menu', command=self.hide_menu, accelerator='Ctrl+H')

        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-Alt-s>', self.save_file_as)
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-w>', self.close_tab)
        self.root.bind('<Control-h>', self.hide_menu)
        self.root.bind('<Control-f>', self.search_box)

        self.search_entry = ttk.Entry(self.search_box_label, width=29, justify=tk.CENTER)
        self.search_entry.grid(column=1, row=0, padx=2, pady=2, columnspan=1)
        self.search_button = ttk.Button(self.search_box_label, text='Find all', command=self.find_match)
        self.search_button.grid(column=0, row=0, padx=2, pady=2, columnspan=1)
        self.find_next = ttk.Button(self.search_box_label, text='Next', command=self.next_match)
        self.find_next.grid(column=2, row=0, padx=2, pady=2, columnspan=1)
        self.replace_with_label = ttk.Label(self.search_box_label, text='Replace with:')
        self.replace_with_label.grid(column=3, row=0, padx=2, pady=2, columnspan=1)
        self.replace_match_entry = ttk.Entry(self.search_box_label, width=29, justify=tk.CENTER)
        self.replace_match_entry.grid(column=4, row=0, padx=2, pady=2, columnspan=1)
        self.repace_match_button = ttk.Button(self.search_box_label, text='Replace', command=self.replace_match)
        self.repace_match_button.grid(column=5, row=0, padx=2, pady=2, columnspan=1)

        self.dpi_awareness()
        self.create_tab()

    def on_window_resize(self, event):
        """Strictly isolate the event to the Notebook frame to prevent child event flooding"""
        if event.widget == self.notebook:
            if event.width == getattr(self, '_root_prev_width', None) and event.height == getattr(self, '_root_prev_height', None):
                return
            
            self._root_prev_width = event.width
            self._root_prev_height = event.height
            self.is_resizing = True

            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            # Wait 150ms after the user releases the mouse to run the UI update
            self._resize_timer = self.root.after(150, self.on_resize_stop)

    def on_resize_stop(self):
        """Unfreezes the UI and does one single, clean update."""
        self.is_resizing = False
        self._do_vertical_line()
        if self.current_tab and self.line_count_bar:
            self.line_count_bar.redraw()

    @property
    def current_tab_id(self):
        try:
            selected = self.notebook.select()
            return str(selected) if selected else None
        except tk.TclError:
            return None

    @property
    def current_tab(self):
        tab_id = self.current_tab_id
        return self.tabs.get(tab_id) if tab_id else None

    @property
    def text_area(self):
        tab = self.current_tab
        return tab['text_area'] if tab else None

    @property
    def filename(self):
        tab = self.current_tab
        return tab['filename'] if tab else ""

    @filename.setter
    def filename(self, value):
        tab = self.current_tab
        if tab:
            tab['filename'] = value
            self.update_tab_title(self.current_tab_id)

    @property
    def line_count_bar(self):
        tab = self.current_tab
        return tab['line_count_bar'] if tab else None

    def update_tab_title(self, tab_id):
        tab = self.tabs.get(tab_id)
        if not tab: return
        filename = tab['filename']
        is_modified = tab.get('is_modified', False)
        title = os.path.basename(filename) if filename else "Untitled"
        if is_modified: title += " *"
        self.notebook.tab(tab_id, text=title)
        if tab_id == self.current_tab_id:
            self.root.title(title)

    def on_tab_right_click(self, event):
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
            self.notebook.select(index)
            tab_menu = tk.Menu(self.root, tearoff=0)
            tab_menu.add_command(label="Close Tab", command=lambda: self.close_tab(index=index))
            tab_menu.add_command(label="Close Other Tabs", command=lambda: self.close_other_tabs(index))
            tab_menu.add_command(label="Close All Tabs", command=self.close_all_tabs)
            tab_menu.tk_popup(event.x_root, event.y_root)
            return "break"
        except tk.TclError:
            pass

    def close_other_tabs(self, keep_index):
        tabs_to_close = [i for i in range(len(self.notebook.tabs())) if i != keep_index]
        for i in reversed(tabs_to_close): self.close_tab(index=i)

    def close_all_tabs(self):
        while len(self.notebook.tabs()) > 0: self.close_tab(index=0)

    def on_text_modified(self, event):
        for tab_id, tab in self.tabs.items():
            if tab['text_area'] == event.widget:
                is_mod = tab['text_area'].edit_modified()
                if tab.get('is_modified') != is_mod:
                    tab['is_modified'] = is_mod
                    self.update_tab_title(tab_id)
                break

    def create_tab(self, filename="", text_content=""):
        tab_frame = ttk.Frame(self.notebook)
        title = os.path.basename(filename) if filename else "Untitled"
        self.notebook.add(tab_frame, text=title)
        
        text_area = TextWidget(tab_frame, undo=True, wrap='none', font=("Consolas", 11), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        
        # Setup Grid Weights for Native Layout Scaling
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(1, weight=1)
        text_area.grid(column=1, row=0, sticky='nsew')
        
        # Native ttk Scrollbars completely eliminate layout thrashing
        scrollbar_y = ttk.Scrollbar(tab_frame, orient='vertical', command=text_area.yview)
        scrollbar_x = ttk.Scrollbar(tab_frame, orient='horizontal', command=text_area.xview)
        scrollbar_y.grid(column=2, row=0, sticky='ns')
        scrollbar_x.grid(column=1, row=1, sticky='ew')
        
        line_count_bar = LineTextWidget(tab_frame)
        
        # Synchronize scrollbars with line counts efficiently
        def on_scroll(*args):
            scrollbar_y.set(*args)
            line_count_bar.redraw()

        text_area.configure(yscrollcommand=on_scroll, xscrollcommand=scrollbar_x.set)
        
        canvas_line = tk.Canvas(text_area, width=1, height=self.Height, highlightthickness=0, bg='lightsteelblue3')
        
        tab_id = str(tab_frame)
        self.tabs[tab_id] = {
            'frame': tab_frame, 'text_area': text_area, 'filename': filename,
            'line_count_bar': line_count_bar, 'canvas_line': canvas_line, 'is_modified': False
        }
        
        text_area.bind('<Tab>', self.tab)
        if self.os_platform == "win32": text_area.bind('<Shift-Tab>', self.shift_tab)
        elif self.os_platform == "linux": text_area.bind('<Shift-ISO_Left_Tab>', self.shift_tab)
        
        text_area.bind('<ButtonRelease-3>', self.popup)
        text_area.bind('<Control-r>', self.redo)
        text_area.bind('<Control-z>', self.undo)
        text_area.bind('<Control-a>', self.select_all)
        text_area.bind('<<Modified>>', self.on_text_modified)
        
        if text_content:
            text_area.insert("1.0", text_content)
        text_area.edit_modified(False)
            
        self.notebook.select(tab_frame)
        self.apply_theme_to_tab(tab_id)
        
        if self.variable_syntax_highlight.get() != "None": self.switch_syntax_highlight()
        if self.variable_line_bar_hide.get() == True:
            line_count_bar.grid(column=0, row=0, sticky='ns')
            line_count_bar.attach(text_area)
            text_area.bind("<<IcursorModify>>", self.icursor_modify)
            line_count_bar.redraw()
        if self.variable_statusbar_hide.get() == True:
            text_area.event_add("<<ButtonKeyRelease>>", "<ButtonRelease>", "<KeyRelease>")
            text_area.bind("<<ButtonKeyRelease>>", self.count_text_area)
        if self.variable_word_wrap.get() == 1: text_area.configure(wrap="word")
            
        self.on_tab_change()

    def apply_theme_to_tab(self, tab_id):
        theme_map = {
            0: ('#1e1e1e', '#d4d4d4', 'white', 'dark'), 1: ('#ffffff', '#000000', 'black', 'light'),
            2: ('#272822', '#f8f8f2', 'white', 'dark'), 3: ('#002b36', '#839496', 'white', 'dark'),
            4: ('#fdf6e3', '#657b83', 'black', 'light'), 5: ('#282a36', '#f8f8f2', 'white', 'dark'),
            6: ('#2e3440', '#d8dee9', 'white', 'dark'), 7: ('#0d1117', '#c9d1d9', 'white', 'dark')
        }
        val = self.variable_theme.get()
        if val in theme_map:
            bg, fg, insert, _ = theme_map[val]
            tab = self.tabs[tab_id]
            tab['text_area'].config(bg=bg, fg=fg, insertbackground=insert)
            if self.variable_line_bar.get() == 0:
                tab['line_count_bar'].config(bg=bg)

    def close_tab(self, event=None, index=None):
        if index is not None:
            try: tab_id = str(self.notebook.tabs()[index])
            except IndexError: return
        else:
            tab_id = self.current_tab_id

        if not tab_id: return
        tab = self.tabs.get(tab_id)
        if tab and tab.get('is_modified', False):
            self.notebook.select(tab_id)
            title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
            response = tkMessageBox.askyesnocancel("Save Changes", f"Do you want to save changes to {title}?")
            if response is True:
                if not self.save_file(): return
            elif response is None:
                return

        self.notebook.forget(tab_id)
        if tab_id in self.tabs: del self.tabs[tab_id]
        if not self.tabs: self.create_tab()

    def on_tab_change(self, event=None):
        if self.current_tab:
            self.count_text_area()
            self.root.title(os.path.basename(self.filename) if self.filename else "Untitled")
            self.update_tab_title(self.current_tab_id)

    def on_notebook_focus(self, event):
        if self.text_area: self.text_area.focus_set()

    def on_tab_press(self, event):
        try:
            self.drag_start_index = self.notebook.index(f"@{event.x},{event.y}")
            self.drag_start_x, self.drag_start_y = event.x, event.y
            self.drag_target_index = self.drag_start_index
        except tk.TclError:
            self.drag_start_index = None

    def on_tab_drag(self, event):
        if self.drag_start_index is None: return
        dx, dy = abs(event.x - self.drag_start_x), abs(event.y - self.drag_start_y)

        if dx > self.drag_threshold or dy > self.drag_threshold:
            if not hasattr(self, 'drag_overlay'):
                self.drag_overlay = tk.Toplevel(self.root)
                self.drag_overlay.overrideredirect(True)
                self.drag_overlay.attributes('-alpha', 0.8)
                tab_name = self.notebook.tab(self.notebook.tabs()[self.drag_start_index], "text")
                tk.Label(self.drag_overlay, text=tab_name, bg="#007acc", fg="white", 
                         font=("Consolas", 10), padx=8, pady=4).pack()
            
            x = self.notebook.winfo_rootx() + event.x + 15
            y = self.notebook.winfo_rooty() + event.y + 15
            self.drag_overlay.geometry(f"+{x}+{y}")
            try: self.drag_target_index = self.notebook.index(f"@{event.x},{event.y}")
            except tk.TclError: pass

    def on_tab_release(self, event):
        if hasattr(self, 'drag_overlay'):
            self.drag_overlay.destroy()
            del self.drag_overlay
        if self.drag_start_index is not None and self.drag_target_index is not None:
            if self.drag_start_index != self.drag_target_index:
                self.perform_tab_reorder(self.drag_start_index, self.drag_target_index)
        self.drag_start_index = self.drag_target_index = None

    def perform_tab_reorder(self, source_index, target_index):
        try:
            tabs = list(self.notebook.tabs())
            if not (0 <= source_index < len(tabs) and 0 <= target_index < len(tabs)): return
            source_tab_id = tabs[source_index]
            self.notebook.forget(source_index)
            if target_index > source_index: self.notebook.insert('end', source_tab_id)
            else: self.notebook.insert(target_index, source_tab_id)
            self.notebook.select(source_tab_id)
        except Exception as e:
            print(f"Error reordering tabs: {e}")

    def on_tab_press(self, event):
        """Handle mouse press on tab area - start drag tracking."""
        try:
            self.drag_start_index = self.notebook.index("@%d,%d" % (event.x, event.y))
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.drag_target_index = self.drag_start_index
        except tk.TclError:
            self.drag_start_index = None

    def on_tab_drag(self, event):
        """Handle mouse drag motion on tabs with animation."""
        if self.drag_start_index is None:
            return

        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)

        if dx > self.drag_threshold or dy > self.drag_threshold:
            try:
                current_index = self.notebook.index("@%d,%d" % (event.x, event.y))
                old_target = self.drag_target_index
                self.drag_target_index = current_index
                if self.drag_target_index != old_target:
                    self.update_tab_drag_visual(self.drag_target_index)
            except tk.TclError:
                pass

    def on_tab_release(self, event):
        """Handle mouse release - complete tab reordering."""
        if self.drag_start_index is None:
            return

        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)

        if (dx > self.drag_threshold or dy > self.drag_threshold) and self.drag_target_index != self.drag_start_index:
            self.perform_tab_reorder(self.drag_start_index, self.drag_target_index)

        self.reset_tab_visual()
        self.drag_start_index = None
        self.drag_target_index = None

    def update_tab_drag_visual(self, target_index):
        """Update visual feedback during drag by changing tab text."""
        try:
            num_tabs = len(self.notebook.tabs())
            for i in range(num_tabs):
                tab_id = self.notebook.tabs()[i]
                tab_text = self.notebook.tab(tab_id, "text")

                if i == self.drag_start_index:
                    if not tab_text.endswith(" ◄"):
                        self.notebook.tab(tab_id, text=tab_text.rstrip() + " ◄")
                elif i == target_index:
                    if not tab_text.endswith(" ►"):
                        self.notebook.tab(tab_id, text=tab_text.rstrip() + " ►")
                else:
                    if tab_text.endswith(" ◄") or tab_text.endswith(" ►"):
                        self.notebook.tab(tab_id, text=tab_text.rstrip()[:-2])
        except Exception as e:
            print(f"Error updating tab visual: {e}")

    def reset_tab_visual(self):
        """Reset all tab visual styling by removing markers."""
        try:
            for tab in self.notebook.tabs():
                tab_text = self.notebook.tab(tab, "text")
                if tab_text.endswith(" ◄") or tab_text.endswith(" ►"):
                    self.notebook.tab(tab, text=tab_text.rstrip()[:-2])
        except tk.TclError:
            pass

    def perform_tab_reorder(self, source_index, target_index):
        """Perform the actual tab reordering."""
        try:
            tabs = list(self.notebook.tabs())
            num_tabs = len(tabs)

            if source_index < 0 or source_index >= num_tabs or target_index < 0 or target_index >= num_tabs:
                return

            source_tab_id = tabs[source_index]

            self.notebook.forget(source_index)

            if target_index > source_index:
                self.notebook.insert('end', source_tab_id)
            else:
                self.notebook.insert(target_index, source_tab_id)

            self.notebook.select(source_tab_id)
        except Exception as e:
            print(f"Error reordering tabs: {e}")

    def search_box(self, event=None):
        if self.variable_search_box.get() == True:
            self.search_box_label.place_forget()
            self.variable_search_box.set(False)
            self.search_entry.unbind('<Return>')
        else:
            self.search_box_label.place(relx=1.0, rely=0.0, anchor="ne")
            self.variable_search_box.set(True)
            self.search_entry.focus_set()
            self.search_entry.bind('<Return>', self.find_match)
            tk.Misc.lift(self.search_box_label)

    def find_match(self, event=None):
        self.text_area.tag_remove('find_match', '1.0', tk.END)
        _search = self.search_entry.get()
        if _search:
            _index = '1.0'
            while True:
                _index = self.text_area.search(_search, _index, nocase=True, stopindex=tk.END)
                if not _index: break
                _last_index = f'{_index}+{len(_search)}c'
                self.text_area.tag_add('find_match', _index, _last_index)
                _index = _last_index
            self.text_area.tag_config('find_match', background='yellow', foreground='black')
        self.search_entry.focus_set()
        return "break"

    def next_match(self, event=None):
        _search = self.search_entry.get()
        self.text_area.focus_set()
        self.text_area.tag_delete('find_next')
        while (self.text_area.compare("insert", "<", "end") and "find_match" in self.text_area.tag_names("insert")):
                self.text_area.mark_set("insert", "insert+1c")
        _last_index = f'insert+{len(_search)}c'
        next_match = self.text_area.tag_nextrange("find_match", "insert")
        self.text_area.tag_config('find_next', background='aquamarine', foreground='black')

        if next_match:
            self.text_area.mark_set("insert", next_match[0])
            self.text_area.tag_add('find_next', next_match[0], _last_index)
            self.text_area.see("insert")
        elif next_match == ():
            self.text_area.mark_set("insert", "1.0")
        return "break"

    def replace_match(self):
        _search, _replace = self.search_entry.get(), self.replace_match_entry.get()
        if _search and _replace:
            _index = "1.0"
            while True:
                _index = self.text_area.search(_search, _index, nocase=False, stopindex=tk.END)
                if not _index: break
                _lastindex = f'{_index}+{len(_search)}c'
                self.text_area.delete(_index, _lastindex)
                self.text_area.insert(_index, _replace)

    def popup(self, event):
        try: self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally: self.popup_menu.grab_release()
    
    def new_file(self, event=None):
        self.create_tab()
        
    def open_file(self, event=None):
        try:
            filename = tkFileDialog.askopenfilename(defaultextension=".txt", filetypes=self.file_options)
            if not filename: return
            filename = os.path.normpath(filename)
            
            for tab_id, tab_info in self.tabs.items():
                tab_fn = tab_info.get('filename')
                if tab_fn and os.path.normpath(tab_fn) == filename:
                    self.notebook.select(tab_id)
                    return
            
            self.create_tab(filename=filename, text_content="")
            tab = self.tabs[self.current_tab_id]
            ta = tab['text_area']
            
            ta.config(state=tk.NORMAL, wrap="none")
            file_queue = queue.Queue()
            
            def producer():
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        chunk_size = 1024 * 1024 # 1MB Chunking Buffer
                        for chunk in iter(functools.partial(f.read, chunk_size), ''):
                            file_queue.put(chunk)
                    file_queue.put(None)
                except Exception as e:
                    print(f"I/O Exception: {e}")

            def consumer():
                try:
                    while True:
                        chunk = file_queue.get_nowait()
                        if chunk is None:
                            ta.edit_modified(False)
                            tab['is_modified'] = False
                            self.update_tab_title(self.current_tab_id)
                            if self.variable_word_wrap.get() == 1: ta.config(wrap="word")
                            return
                        ta.insert(tk.END, chunk)
                except queue.Empty:
                    pass
                self.root.after(50, consumer)

            threading.Thread(target=producer, daemon=True).start()
            self.root.after(50, consumer)

        except FileNotFoundError:
            return None

    def save_file_as(self, event=None):
        if not self.current_tab: return False
        tab = self.current_tab
        try:
            title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
            filename = tkFileDialog.asksaveasfilename(initialfile=title, defaultextension='.txt', filetypes=self.file_options)
            if not filename: return False
                
            self.filename = filename
            with open(self.filename, 'w', encoding='utf-8') as data:
                data.write(self.text_area.get(1.0, tk.END))
            self.root.title(os.path.basename(self.filename))
            self.text_area.edit_modified(False)
            tab['is_modified'] = False
            self.update_tab_title(self.current_tab_id)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
                
    def save_file(self, event=None):
        if not self.current_tab: return False
        tab = self.current_tab
        if tab['filename']:
            with open(tab['filename'], 'w', encoding='utf-8') as note:
                note.write(self.text_area.get(1.0, tk.END))
            self.root.title(os.path.basename(tab['filename']))
            self.text_area.edit_modified(False)
            tab['is_modified'] = False
            self.update_tab_title(self.current_tab_id)
            return True
        else: return self.save_file_as()

    def quit_app(self):
        for tab_id in list(self.tabs.keys()):
            tab = self.tabs.get(tab_id)
            if tab and tab.get('is_modified', False):
                self.notebook.select(tab_id)
                title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
                response = tkMessageBox.askyesnocancel("Save Changes", f"Do you want to save changes to {title}?")
                if response is True:
                    if not self.save_file(): return
                elif response is None: return
        self.root.destroy()
    
    def copy(self):
        if self.text_area: self.text_area.event_generate("<<Copy>>")
    def cut(self, event=None):
        if self.text_area: self.text_area.event_generate("<<Cut>>")
    def paste(self, event=None):
        if self.text_area: self.text_area.event_generate("<<Paste>>")
        return 'break'
    def undo(self, event=None):
        if self.text_area: self.text_area.event_generate("<<Undo>>")
    def redo(self, event=None):
        if self.text_area: self.text_area.event_generate("<<Redo>>")
    def select_all(self, event=None):
        if self.text_area: self.text_area.event_generate("<<SelectAll>>")
    def about(self):
        tkMessageBox.showinfo("Notepad", "High Performance Architecture")
    def run(self):
        self.root.mainloop()
        
    def tab(self, arg):
        if not self.text_area: return 'break'
        self.text_area.insert(tk.INSERT, " " * self.tab_width)
        return 'break'
    def shift_tab(self, event=None):
        if not self.text_area: return 'break'
        previous_characters = self.text_area.get(f"insert -{self.tab_width}c", tk.INSERT)
        if previous_characters == " " * self.tab_width:
            self.text_area.delete(f"insert-{self.tab_width}c", tk.INSERT)
        return "break"
       
    def theme_activate(self):
        theme_map = {
            0: ('#1e1e1e', '#d4d4d4', 'white', 'dark'), 1: ('#ffffff', '#000000', 'black', 'light'),
            2: ('#272822', '#f8f8f2', 'white', 'dark'), 3: ('#002b36', '#839496', 'white', 'dark'),
            4: ('#fdf6e3', '#657b83', 'black', 'light'), 5: ('#282a36', '#f8f8f2', 'white', 'dark'),
            6: ('#2e3440', '#d8dee9', 'white', 'dark'), 7: ('#0d1117', '#c9d1d9', 'white', 'dark')
        }
        val = self.variable_theme.get()
        if val in theme_map:
            bg, fg, insert, sv_theme = theme_map[val]
            sv_ttk.set_theme(sv_theme)
            for tab in self.tabs.values():
                tab['text_area'].config(bg=bg, fg=fg, insertbackground=insert)
                if self.variable_line_bar.get() == 0: tab['line_count_bar'].config(bg=bg)
            if self.variable_statusbar.get() == 0:
                self.statusbar.config(bg="#007acc" if sv_theme == "dark" else "#005999", fg="white")
            self.switch_syntax_highlight()

    def vertical_line(self, event=None):
        if getattr(self, 'is_resizing', False):
            return
        self._do_vertical_line()

    def _do_vertical_line(self):
        for tab in self.tabs.values():
            canvas_line = tab['canvas_line']
            if self.variable_marker.get() == 0: canvas_line.place_forget()
            elif self.variable_marker.get() == 1: canvas_line.place(x=640, height=self.root.winfo_height())
            elif self.variable_marker.get() == 2: canvas_line.place(x=960, height=self.root.winfo_height())

    def count_text_area(self, event=None):
        if not self.text_area: return
        line, col = self.text_area.index("insert").split(".")
        symb_count = self.text_area.count(1.0, "end-1c", "chars")
        symb = str(symb_count[0]) if symb_count else "0"
        self.statusbar.config(text=f"Line: {line} | Col: {col} | Symbols: {symb}")

    def icursor_modify(self, event):
        if getattr(self, 'is_resizing', False): return
        if self.line_count_bar: self.line_count_bar.redraw()
    
    def line_bar_color(self, event=None):
        for tab in self.tabs.values():
            line_count_bar = tab['line_count_bar']
            text_area = tab['text_area']
            val = self.variable_line_bar.get()
            colors = {0: text_area.cget('bg'), 1: 'lightsteelblue3', 2: 'yellow', 3: 'dodger blue', 4: 'Indian red'}
            if val in colors: line_count_bar.config(bg=colors[val])
    
    def statusbar_color(self, event=None):
        val = self.variable_statusbar.get()
        if val == 0:
            is_dark = sv_ttk.get_theme() == "dark"
            self.statusbar.config(bg="#007acc" if is_dark else "#005999", fg="white")
        else:
            colors = {1: ('lightsteelblue3', 'black'), 2: ('yellow', 'black'), 3: ('dodger blue', 'white'), 4: ('Indian red', 'white')}
            if val in colors: self.statusbar.config(bg=colors[val][0], fg=colors[val][1])

    def hide_menu(self, event=None):
        if self.variable_hide_menu.get() == False:
            self.root.config(menu=tk.Menu(self.root))
            self.variable_hide_menu.set(True)
        else:
            self.root.config(menu=self.menu_bar)
            self.variable_hide_menu.set(False)
    
    def statusbar_show_remove(self):
        if self.variable_statusbar_hide.get() == False:
            for tab in self.tabs.values():
                try: tab['text_area'].event_delete("<<ButtonKeyRelease>>")
                except tk.TclError: pass
            self.statusbar.grid_forget()
        else:
            self.statusbar.grid(column=0, columnspan=3, row=1, sticky='wes')
            for tab in self.tabs.values():
                tab['text_area'].event_add("<<ButtonKeyRelease>>", "<ButtonRelease>", "<KeyRelease>")
                tab['text_area'].bind("<<ButtonKeyRelease>>", self.count_text_area)
    
    def line_bar_show_remove(self):
        if self.variable_line_bar_hide.get() == False:
            for tab in self.tabs.values():
                try:
                    tab['line_count_bar'].config(state='normal')
                    tab['line_count_bar'].delete("1.0", tk.END)
                    tab['line_count_bar'].config(state='disabled')
                    tab['line_count_bar'].grid_forget()
                    tab['line_count_bar'].textwidget = None
                    tab['text_area'].unbind("<<IcursorModify>>")
                except TypeError: pass
        else:
            for tab in self.tabs.values():
                tab['line_count_bar'].grid(column=0, row=0, sticky='ns')
                tab['line_count_bar'].attach(tab['text_area'])
                tab['line_count_bar'].redraw()
                tab['text_area'].bind("<<IcursorModify>>", self.icursor_modify)

    def dpi_awareness(self):
        if self.os_platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (ImportError, OSError): pass
    
    def syntax_highlight(self, event):
        if getattr(self, 'is_resizing', False): return
        if self._highlight_timer: self.root.after_cancel(self._highlight_timer)
        self._highlight_timer = self.root.after(50, self._apply_syntax_highlight)

    def _apply_syntax_highlight(self):
        if not self.text_area: return
        row = self.text_area.index("insert").split(".")[0]
        for tag in self.text_area.tag_names():
            if tag.startswith("Token."): self.text_area.tag_remove(tag, f"{row}.0", f"{row}.end")
        data = self.text_area.get(f"{row}.0", f"{row}.end")
        self.syntax_colorizer(data, f"{row}.0")

    def switch_syntax_highlight(self):
        if self.variable_syntax_highlight.get() != "None":
            self.text_area.bind("<KeyRelease>", self.syntax_highlight)
            is_dark = sv_ttk.get_theme() == "dark"
            
            tags_dark = {
                "Token.Literal.String": "#ce9178", "Token.Literal.Number": "#b5cea8",
                "Token.Name.Builtin": "#4ec9b0", "Token.Name.Tag": "#569cd6", "Token.Name.Variable": "#9cdcfe",
                "Token.Operator": "#d4d4d4", "Token.Keyword": "#569cd6", "Token.Comment": "#6a9955"
            }
            tags_light = {
                "Token.Literal.String": "#a31515", "Token.Literal.Number": "#098658",
                "Token.Name.Builtin": "#267f99", "Token.Name.Tag": "#0000ff", "Token.Name.Variable": "#001080",
                "Token.Operator": "#000000", "Token.Keyword": "#0000ff", "Token.Comment": "#008000"
            }
            target_tags = tags_dark if is_dark else tags_light
            
            for base, color in target_tags.items():
                self.text_area.tag_configure(base, foreground=color)
                self.text_area.tag_configure(f"{base}.Single", foreground=color)
                self.text_area.tag_configure(f"{base}.Double", foreground=color)
                self.text_area.tag_configure(f"{base}.Integer", foreground=color)
                self.text_area.tag_configure(f"{base}.Float", foreground=color)
                self.text_area.tag_configure(f"{base}.Namespace", foreground=color)
                self.text_area.tag_configure(f"{base}.Hashbang", foreground=color)
                self.text_area.tag_configure(f"{base}.Attribute", foreground=color)

            for tag in self.text_area.tag_names():
                if tag.startswith("Token."): self.text_area.tag_remove(tag, "1.0", tk.END)

            data = self.text_area.get("1.0", "end-1c")
            self.syntax_colorizer(data, "1.0")
        else:
            self.text_area.unbind("<KeyRelease>")
            for tag in self.text_area.tag_names():
                if tag.startswith("Token."): self.text_area.tag_delete(tag)

    def syntax_colorizer(self, data, start_index, ta=None):
        ta = ta or self.text_area
        if not ta: return
        lang = self.variable_syntax_highlight.get()
        try: lexer = get_lexer_by_name(lang.lower())
        except ClassNotFound: return

        row, col = map(int, start_index.split('.'))
        for token, content in lex(data, lexer):
            lines = content.split('\n')
            if len(lines) == 1:
                end_row, end_col = row, col + len(lines[0])
            else:
                end_row, end_col = row + len(lines) - 1, len(lines[-1])
            ta.tag_add(str(token), f"{row}.{col}", f"{end_row}.{end_col}")
            row, col = end_row, end_col

    def word_wrap(self):
        wrap_mode = "none" if self.variable_word_wrap.get() == 0 else "word"
        for tab in self.tabs.values(): tab['text_area'].configure(wrap=wrap_mode)

if __name__ == '__main__':
    notepad = Notepad()
    notepad.run()