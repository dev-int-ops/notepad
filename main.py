import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

from text_widget import TextWidget
from line_enumerator import LineEnumerator
from scrollbar import AutoScrollbar

import os
import sys

from pygments import lex
from pygments.lexers import PythonLexer


class Notepad:
    def __init__(self):
        self.root = tk.Tk()
        
        self.Width = 800
        self.Height = 600

        self.text_area = TextWidget(self.root, undo=True, wrap='none')
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

        self.search_box_label = tk.Label(self.text_area, highlightthickness=0,
            bg='white')

        self.scrollbar_y = AutoScrollbar(self.text_area, orient='vertical')
        self.scrollbar_x = AutoScrollbar(self.text_area, orient='horizontal')

        self.filename = ''
        self.filename_var = ''
        self.file_options = [('All Files', '*.*'), ('Python Files', '*.py'),
                    ('Text Document', '*.txt')]
        
        self.tab_width = 4
        
        self.variable_marker = tk.IntVar()
        self.variable_theme = tk.IntVar()
        self.variable_line_bar = tk.IntVar()
        self.variable_statusbar = tk.IntVar()
        self.variable_hide_menu = tk.BooleanVar()
        self.variable_statusbar_hide = tk.BooleanVar()
        self.variable_line_bar_hide = tk.BooleanVar()
        self.variable_search_box = tk.BooleanVar()
        self.variable_syntax_highligh = tk.BooleanVar()
        self.variable_word_wrap = tk.BooleanVar()
        
        self.canvas_line = tk.Canvas(self.text_area, width=1, height=self.Height,
                highlightthickness=0, bg='lightsteelblue3')
                
        self.statusbar = tk.Label(self.root, text=f"",
            relief=tk.FLAT, anchor='e', highlightthickness=0)
        self.line_count_bar = LineEnumerator(width=32, highlightthickness=0)
        
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

        # Make the textarea auto resizable
        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_columnconfigure(1, weight=1)
        # Make textarea size as window
        self.text_area.grid(column=1, row=0, sticky='nsew')
        
        # Configure Yscrollbar
        self.text_area.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.config(command=self.text_area.yview,
            cursor="sb_v_double_arrow")
        # Configure Xscrollbar
        self.text_area.configure(xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_x.config(command=self.text_area.xview,
            cursor="sb_h_double_arrow")

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
        self.customize_menu.add_cascade(label="Line bar color",
            menu=self.line_bar_menu)
        self.customize_menu.add_cascade(label="Statusbar color",
            menu=self.statusbar_menu)
        self.customize_menu.add_cascade(label='StatusBars',
            menu=self.s_bars_menu)
        self.customize_menu.add_cascade(label="Word wrap",
            menu=self.word_wrap_menu)
        self.customize_menu.add_checkbutton(label="Highlight syntax",
            onvalue=1, offvalue=0, variable=self.variable_syntax_highligh,
            command=self.switch_syntax_highlight)

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
        self.theme_edit.add_checkbutton(label="Azure", onvalue=1,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Aquamarine", onvalue=2,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Black", onvalue=3, offvalue=0,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Deep Sky blue", onvalue=4,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Midnight blue", onvalue=5,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Dark Slate Gray", onvalue=6,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Cyber Dark", onvalue=7,
            variable=self.variable_theme, command=self.theme_activate)
        self.theme_edit.add_checkbutton(label="Gray-Gold", onvalue=8,
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

        # Button bind
        self.text_area.bind('<Tab>', self.tab)
        self.shift_tab_bind()
        self.text_area.bind('<ButtonRelease-3>', self.popup)
        self.text_area.bind('<Control-r>', self.redo)
        self.text_area.bind('<Control-z>', self.undo)
        self.text_area.bind('<Control-a>', self.select_all)
        self.text_area.bind('<Control-s>', self.save_file)
        self.text_area.bind('<Control-Alt-s>', self.save_file_as)
        self.text_area.bind('<Control-n>', self.new_file)
        self.text_area.bind('<Control-o>', self.open_file)
        self.text_area.bind('<Control-h>', self.hide_menu)
        self.root.bind('<Control-f>', self.search_box)

        # Vertical line auto resize
        self.text_area.bind('<Configure>', self.vertical_line)

        # Search box
        self.search_entry = tk.Entry(self.search_box_label, bg='light cyan',
            bd=4, width=29, justify=tk.CENTER)
        self.search_entry.grid(column=1, row=0, columnspan=1)
        self.search_button = tk.Button(self.search_box_label, text='Find all',
            bd=1, command=self.find_match, cursor='arrow')
        self.search_button.grid(column=0, row=0, columnspan=1)
        self.find_next = tk.Button(self.search_box_label, text='Next', 
            bd=1, command=self.next_match, cursor='arrow')
        self.find_next.grid(column=2, row=0, columnspan=1)

        self.replace_with_label = tk.Label(self.search_box_label, bd=4,
            text='Replace with:')
        self.replace_with_label.grid(column=3, row=0, columnspan=1)
        self.replace_match_entry = tk.Entry(self.search_box_label, bg='gold', bd=4,
            width=29, justify=tk.CENTER)
        self.replace_match_entry.grid(column=4, row=0, columnspan=1)
        self.repace_match_button = tk.Button(self.search_box_label, bd=1,
            text='Replace', command=self.replace_match, cursor='arrow')
        self.repace_match_button.grid(column=5, row=0, columnspan=1)

        self.dpi_awareness()
        self.previous_content = self.text_area.get("1.0", tk.END)
        
    def shift_tab_bind(self):
        if self.os_platform == "win32":
            self.text_area.bind('<Shift-Tab>', self.shift_tab)
        elif self.os_platform == "linux":
            self.text_area.bind('<Shift-ISO_Left_Tab>', self.shift_tab)
        else:
            return None

    def search_box(self, event=None):
        """Make Search box appear inside text area"""
        if self.variable_search_box.get() == True:
            # self.search_box_label.place_forget()
            self.search_box_label.pack_forget()
            self.variable_search_box.set(False)
            self.search_entry.unbind('<Return>')
        elif self.variable_search_box.get() == False:
            # self.search_box_label.place(bordermode=tk.INSIDE,
            #     width=self.Width/3, relx=1.0, rely=0.0, anchor='ne')
            self.search_box_label.pack(side=tk.TOP, anchor=tk.NE)
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
        if  self.variable_theme.get() == 1:
            self.search_box_label.config(bg='azure')
        elif  self.variable_theme.get() == 2:
            self.search_box_label.config(bg='aquamarine')
        elif  self.variable_theme.get() == 3:
            self.search_box_label.config(bg='black')
        elif  self.variable_theme.get() == 4:
            self.search_box_label.config(bg='deepskyblue4')
        elif  self.variable_theme.get() == 5:
            self.search_box_label.config(bg='midnight blue')
        elif  self.variable_theme.get() == 6:
            self.search_box_label.config(bg='dark slate gray')
        elif  self.variable_theme.get() == 7:
            self.search_box_label.config(bg='#1f1f2e')
        elif  self.variable_theme.get() == 8:
            self.search_box_label.config(bg='gray17')

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
        self.root.title(self.filename)
        self.filename = ''
        self.text_area.delete(0.0, tk.END)
        
    def open_file(self, event=None):
        try:
            self.filename = tkFileDialog.askopenfilename(
                defaultextension=".txt", filetypes=self.file_options)
            if self.filename is not None:
                with open(self.filename, 'r', encoding='utf-8') as data:
                        self.root.title(os.path.basename(self.filename))
                        self.text_area.delete(0.0, tk.END)
                        self.text_area.insert(0.0, data.read())
        except FileNotFoundError:
            return None

    def save_file_as(self, event=None):
        """
        Define file name, extension and save file.
        Remove '*' symbol from file name.
        """
        self.filename_var = self.filename
        try:
            self.filename = tkFileDialog.asksaveasfilename(
                initialfile=self.root.title().strip("*"),
                defaultextension='.txt', filetypes=self.file_options)
            if self.filename == '':
                self.filename = self.filename_var
            else:
                with open(self.filename, 'w', encoding='utf-8') as data:
                        data.write(self.text_area.get(1.0, tk.END))
                        self.root.title(os.path.basename(self.filename))
        except Exception as e:
            raise e
                
    def save_file(self, event=None):
        """AutoSave file if it was opened else "Save as"."""
        if self.filename != None and self.filename != "":
            with open(self.filename, 'w', encoding='utf-8') as note:
                    note.write(self.text_area.get(1.0, tk.END))
            self.root.title(os.path.basename(self.filename))
        elif self.filename == None or self.filename =='':
            self.save_file_as()
        else:
            return "Error"

    def quit_app(self):
        self.save_file()
        self.root.destroy()
    
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
        
    def cut(self, event=None):
        self.text_area.event_generate("<<Cut>>")
        
    def paste(self, event=None):
        self.text_area.event_generate("<<Paste>>")
        return 'break'
        
    def undo(self, event=None):
        self.text_area.event_generate("<<Undo>>")
        
    def redo(self, event=None):
        self.text_area.event_generate("<<Redo>>")
        
    def select_all(self, event=None):
        self.text_area.event_generate("<<SelectAll>>")
    
    def about(self):
        tkMessageBox.showinfo("Notepad", "Simple but Good :)")
    
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            raise e
        
    def tab(self, arg):
        """Change "TAB" button behaviour. Insert 4 spaces"""
        self.text_area.insert(tk.INSERT, " " * self.tab_width)
        return 'break'
    
    def shift_tab(self, event=None):
        """
        Change "Shift+TAB" behaviour. Return icursor 4 spaces back.
        https://stackoverflow.com/a/43920993
        """
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

        if self.variable_theme.get() == 0:
            self.text_area.config(bg='white', fg='black',
                insertbackground='black')
        elif self.variable_theme.get() == 1:
            self.text_area.config(bg='azure', fg='black',
                insertbackground='black')
        elif self.variable_theme.get() == 2:
            self.text_area.config(bg='aquamarine', fg='black',
                insertbackground='black')
        elif self.variable_theme.get() == 3:
            self.text_area.config(bg='black', fg='white',
                insertbackground='white')
        elif self.variable_theme.get() == 4:
            self.text_area.config(bg='deepskyblue4', fg='light cyan',
                insertbackground='white')
        elif self.variable_theme.get() == 5:
            self.text_area.config(bg='midnight blue', fg='white',
                insertbackground='white')
        elif self.variable_theme.get() == 6:
            self.text_area.config(bg='dark slate gray', fg='linen',
                insertbackground='white')
        elif self.variable_theme.get() == 7:
            self.text_area.config(bg='#1f1f2e', fg='cyan',
                insertbackground='white')
        elif self.variable_theme.get() == 8:
            self.text_area.config(bg='gray17', fg='gold',
                insertbackground='white')
        else:
            return 'Error'
       
    def vertical_line(self, event=None):
        """Inseert or remove vertical marker"""
        if self.variable_marker.get() == 0:
            self.canvas_line.place_forget()  # Unmap widget
        elif self.variable_marker.get() == 1:
            self.canvas_line.place(x=640, height=self.root.winfo_height())
        elif self.variable_marker.get() == 2:
            self.canvas_line.place(x=960, height=self.root.winfo_height())
        else:
            return "Error"          

    def count_text_area(self, event):
        """
        Count line and column where cursor inserted.
        Count total amount of symbols.
        Show line, col and symb inside statusbar.
        """
        line, col = self.text_area.index("insert").split(".")
        symb = str(len(self.text_area.get(1.0, 'end-1c')))
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
        self.line_count_bar.redraw()
    
    def line_bar_color(self, event=None):
        """Change color of line-count bar"""
        if self.variable_line_bar.get() == 0:
            self.line_count_bar.config(bg='SystemButtonFace')
        elif self.variable_line_bar.get() == 1:
            self.line_count_bar.config(bg='lightsteelblue3')
        elif self.variable_line_bar.get() == 2:
            self.line_count_bar.config(bg='yellow')
        elif self.variable_line_bar.get() == 3:
            self.line_count_bar.config(bg='dodger blue')
        elif self.variable_line_bar.get() == 4:
            self.line_count_bar.config(bg='Indian red')
        else:
            return "Error"
    
    def statusbar_color(self, event=None):
        """Change color of bottom status bar"""
        if self.variable_statusbar.get() == 0:
            self.statusbar.config(bg='SystemButtonFace')
        elif self.variable_statusbar.get() == 1:
            self.statusbar.config(bg='lightsteelblue3')
        elif self.variable_statusbar.get() == 2:
            self.statusbar.config(bg='yellow')
        elif self.variable_statusbar.get() == 3:
            self.statusbar.config(bg='dodger blue')
        elif self.variable_statusbar.get() == 4:
            self.statusbar.config(bg='Indian red')
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
                self.text_area.unbind("<<ButtonKeyRelea>>", 
                    self.text_area.bind("<<ButtonKeyRelease>>", 
                    self.count_text_area)) # Make better
                self.text_area.event_delete("<<ButtonKeyRelea>>",
                    "<ButtonRelease>", "<KeyRelease>")
                self.statusbar.grid_forget()
            except TypeError:
                pass
        elif self.variable_statusbar_hide.get() == True:
            self.text_area.event_add("<<ButtonKeyRelease>>", 
                "<ButtonRelease>", "<KeyRelease>")
            self.statusbar.grid(column=0, columnspan=3, row=1, sticky='wes')
            self.text_area.bind("<<ButtonKeyRelease>>", self.count_text_area)
        else:
            return None
    
    def line_bar_show_remove(self):
        """
        Hide(remove) line-count bar.
        Bind custom event "<<IcursorModify>>".
        Undind if line_count_bar removed.
        """
        if self.variable_line_bar_hide.get() == False:
            try:
                self.line_count_bar.delete("all")
                self.line_count_bar.grid_forget()
                self.text_area.unbind("<<IcursorModify>>",
                    self.text_area.bind("<<IcursorModify>>",
                    self.icursor_modify))
            except TypeError:
                pass
        elif self.variable_line_bar_hide.get() == True:
            self.line_count_bar.grid(column=0, row=0, sticky='ns')
            self.line_count_bar.attach(self.text_area)
            self.text_area.bind("<<IcursorModify>>", self.icursor_modify)
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
        row = self.text_area.index("insert").split(".")[0]
        text_content = self.text_area.get("1.0", tk.END)
        lines = text_content.split("\n")

        if (self.previous_content != text_content):
            self.text_area.mark_set("range_start", row + ".0")
            
            # Remove old syntax tags from the current line before updating
            for tag in self.text_area.tag_names():
                if tag.startswith("Token."):
                    self.text_area.tag_remove(tag, row + ".0", row + ".end")

            data = self.text_area.get(
                row + ".0", row + "." +\
                str(len(lines[int(row) - 1])))

            self.syntax_colorizer(data)

        self.previous_content = self.text_area.get("1.0", tk.END)

    def switch_syntax_highlight(self):
        """
        Bind syntax_highlight function to "<KeyRelease>" event, 
        if check_button is pressed on.
        If text widget is not empty - colorize it.

        If check_button switched off - remove Key binding and delete tags.
        
        """
        if self.variable_syntax_highligh.get() == True:
            self.text_area.bind("<KeyRelease>", self.syntax_highlight)

            self.text_area.tag_configure("Token.Literal.String.Single",
                foreground="green")
            self.text_area.tag_configure("Token.Literal.String.Double",
                foreground="green")
            self.text_area.tag_configure("Token.Literal.Number.Integer",
                foreground="tomato")
            self.text_area.tag_configure("Token.Literal.Number.Float",
                foreground="tomato")
            self.text_area.tag_configure("Token.Name.Builtin",
                foreground="light salmon")
            self.text_area.tag_configure("Token.Name.Namespace",
                foreground="forest green")
            self.text_area.tag_configure("Token.Operator",
                foreground="light sea green")
            self.text_area.tag_configure("Token.Punctuation",
                foreground="SlateBlue2")
            self.text_area.tag_configure("Token.Keyword.Namespace",
                foreground="dark olive green")
            self.text_area.tag_configure("Token.Comment.Single",
                foreground="grey")
            self.text_area.tag_configure("Token.Comment.Hashbang",
                foreground="grey")
            self.text_area.tag_configure("Token.Keyword",
                foreground="brown")

            self.text_area.mark_set("range_start", "1.0")
            data = self.text_area.get("1.0", "end-1c")
            self.syntax_colorizer(data)

        elif self.variable_syntax_highligh.get() == False:
            self.text_area.unbind("<KeyRelease>")
            self.text_area.tag_delete(
                "Token.Literal.String.Single", "Token.Literal.String.Double",
                "Token.Literal.Number.Integer", "Token.Literal.Number.Float",
                "Token.Name.Builtin", "Token.Name.Namespace", "Token.Operator",
                "Token.Punctuation", "Token.Comment.Hashbang",
                "Token.Keyword.Namespace", "Token.Comment.Single",
                "Token.Keyword")
        else:
            return None

    def syntax_colorizer(self, data):
        """
        Colorize market text.
        Must be provided: 
            range with .mark_set(markName, index),
            "data" arg. - content to which range applied 
            e.g. data = text_widget.get("1.0", "end-1c").
        """
        for token, content in lex(data, PythonLexer()):
            self.text_area.mark_set(
                "range_end", "range_start + %dc" % len(content))
            self.text_area.tag_add(str(token), "range_start", "range_end")
            self.text_area.mark_set("range_start", "range_end")


    def word_wrap(self):
        if self.variable_word_wrap.get() == 0:
            self.text_area.configure(wrap="none")
        else:
            self.text_area.configure(wrap="word")

if __name__ == '__main__':
    notepad = Notepad()
    notepad.run()
