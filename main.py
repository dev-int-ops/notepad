import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

from text_widget import TextWidget
from line_enumerator import LineEnumerator
from scrollbar import AutoScrollbar

import os
import sys
import sv_ttk
from tkinter import ttk

from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


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

        self.file_options = [('All Files', '*.*'), ('Python Files', '*.py'),
                    ('Text Document', '*.txt')]
        
        self.tab_width = 4

        self.drag_start_index = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_target_index = None
        self.drag_threshold = 5

        self.variable_marker = tk.IntVar()
        self.variable_theme = tk.IntVar()
        self.variable_line_bar = tk.IntVar()
        self.variable_statusbar = tk.IntVar()
        self.variable_hide_menu = tk.BooleanVar()
        self.variable_statusbar_hide = tk.BooleanVar()
        self.variable_line_bar_hide = tk.BooleanVar()
        self.variable_search_box = tk.BooleanVar()
        self.variable_syntax_highlight = tk.StringVar(value="None")
        self.variable_word_wrap = tk.BooleanVar()
        
        self.statusbar = tk.Label(self.root, text=f"", font=("Consolas", 9),
            relief=tk.FLAT, anchor='e', highlightthickness=0, bg="#007acc", fg="white")
        
        self.os_platform = sys.platform
        
        self.root.title("Untitled")
        # Center the window
        screen_width = self.root.winfo_screenwidth() 
        screen_height = self.root.winfo_screenheight() 

        # For left-alling
        left = (screen_width / 2) - (self.Width / 2)  
        # For right-allign
        top = (screen_height / 2) - (self.Height /2)  
        # For top and bottom
        self.root.geometry('%dx%d+%d+%d' % (self.Width, self.Height,
            left, top))
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Make the notebook auto resizable
        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        self.notebook.grid(column=0, columnspan=3, row=0, sticky='nsew')
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.notebook.bind("<FocusIn>", self.on_notebook_focus)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)
        self.notebook.bind("<Button-1>", self.on_tab_press, add=True)
        self.notebook.bind("<B1-Motion>", self.on_tab_drag, add=True)
        self.notebook.bind("<ButtonRelease-1>", self.on_tab_release, add=True)
        
        # Apply modern theme
        sv_ttk.set_theme("dark")
        
        ## Menu GUI
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.menu_bar.add_cascade(label='Customize', menu=self.customize_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # File menu
        self.file_menu.add_command(label='New', accelerator='Ctrl+N', 
            command=self.new_file)
        self.file_menu.add_command(label='Open', accelerator='Ctrl+O',
            command=self.open_file)
        self.file_menu.add_command(label='Save', accelerator='Ctrl+S',
            command=self.save_file)
        self.file_menu.add_command(label='Save as ...',
            accelerator='Ctrl+Alt+S', command=self.save_file_as)
        self.file_menu.add_command(label='Close Tab',
            accelerator='Ctrl+W', command=self.close_tab)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit_app)
        
        # Edit menu
        self.edit_menu.add_command(label="Copy", accelerator='Ctrl+C',
            command=self.copy)
        self.edit_menu.add_command(label="Paste", accelerator='Ctrl+V',
            command=self.paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", accelerator='Ctrl+Z',
            command=self.undo)
        self.edit_menu.add_command(label="Redo", accelerator='Ctrl+R',
            command=self.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select all", accelerator='Ctrl+A',
            command=self.select_all)
        self.edit_menu.add_command(label="Search", accelerator='Ctrl+F',
            command=self.search_box)

        # Customize menu
        self.customize_menu.add_cascade(label='Vertical marker',
            menu=self.vertical_marker_menu)
        self.customize_menu.add_cascade(label='Color theme',
            menu=self.theme_edit)
        self.customize_menu.add_cascade(label='StatusBars',
            menu=self.s_bars_menu)
        self.customize_menu.add_cascade(label="Line bar color",
            menu=self.line_bar_menu)
        self.customize_menu.add_cascade(label="Statusbar color",
            menu=self.statusbar_menu)
        self.customize_menu.add_cascade(label="Word wrap",
            menu=self.word_wrap_menu)
        self.customize_menu.add_cascade(label="Highlight syntax",
            menu=self.syntax_menu)

        # Syntax highlight menu
        for lang in ["None", "Python", "JSON", "CSV", "Bash", "PowerShell", "YAML"]:
            self.syntax_menu.add_radiobutton(label=lang, variable=self.variable_syntax_highlight,
                value=lang, command=self.switch_syntax_highlight)

        # Word wrap menu
        self.word_wrap_menu.add_checkbutton(label="Turn On",
            onvalue=1, offvalue=0, variable=self.variable_word_wrap,
            command=self.word_wrap)
        # StatusBars show-hide option
        self.s_bars_menu.add_checkbutton(label='Statusbar', onvalue=1,
            offvalue=0, variable=self.variable_statusbar_hide,
            command=self.statusbar_show_remove)
        self.s_bars_menu.add_checkbutton(label='Linebar', onvalue=1,
            offvalue=0, variable=self.variable_line_bar_hide,
            command=self.line_bar_show_remove)

        # Status bar color
        self.statusbar_menu.add_checkbutton(label='LightSteelBlue', onvalue=1,
            offvalue=0, variable=self.variable_statusbar,
            command=self.statusbar_color)
        self.statusbar_menu.add_checkbutton(label='Yellow', onvalue=2,
            offvalue=0, variable=self.variable_statusbar,
            command=self.statusbar_color)
        self.statusbar_menu.add_checkbutton(label='Dodger blue', onvalue=3,
            offvalue=0, variable=self.variable_statusbar,
            command=self.statusbar_color)
        self.statusbar_menu.add_checkbutton(label='Indian red', onvalue=4,
            offvalue=0, variable=self.variable_statusbar,
            command=self.statusbar_color)

        # Left bar color
        self.line_bar_menu.add_checkbutton(label='LightSteelBlue', onvalue=1,
            offvalue=0, variable=self.variable_line_bar,
            command=self.line_bar_color)
        self.line_bar_menu.add_checkbutton(label='Yellow', onvalue=2,
            offvalue=0, variable=self.variable_line_bar,
            command=self.line_bar_color)
        self.line_bar_menu.add_checkbutton(label='Dodger blue', onvalue=3,
            offvalue=0, variable=self.variable_line_bar,
            command=self.line_bar_color)
        self.line_bar_menu.add_checkbutton(label='Indian red', onvalue=4,
            offvalue=0, variable=self.variable_line_bar,
            command=self.line_bar_color)

        # Vertical marker
        self.vertical_marker_menu.add_checkbutton(label="80", onvalue=1,
            offvalue=0, variable=self.variable_marker,
            command=self.vertical_line)
        self.vertical_marker_menu.add_checkbutton(label="120", onvalue=2,
            variable=self.variable_marker, command=self.vertical_line)

        # Nested Theme menu
        self.theme_edit.add_checkbutton(label="Default Dark", onvalue=0, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Default Light", onvalue=1, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Monokai", onvalue=2, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Solarized Dark", onvalue=3, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Solarized Light", onvalue=4, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Dracula", onvalue=5, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Nord", onvalue=6, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="GitHub Dark", onvalue=7, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        
        # Help menu
        self.help_menu.add_command(label="About", command=self.about)
        
        # Mouse right click popup menu
        self.popup_menu.add_command(label="Copy", accelerator='Ctrl+C',
            command=self.copy)
        self.popup_menu.add_command(label="Paste", accelerator='Ctrl+V',
            command=self.paste)
        self.popup_menu.add_command(label="Cut", accelerator='Ctrl+X',
            command=self.cut)
        self.popup_menu.add_command(label="Undo", accelerator='Ctrl+Z',
            command=self.undo)
        self.popup_menu.add_command(label="Redo", accelerator='Ctrl+R',
            command=self.redo)
        self.popup_menu.add_command(label='Hide menu',
            command=self.hide_menu, accelerator='Ctrl+H')

        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-Alt-s>', self.save_file_as)
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-w>', self.close_tab)
        self.root.bind('<Control-h>', self.hide_menu)
        self.root.bind('<Control-f>', self.search_box)

        # Search box
        self.search_entry = ttk.Entry(self.search_box_label, width=29, justify=tk.CENTER)
        self.search_entry.grid(column=1, row=0, padx=2, pady=2, columnspan=1)
        self.search_button = ttk.Button(self.search_box_label, text='Find all',
            command=self.find_match, cursor='arrow')
        self.search_button.grid(column=0, row=0, padx=2, pady=2, columnspan=1)
        self.find_next = ttk.Button(self.search_box_label, text='Next', 
            command=self.next_match, cursor='arrow')
        self.find_next.grid(column=2, row=0, padx=2, pady=2, columnspan=1)

        self.replace_with_label = ttk.Label(self.search_box_label, text='Replace with:')
        self.replace_with_label.grid(column=3, row=0, padx=2, pady=2, columnspan=1)
        self.replace_match_entry = ttk.Entry(self.search_box_label, width=29, justify=tk.CENTER)
        self.replace_match_entry.grid(column=4, row=0, padx=2, pady=2, columnspan=1)
        self.repace_match_button = ttk.Button(self.search_box_label, text='Replace',
            command=self.replace_match, cursor='arrow')
        self.repace_match_button.grid(column=5, row=0, padx=2, pady=2, columnspan=1)

        self.dpi_awareness()
        self._highlight_timer = None
        self._incremental_timer = None

        self.create_tab()

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

    @property
    def canvas_line(self):
        tab = self.current_tab
        return tab['canvas_line'] if tab else None

    def update_tab_title(self, tab_id):
        tab = self.tabs.get(tab_id)
        if not tab: return

        filename = tab['filename']
        is_modified = tab.get('is_modified', False)

        title = os.path.basename(filename) if filename else "Untitled"
        if is_modified:
            title += " *"

        self.notebook.tab(tab_id, text=title)

        if tab_id == self.current_tab_id:
            self.root.title(title)

    def on_tab_right_click(self, event):
        try:
            index = self.notebook.index("@%d,%d" % (event.x, event.y))
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
        for i in reversed(tabs_to_close):
            self.close_tab(index=i)

    def close_all_tabs(self):
        while len(self.notebook.tabs()) > 0:
            self.close_tab(index=0)

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
        text_area.grid(column=1, row=0, sticky='nsew')
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(1, weight=1)
        
        scrollbar_y = AutoScrollbar(text_area, orient='vertical')
        scrollbar_x = AutoScrollbar(text_area, orient='horizontal')
        text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.config(command=text_area.yview, cursor="sb_v_double_arrow")
        scrollbar_x.config(command=text_area.xview, cursor="sb_h_double_arrow")
        
        line_count_bar = LineEnumerator(tab_frame, width=32, highlightthickness=0)
        canvas_line = tk.Canvas(text_area, width=1, height=self.Height, highlightthickness=0, bg='lightsteelblue3')
        
        tab_id = str(tab_frame)
        self.tabs[tab_id] = {
            'frame': tab_frame,
            'text_area': text_area,
            'filename': filename,
            'line_count_bar': line_count_bar,
            'canvas_line': canvas_line,
            'is_modified': False
        }
        
        text_area.bind('<Tab>', self.tab)
        if self.os_platform == "win32":
            text_area.bind('<Shift-Tab>', self.shift_tab)
        elif self.os_platform == "linux":
            text_area.bind('<Shift-ISO_Left_Tab>', self.shift_tab)
        text_area.bind('<ButtonRelease-3>', self.popup)
        text_area.bind('<Control-r>', self.redo)
        text_area.bind('<Control-z>', self.undo)
        text_area.bind('<Control-a>', self.select_all)
        text_area.bind('<Configure>', self.vertical_line)
        text_area.bind('<<Modified>>', self.on_text_modified)
        
        if text_content:
            text_area.insert("1.0", text_content)
            
        text_area.edit_modified(False)
            
        self.notebook.select(tab_frame)
        self.apply_theme_to_tab(tab_id)
        
        if self.variable_syntax_highlight.get() != "None":
            self.switch_syntax_highlight()
            
        if self.variable_line_bar_hide.get() == True:
            line_count_bar.grid(column=0, row=0, sticky='ns')
            line_count_bar.attach(text_area)
            text_area.bind("<<IcursorModify>>", self.icursor_modify)
            
        if self.variable_statusbar_hide.get() == True:
            text_area.event_add("<<ButtonKeyRelease>>", "<ButtonRelease>", "<KeyRelease>")
            text_area.bind("<<ButtonKeyRelease>>", self.count_text_area)
            
        if self.variable_word_wrap.get() == 1:
            text_area.configure(wrap="word")
            
        self.on_tab_change()

    def apply_theme_to_tab(self, tab_id):
        theme_map = {
            0: ('#1e1e1e', '#d4d4d4', 'white', 'dark'),
            1: ('#ffffff', '#000000', 'black', 'light'),
            2: ('#272822', '#f8f8f2', 'white', 'dark'),
            3: ('#002b36', '#839496', 'white', 'dark'),
            4: ('#fdf6e3', '#657b83', 'black', 'light'),
            5: ('#282a36', '#f8f8f2', 'white', 'dark'),
            6: ('#2e3440', '#d8dee9', 'white', 'dark'),
            7: ('#0d1117', '#c9d1d9', 'white', 'dark')
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
            try:
                tab_id = str(self.notebook.tabs()[index])
            except IndexError:
                return
        else:
            tab_id = self.current_tab_id

        if not tab_id:
            return

        tab = self.tabs.get(tab_id)
        if tab and tab.get('is_modified', False):
            self.notebook.select(tab_id)
            title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
            response = tkMessageBox.askyesnocancel("Save Changes", f"Do you want to save changes to {title}?")
            if response is True:
                saved = self.save_file()
                if not saved:
                    return
            elif response is None:
                return

        self.notebook.forget(tab_id)
        if tab_id in self.tabs:
            del self.tabs[tab_id]
        if not self.tabs:
            self.create_tab()

    def on_tab_change(self, event=None):
        if self.current_tab:
            self.count_text_area()
            self.root.title(os.path.basename(self.filename) if self.filename else "Untitled")
            self.update_tab_title(self.current_tab_id)

    def on_notebook_focus(self, event):
        """Set focus to the text area when the notebook is focused."""
        if self.text_area:
            self.text_area.focus_set()

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
        """Make Search box appear inside text area"""
        if self.variable_search_box.get() == True:
            self.search_box_label.place_forget()
            self.variable_search_box.set(False)
            self.search_entry.unbind('<Return>')
        elif self.variable_search_box.get() == False:
            self.search_box_label.place(relx=1.0, rely=0.0, anchor="ne")
            self.variable_search_box.set(True)
            self.search_entry.focus_set()
            self.search_entry.bind('<Return>', self.find_match)
            tk.Misc.lift(self.search_box_label) # display over other items
        else:
            return None

    def find_match(self, event=None):
        """Search for match of words or symbols inside text area"""
        self.text_area.tag_remove('find_match', '1.0', tk.END)
        _search = self.search_entry.get()

        if _search:
            _index = '1.0'
            while True:
                _index = self.text_area.search(_search, _index,
                    nocase=True, stopindex=tk.END)
                if not _index:
                    break
                _last_index = '%s+%dc' % (_index, len(_search))
                self.text_area.tag_add('find_match', _index, _last_index)
                _index = _last_index
            self.text_area.tag_config('find_match', background='yellow',
                foreground='black')
        self.search_entry.focus_set()
        return "break"

    def next_match(self, event=None):
        """
        Move cursor to next match, highlight and focus it.
        After last match is marked - start over.

        https://stackoverflow.com/a/44164144
        """
        _search = self.search_entry.get()
        self.text_area.focus_set()
        self.text_area.tag_delete('find_next')
        # move cursor to beginning of current match
        while (self.text_area.compare("insert", "<", "end") and
            "find_match" in self.text_area.tag_names("insert")):
                self.text_area.mark_set("insert", "insert+1c")
        _last_index = '%s+%dc' % ("insert", len(_search))
        # find next character with the tag
        next_match = self.text_area.tag_nextrange("find_match", "insert")
        self.text_area.tag_config('find_next', background='aquamarine',
                foreground='black')

        if next_match:
            self.text_area.mark_set("insert", next_match[0])
            self.text_area.tag_add('find_next', next_match[0], _last_index)
            self.text_area.see("insert")
        elif next_match == ():
            # mark all concurrences again from beggining
            self.text_area.mark_set("insert", "1.0")
        else:
            return None
        # prevent default behavior, in case this was called
        # via a key binding
        return "break"

    def replace_match(self):
        """Find and replace occurrences. Case sensitive."""
        _search = self.search_entry.get()
        _replace = self.replace_match_entry.get()

        if _search and _replace:
            _index = "1.0"
            while True:
                _index = self.text_area.search(_search, _index, nocase=False,
                    stopindex=tk.END)

                if not _index:
                    break

                _lastindex = '%s+% dc' % (_index, len(_search))

                self.text_area.delete(_index, _lastindex)
                self.text_area.insert(_index, _replace)

    def seach_box_background(self):
        """Change search box background"""
        pass # Managed by sv_ttk theme now

    def popup(self, event):
        """
        Show context menu when Mouse <Button-3> is clicked.
        https://stackoverflow.com/a/12014379
        """
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()
    
    def new_file(self, event=None):
        """Clear text area."""
        self.create_tab()
        
    def open_file(self, event=None):
        try:
            filename = tkFileDialog.askopenfilename(
                defaultextension=".txt", filetypes=self.file_options)
            if filename:
                filename = os.path.normpath(filename)
                for tab_id, tab_info in self.tabs.items():
                    tab_fn = tab_info.get('filename')
                    if tab_fn and os.path.normpath(tab_fn) == filename:
                        self.notebook.select(tab_id)
                        return
                
                with open(filename, 'r', encoding='utf-8') as data:
                    self.create_tab(filename=filename, text_content=data.read())
        except FileNotFoundError:
            return None

    def save_file_as(self, event=None):
        """
        Define file name, extension and save file.
        """
        if not self.current_tab: return False
        
        tab = self.current_tab
        try:
            title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
            filename = tkFileDialog.asksaveasfilename(
                initialfile=title,
                defaultextension='.txt', filetypes=self.file_options)
            if not filename:
                return False
                
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
        """AutoSave file if it was opened else "Save as"."""
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
        else:
            return self.save_file_as()

    def quit_app(self):
        for tab_id in list(self.tabs.keys()):
            tab = self.tabs.get(tab_id)
            if tab and tab.get('is_modified', False):
                self.notebook.select(tab_id)
                title = os.path.basename(tab['filename']) if tab['filename'] else "Untitled"
                response = tkMessageBox.askyesnocancel("Save Changes", f"Do you want to save changes to {title}?")
                if response is True:
                    saved = self.save_file()
                    if not saved:
                        return
                elif response is None:
                    return

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
        tkMessageBox.showinfo("Notepad", "Simple but Good :)")
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            raise e
        
    def tab(self, arg):
        """Change "TAB" button behaviour. Insert 4 spaces"""
        if not self.text_area: return 'break'
        self.text_area.insert(tk.INSERT, " " * self.tab_width)
        return 'break'
    
    def shift_tab(self, event=None):
        """
        Change "Shift+TAB" behaviour. Return icursor 4 spaces back.
        https://stackoverflow.com/a/43920993
        """
        if not self.text_area: return 'break'
        # get 4 characters before icursor
        previous_characters = self.text_area.get(
            "insert -%dc" % self.tab_width, tk.INSERT)
        # if previous characters are spaces -> remove them
        if previous_characters == " " * self.tab_width:
            self.text_area.delete("insert-%dc" % self.tab_width, tk.INSERT)
        return "break"
       
    def theme_activate(self):
        """Change background, font color, icursor color"""
        self.seach_box_background()
        
        # Map themes to: (Text BG, Text FG, Cursor Color, sv_ttk Theme)
        theme_map = {
            0: ('#1e1e1e', '#d4d4d4', 'white', 'dark'),      # Default Dark
            1: ('#ffffff', '#000000', 'black', 'light'),     # Default Light
            2: ('#272822', '#f8f8f2', 'white', 'dark'),      # Monokai
            3: ('#002b36', '#839496', 'white', 'dark'),      # Solarized Dark
            4: ('#fdf6e3', '#657b83', 'black', 'light'),     # Solarized Light
            5: ('#282a36', '#f8f8f2', 'white', 'dark'),      # Dracula
            6: ('#2e3440', '#d8dee9', 'white', 'dark'),      # Nord
            7: ('#0d1117', '#c9d1d9', 'white', 'dark')       # GitHub Dark
        }

        val = self.variable_theme.get()
        if val in theme_map:
            bg, fg, insert, sv_theme = theme_map[val]
            sv_ttk.set_theme(sv_theme)
            
            for tab in self.tabs.values():
                tab['text_area'].config(bg=bg, fg=fg, insertbackground=insert)
                if self.variable_line_bar.get() == 0:
                    tab['line_count_bar'].config(bg=bg)
            
            if self.variable_statusbar.get() == 0:
                self.statusbar.config(bg="#007acc" if sv_theme == "dark" else "#005999", fg="white")
                
            # Refresh syntax highlighting colors based on new theme
            self.switch_syntax_highlight()
       
    def vertical_line(self, event=None):
        """Inseert or remove vertical marker"""
        for tab in self.tabs.values():
            canvas_line = tab['canvas_line']
            if self.variable_marker.get() == 0:
                canvas_line.place_forget()  # Unmap widget
            elif self.variable_marker.get() == 1:
                canvas_line.place(x=640, height=self.root.winfo_height())
            elif self.variable_marker.get() == 2:
                canvas_line.place(x=960, height=self.root.winfo_height())

    def count_text_area(self, event=None):
        """
        Count line and column where cursor inserted.
        Count total amount of symbols.
        Show line, col and symb inside statusbar.
        """
        if not self.text_area: return
        line, col = self.text_area.index("insert").split(".")
        symb_count = self.text_area.count(1.0, "end-1c", "chars")
        symb = str(symb_count[0]) if symb_count else "0"
        self.statusbar.config(
            text=f"Line: {line} | Col: {col} | Symbols: {symb}")
        
        # if self.text_area.edit_modified():
            # Insert "*" symbol to filename when text area modified
            # Need to remake
            # self.root.title(os.path.basename(self.filename) + '*')

    def icursor_modify(self, event):
        """
        Draw line number inside line-count bar.
        """
        if self.line_count_bar:
            self.line_count_bar.redraw()
    
    def line_bar_color(self, event=None):
        """Change color of line-count bar"""
        for tab in self.tabs.values():
            line_count_bar = tab['line_count_bar']
            text_area = tab['text_area']
            if self.variable_line_bar.get() == 0:
                line_count_bar.config(bg=text_area.cget('bg'))
            elif self.variable_line_bar.get() == 1:
                line_count_bar.config(bg='lightsteelblue3')
            elif self.variable_line_bar.get() == 2:
                line_count_bar.config(bg='yellow')
            elif self.variable_line_bar.get() == 3:
                line_count_bar.config(bg='dodger blue')
            elif self.variable_line_bar.get() == 4:
                line_count_bar.config(bg='Indian red')
    
    def statusbar_color(self, event=None):
        """Change color of bottom status bar"""
        if self.variable_statusbar.get() == 0:
            is_dark = sv_ttk.get_theme() == "dark"
            self.statusbar.config(bg="#007acc" if is_dark else "#005999", fg="white")
        elif self.variable_statusbar.get() == 1:
            self.statusbar.config(bg='lightsteelblue3', fg='black')
        elif self.variable_statusbar.get() == 2:
            self.statusbar.config(bg='yellow', fg='black')
        elif self.variable_statusbar.get() == 3:
            self.statusbar.config(bg='dodger blue', fg='white')
        elif self.variable_statusbar.get() == 4:
            self.statusbar.config(bg='Indian red', fg='white')
        else:
            return "Error"

    def hide_menu(self, event=None):
        """Hide main menu"""
        fake_menu_bar = tk.Menu(self.root)
        if self.variable_hide_menu.get() == False:
            self.root.config(menu=fake_menu_bar)
            self.variable_hide_menu.set(True)
        elif self.variable_hide_menu.get() == True:
            self.root.config(menu=self.menu_bar)
            self.variable_hide_menu.set(False)
        else:
            return None
    
    def statusbar_show_remove(self):
        """
        Hide(remove) bottom status bar.
        Create combined event "<<ButtonKeyRelease>>.
        Delete "<<ButtonKeyRelease>> if statusbar removed."
        """
        if self.variable_statusbar_hide.get() == False:
            try:
                for tab in self.tabs.values():
                    try:
                        tab['text_area'].event_delete("<<ButtonKeyRelease>>")
                    except tk.TclError:
                        pass
                self.statusbar.grid_forget()
            except TypeError:
                pass
        elif self.variable_statusbar_hide.get() == True:
            self.statusbar.grid(column=0, columnspan=3, row=1, sticky='wes')
            for tab in self.tabs.values():
                tab['text_area'].event_add("<<ButtonKeyRelease>>", "<ButtonRelease>", "<KeyRelease>")
                tab['text_area'].bind("<<ButtonKeyRelease>>", self.count_text_area)
        else:
            return None
    
    def line_bar_show_remove(self):
        """
        Hide(remove) line-count bar.
        Bind custom event "<<IcursorModify>>".
        Undind if line_count_bar removed.
        """
        if self.variable_line_bar_hide.get() == False:
            for tab in self.tabs.values():
                try:
                    tab['line_count_bar'].delete("all")
                    tab['line_count_bar'].grid_forget()
                    tab['text_area'].unbind("<<IcursorModify>>")
                except TypeError:
                    pass
        elif self.variable_line_bar_hide.get() == True:
            for tab in self.tabs.values():
                tab['line_count_bar'].grid(column=0, row=0, sticky='ns')
                tab['line_count_bar'].attach(tab['text_area'])
                tab['text_area'].bind("<<IcursorModify>>", self.icursor_modify)
        else:
            return None

    def dpi_awareness(self):
        """Set DPI Awareness  (Windows 10 and 8)"""
        if self.os_platform == 'win32':
            try:
                import ctypes

                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (ImportError, OSError):
                pass
    
    def syntax_highlight(self, event):
        """
        Highlight syntax after KeyRelease only in selected row.

        Args:
            row(str) - number of row, where cursor inserted.
            lines(list) - list of lines
            text_content(str) - get string inside text widget
            data(str) - get string from current row of text widget, 
                with index("row", "row + number of items inside row")

        Source: https://stackoverflow.com/a/32064481,
        https://www.holadevs.com/pregunta/100576/python-pygments-tkinter
        """
        if self._highlight_timer:
            self.root.after_cancel(self._highlight_timer)
        # Debounce the highlighter to prevent UI blocking
        self._highlight_timer = self.root.after(50, self._apply_syntax_highlight)

    def _apply_syntax_highlight(self):
        if not self.text_area: return
        row = self.text_area.index("insert").split(".")[0]

        # Remove old syntax tags from the current line before updating
        for tag in self.text_area.tag_names():
            if tag.startswith("Token."):
                self.text_area.tag_remove(tag, row + ".0", row + ".end")

        data = self.text_area.get(row + ".0", row + ".end")
        self.syntax_colorizer(data, row + ".0")

    def switch_syntax_highlight(self):
        """
        Bind syntax_highlight function to "<KeyRelease>" event, 
        if radio button is not "None".
        If text widget is not empty - colorize it.

        If radio button is "None" - remove Key binding and delete tags.
        
        """
        if self.variable_syntax_highlight.get() != "None":
            self.text_area.bind("<KeyRelease>", self.syntax_highlight)

            is_dark = sv_ttk.get_theme() == "dark"
            
            if is_dark:
                # Modern VS Code Dark Theme syntax colors
                self.text_area.tag_configure("Token.Literal.String.Single", foreground="#ce9178")
                self.text_area.tag_configure("Token.Literal.String.Double", foreground="#ce9178")
                self.text_area.tag_configure("Token.Literal.String", foreground="#ce9178")
                self.text_area.tag_configure("Token.Literal.Number.Integer", foreground="#b5cea8")
                self.text_area.tag_configure("Token.Literal.Number.Float", foreground="#b5cea8")
                self.text_area.tag_configure("Token.Literal.Number", foreground="#b5cea8")
                self.text_area.tag_configure("Token.Name.Builtin", foreground="#4ec9b0")
                self.text_area.tag_configure("Token.Name.Namespace", foreground="#4ec9b0")
                self.text_area.tag_configure("Token.Name.Tag", foreground="#569cd6")
                self.text_area.tag_configure("Token.Name.Attribute", foreground="#9cdcfe")
                self.text_area.tag_configure("Token.Name.Variable", foreground="#9cdcfe")
                self.text_area.tag_configure("Token.Operator", foreground="#d4d4d4")
                self.text_area.tag_configure("Token.Punctuation", foreground="#d4d4d4")
                self.text_area.tag_configure("Token.Keyword.Namespace", foreground="#c586c0")
                self.text_area.tag_configure("Token.Comment.Single", foreground="#6a9955")
                self.text_area.tag_configure("Token.Comment.Hashbang", foreground="#6a9955")
                self.text_area.tag_configure("Token.Comment", foreground="#6a9955")
                self.text_area.tag_configure("Token.Keyword", foreground="#569cd6")
                self.text_area.tag_configure("Token.Generic.Heading", foreground="#569cd6")
            else:
                # Modern VS Code Light Theme syntax colors
                self.text_area.tag_configure("Token.Literal.String.Single", foreground="#a31515")
                self.text_area.tag_configure("Token.Literal.String.Double", foreground="#a31515")
                self.text_area.tag_configure("Token.Literal.String", foreground="#a31515")
                self.text_area.tag_configure("Token.Literal.Number.Integer", foreground="#098658")
                self.text_area.tag_configure("Token.Literal.Number.Float", foreground="#098658")
                self.text_area.tag_configure("Token.Literal.Number", foreground="#098658")
                self.text_area.tag_configure("Token.Name.Builtin", foreground="#267f99")
                self.text_area.tag_configure("Token.Name.Namespace", foreground="#267f99")
                self.text_area.tag_configure("Token.Name.Tag", foreground="#0000ff")
                self.text_area.tag_configure("Token.Name.Attribute", foreground="#001080")
                self.text_area.tag_configure("Token.Name.Variable", foreground="#001080")
                self.text_area.tag_configure("Token.Operator", foreground="#000000")
                self.text_area.tag_configure("Token.Punctuation", foreground="#000000")
                self.text_area.tag_configure("Token.Keyword.Namespace", foreground="#af00db")
                self.text_area.tag_configure("Token.Comment.Single", foreground="#008000")
                self.text_area.tag_configure("Token.Comment.Hashbang", foreground="#008000")
                self.text_area.tag_configure("Token.Comment", foreground="#008000")
                self.text_area.tag_configure("Token.Keyword", foreground="#0000ff")
                self.text_area.tag_configure("Token.Generic.Heading", foreground="#0000ff")

            for tag in self.text_area.tag_names():
                if tag.startswith("Token."):
                    self.text_area.tag_remove(tag, "1.0", tk.END)

            self.text_area.mark_set("range_start", "1.0")
            data = self.text_area.get("1.0", "end-1c")
            self.syntax_colorizer(data, "1.0")

        elif self.variable_syntax_highlight.get() == "None":
            self.text_area.unbind("<KeyRelease>")
            for tag in self.text_area.tag_names():
                if tag.startswith("Token."):
                    self.text_area.tag_delete(tag)
        else:
            return None

    def syntax_colorizer(self, data, start_index, ta=None):
        """
        Colorize market text.
        Must be provided: 
            range with .mark_set(markName, index),
            "data" arg. - content to which range applied 
            e.g. data = text_widget.get("1.0", "end-1c").
        """
        ta = ta or self.text_area
        if not ta: return
        lang = self.variable_syntax_highlight.get()
        try:
            lexer = get_lexer_by_name(lang.lower())
        except ClassNotFound:
            try:
                lexer = get_lexer_by_name("text")
            except ClassNotFound:
                return

        row, col = map(int, start_index.split('.'))

        for token, content in lex(data, lexer):
            lines = content.split('\n')
            if len(lines) == 1:
                end_row = row
                end_col = col + len(lines[0])
            else:
                end_row = row + len(lines) - 1
                end_col = len(lines[-1])

            end_index = f"{end_row}.{end_col}"
            ta.tag_add(str(token), f"{row}.{col}", end_index)
            row, col = end_row, end_col


    def word_wrap(self):
        wrap_mode = "none" if self.variable_word_wrap.get() == 0 else "word"
        for tab in self.tabs.values():
            tab['text_area'].configure(wrap=wrap_mode)

if __name__ == '__main__':
    notepad = Notepad()
    notepad.run()
