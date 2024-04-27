import tkinter as tk
import os
from threading import Thread
import time
from PIL import Image, ImageTk

from manager import Manager


class ThemeConfigure():
    def __init__(self, gui):
        self.gui = gui

        # main / second / hightlight / font
        self.themes = [
            ['white', '#f4f6f5', 'yellow', 'black'],
            ['black', '#575a58', 'darkred', 'white'],
            ['#Aeaee4', '#A0A0EC', 'lightyellow', '#020285'],
            ['black', 'black', '#373737', '#05CD05'],
            ['#30d5c8', '#17ECDB', '#6248F4', 'black'],
            ['white', 'lightyellow', 'orange', 'black'],
            ['white', 'red', 'red', 'black'],
            ['#167234', '#A301BF', '#A301BF', 'white'],
            ['black', '#0E4720', '#0E4720', '#D612F8']
        ]

        self.max_theme = len(self.themes)

        self.current_theme = -1

        self.next_theme()

    def next_theme(self):
        self.current_theme = (self.current_theme + 1) % self.max_theme
        self.gui.main_color = self.themes[self.current_theme][0]
        self.gui.second_color = self.themes[self.current_theme][1]
        self.gui.highlight_color = self.themes[self.current_theme][2]
        self.gui.font_color = self.themes[self.current_theme][3]

    def update_theme(self):
        self.gui.update_theme()
        self.gui.infowindow.update_theme()
        self.gui.bar.update_theme()


class ContextMenu(tk.Listbox):
    def __init__(self, gui, frame, x, y, cell, *args, **kwargs):
        tk.Listbox.__init__(self, frame, *args, **kwargs)
        self.gui = gui
        self.frame = frame
        self.x = x
        self.y = y
        self.cell = cell

        self.draw()

    def draw(self):
        self.gui.set_cursor(self.cell.index)

        self.menu = tk.Menu(self, tearoff=0, bg=self.gui.second_color,
                            fg=self.gui.font_color, font=self.gui.font,
                            activebackground=self.gui.highlight_color,
                            activeforeground=self.gui.font_color)
        
        if self.cell.file.type == 'directory':
            self.menu.add_command(label='Go to directory',
                                  command=lambda: 
                                  self.gui.move_to_dir())
        else:
            self.menu.add_command(label='Open',
                                  command=lambda: 
                                  self.gui.move_to_dir())
        self.menu.add_command(label='Rename', 
                              command=lambda: 
                              self.gui.infowindow.title.focus())
        self.menu.add_command(label='Delete', 
                              command=lambda:
                              Thread(target=self.gui.delete_file).start())

        self.menu.add_separator()
        
        self.menu.add_command(label='Copy', 
                              command=lambda: 
                              Thread(target=self.gui.copy_file).start())
        if self.gui.copied_file:
            self.menu.add_command(label='Paste', 
                                  command=lambda: 
                                  Thread(target=self.gui.paste_action).start())
        
        self.menu.add_command(label='Move', 
                              command=lambda: 
                              Thread(target=self.gui.move_file).start())
        if self.gui.moving_file:
            self.menu.add_command(label='Move here', 
                                  command=lambda: 
                                  Thread(target=self.gui.move_complete).start()
                                  )
        
        self.menu.add_separator()

        self.menu.add_command(label='New Directory',
                              command=lambda: self.gui.make_dir())
        self.menu.add_command(label='New File', 
                              command=lambda: self.gui.make_file())

        self.menu.tk_popup(self.x, self.y, 0)


class Bar():
    def __init__(self, gui, frame):
        self.gui = gui
        self.frame = frame

        self.ascending = True

        self.configure_frame()
        self.configure_layout()

    def change_sorting_direction(self):
        self.ascending = not self.ascending
        self.b_sort_direction.configure(text=('⮬' if self.ascending else '⮯'))
        
        self.gui.manager.sorting_ascending = self.ascending
        self.gui.manager.update_files(self.gui.manager.current_dir)
        self.gui.show_dir()

    def set_sorting_by(self, a):
        self.gui.manager.sorting_by = self.menu_current.get()
        self.gui.manager.update_files(self.gui.manager.current_dir)
        self.gui.show_dir()

    def set_dir(self, dir):
        self.dir.delete(0, tk.END)
        self.dir.insert(tk.END, dir)

    def change_theme(self):
        self.gui.themeconfigure.next_theme()
        self.gui.themeconfigure.update_theme()

    def update_theme(self):
        self.update_button_options()
        self.b_back.configure(**self.button_options)
        self.b_forward.configure(**self.button_options)
        self.b_reload.configure(**self.button_options)
        self.b_sort_direction.configure(**self.button_options)
        self.b_sort_by.configure(**self.button_options)
        self.b_change_theme.configure(**self.button_options)
        self.dir.configure(bg=self.gui.main_color, fg=self.gui.font_color, 
                           insertbackground=self.gui.font_color)
        self.menu_sort_by.configure(bg=self.gui.second_color, 
                                    fg=self.gui.font_color, font=self.gui.font,
                                    activebackground=self.gui.highlight_color, 
                                    activeforeground=self.gui.font_color)

    def configure_frame(self):
        self.frame.configure(bg=self.gui.main_color)
        self.update_button_options()
        
    def update_button_options(self):
        self.button_options = {'bg': self.gui.main_color,
                               'fg': self.gui.font_color,
                               'font': self.gui.font,
                               'borderwidth': 0,
                               'activeforeground': self.gui.font_color,
                               'activebackground': self.gui.highlight_color,
                               'highlightthickness': 0,
                               'relief': 'solid'}
        
    def configure_layout(self):
        self.b_back = tk.Button(self.frame, text="⫷", **self.button_options,
                                command=lambda: self.gui.backward())

        self.b_forward = tk.Button(self.frame, text="⫸",
                                   **self.button_options,
                                   command=lambda: self.gui.forward())

        self.b_reload = tk.Button(self.frame, text="↻", **self.button_options,
                                  command=lambda: 
                                  self.gui.show_dir(force=True))

        self.dir = tk.Entry(self.frame, bd=0, bg=self.gui.main_color, 
                            fg=self.gui.font_color, font=self.gui.font,
                            insertbackground=self.gui.font_color)

        self.b_sort_direction = tk.Button(self.frame, text="⮬", 
                                          **self.button_options,
                                          command=lambda: 
                                          self.change_sorting_direction())

        self.b_sort_by = tk.Menubutton(self.frame, text='Sorting by', 
                                       **self.button_options)
        self.menu_sort_by = tk.Menu(self.b_sort_by, tearoff=0, 
                                    bg=self.gui.second_color, 
                                    fg=self.gui.font_color, font=self.gui.font,
                                    activebackground=self.gui.highlight_color, 
                                    activeforeground=self.gui.font_color)
        
        self.menu_current = tk.StringVar(value='name')
        self.menu_sort_by.add_radiobutton(label='name', 
                                          variable=self.menu_current, 
                                          value='name', font=self.gui.font,
                                          command=lambda: 
                                          self.set_sorting_by())
        self.menu_sort_by.add_radiobutton(label='ext', 
                                          variable=self.menu_current, 
                                          value='ext', font=self.gui.font, 
                                          command=lambda: 
                                          self.set_sorting_by('ext'))
        self.menu_sort_by.add_radiobutton(label='size', 
                                          variable=self.menu_current, 
                                          value='size', font=self.gui.font, 
                                          command=lambda: 
                                          self.set_sorting_by('size'))
        self.menu_sort_by.add_radiobutton(label='time',
                                          variable=self.menu_current, 
                                          value='mtime', font=self.gui.font, 
                                          command=lambda: 
                                          self.set_sorting_by('time'))
        self.b_sort_by['menu'] = self.menu_sort_by

        self.b_change_theme = tk.Button(self.frame, text="☽", 
                                        **self.button_options,
                                        command=lambda: self.change_theme())

        self.padding = {'ipady': 5,
                        'ipadx': 5}

        self.b_back.grid(row=0, column=0, **self.padding)
        self.b_forward.grid(row=0, column=1, **self.padding)
        self.b_reload.grid(row=0, column=2, **self.padding)
        self.dir.grid(row=0, column=3, sticky='ew', **self.padding)
        self.b_sort_direction.grid(row=0, column=4, **self.padding)
        self.b_sort_by.grid(row=0, column=5, **self.padding)
        self.b_change_theme.grid(row=0, column=6, **self.padding)


class InfoWindow():
    def __init__(self, frame, gui):
        self.frame = frame
        self.gui = gui

        self.image_id = 0 # for multi threading
        self.image_size = 128

        self.configure_frame()
        self.configure_layout()

        self.img_dir = ImageTk.PhotoImage(Image.open('icons/dir.png')
                                          .resize([128, 128]))
        self.img_nofile = ImageTk.PhotoImage(Image.open('icons/nofile.png')
                                             .resize([128, 128]))
        self.img_loading = ImageTk.PhotoImage(Image.open('icons/loading.png')
                                              .convert("RGBA")
                                              .resize([128, 128]))

    def copy_show(self, file):
        self.copy_path.grid(row=5, column=0, rowspan=1, columnspan=3,
                            sticky='ew', **self.padding)
        self.b_paste.grid(row=5, column=3, rowspan=1, columnspan=1, 
                          sticky='ew', **self.padding)

        self.copy_path['text'] = file

    def copy_hide(self):
        self.gui.copied_file = None
        self.copy_path.grid_remove()
        self.b_paste.grid_remove()

    def move_show(self, file):
        self.move_path.grid(row=6, column=0, rowspan=1, columnspan=3, 
                            sticky='ew', **self.padding)
        self.b_move_complete.grid(row=6, column=3, rowspan=1, columnspan=1, 
                                  sticky='ew', **self.padding)

        self.move_path['text'] = file

    def move_hide(self):
        self.move_path.grid_remove()
        self.b_move_complete.grid_remove()

    def update(self, cell):
        self.image.configure(image=self.img_loading)
        self.image.image = self.img_loading
        self.image_id += 1
        Thread(target=self.set_photo, args=(cell, self.image_id)).start()

        self.title.delete(0, tk.END)
        self.title.insert(0, cell.file.name)

        self.type.configure(text=cell.file.type)
        self.size.configure(text=Manager.sizeof_fmt(cell.file.size))
        self.ctime.configure(text=cell.file.ctime
                             .strftime("Created: %H:%M:%S, %Y/%m/%d"))
        self.mtime.configure(text=cell.file.mtime
                             .strftime("Modified: %H:%M:%S, %Y/%m/%d"))

    def set_photo(self, cell, current_image_id):
        if cell.file.type == 'directory':
            img = self.img_dir
        elif cell.file.ext.lower() in ('jpg', 'png', 'jpeg'):
            img = Image.open(cell.file.fulldir)
            hsize = self.image_size
            wsize = hsize / img.size[1]
            wsize = min(int(img.size[0] * wsize), hsize * 2)
            img = img.resize([wsize, hsize], Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
        elif cell.file.ext.lower() in ('mp4', 'ogg', 'avi',
                                       'mov', 'mpg', 'flv'):
            img = Image.open('icons/video.png').resize([128, 128])
            img = ImageTk.PhotoImage(img)
        elif cell.file.ext.lower() in [file[:file.rfind('.')] 
                                       for file in os.listdir('icons')]:
            img = Image.open(f'icons/{cell.file.ext}.png').resize([128, 128])
            img = ImageTk.PhotoImage(img)
        else:
            img = self.img_nofile
        
        if current_image_id == self.image_id:
            self.image.configure(image=img)
            self.image.image = img

    def update_theme(self):
        self.update_button_options()

        self.image.configure(bg=self.gui.main_color)
        self.title.configure(bg=self.gui.main_color, fg=self.gui.font_color, 
                             insertbackground=self.gui.font_color)
        self.type.configure(bg=self.gui.main_color, fg=self.gui.font_color)
        self.size.configure(bg=self.gui.main_color, fg=self.gui.font_color)
        self.ctime.configure(bg=self.gui.main_color, fg=self.gui.font_color)
        self.mtime.configure(bg=self.gui.main_color, fg=self.gui.font_color)

        self.b_open.configure(**self.button_options)
        self.b_copy.configure(**self.button_options)
        self.b_move.configure(**self.button_options)
        self.b_delete.configure(**self.button_options)
        self.b_mkdir.configure(**self.button_options)
        self.b_mkfile.configure(**self.button_options)
        self.b_paste.configure(**self.button_options)
        self.b_move_complete.configure(**self.button_options)

        self.copy_path.configure(bg=self.gui.main_color,
                                 fg=self.gui.font_color)
        self.move_path.configure(bg=self.gui.main_color, 
                                 fg=self.gui.font_color)

    def configure_frame(self):
        self.frame.configure(bg=self.gui.main_color)
        self.update_button_options()

    def update_button_options(self):
        self.button_options = {'bg': self.gui.second_color,
                               'fg': self.gui.font_color,
                               'font': self.gui.font,
                               'bd': 1,
                               'activeforeground': self.gui.font_color,
                               'activebackground': self.gui.highlight_color,
                               'highlightthickness': 0,
                               'relief': 'ridge'}

    def configure_layout(self):
        self.padding = {
            'ipady': 5,
            'ipadx': 5,
            'padx': 5,
            'pady': 5
        }

        self.image = tk.Label(self.frame, bg=self.gui.main_color)
        self.title = tk.Entry(self.frame, width=30, justify='center',
                              bg=self.gui.main_color, 
                              insertbackground=self.gui.font_color,
                              fg=self.gui.font_color)
        self.type = tk.Label(self.frame, bg=self.gui.main_color)
        self.size = tk.Label(self.frame, bg=self.gui.main_color)
        self.ctime = tk.Label(self.frame, bg=self.gui.main_color)
        self.mtime = tk.Label(self.frame, bg=self.gui.main_color)

        self.image.grid(row=1, column=0, rowspan=1, columnspan=4, 
                        sticky='nsew', **self.padding)
        self.title.grid(row=2, column=0, rowspan=1, columnspan=4, 
                        **self.padding)
        self.type.grid(row=3, column=0, rowspan=1, columnspan=2, 
                       sticky='w', **self.padding)
        self.size.grid(row=4, column=0, rowspan=1, columnspan=2, 
                       sticky='w', **self.padding)
        self.ctime.grid(row=3, column=2, rowspan=1, columnspan=2, 
                        sticky='e', **self.padding)
        self.mtime.grid(row=4, column=2, rowspan=1, columnspan=2, 
                        sticky='e', **self.padding)

        self.copy_path = tk.Label(self.frame, bg=self.gui.main_color, 
                                  fg=self.gui.font_color)
        self.b_paste = tk.Button(self.frame, text='Paste', 
                                 **self.button_options,
                                 command=lambda: 
                                 Thread(target=self.gui.paste_action).start())
        self.move_path = tk.Label(self.frame, bg=self.gui.main_color, 
                                  fg=self.gui.font_color)
        self.b_move_complete = tk.Button(self.frame, text='Move here', 
                                         **self.button_options, 
                                         command=lambda: 
                                         Thread(target=
                                                self.gui.move_complete).start()
                                        )
        
        self.b_open = tk.Button(self.frame, text='Open', **self.button_options,
                                command=lambda: self.gui.move_to_dir())
        self.b_copy = tk.Button(self.frame, text='Copy', **self.button_options,
                                command=lambda: 
                                Thread(target=self.gui.copy_file).start())
        self.b_move = tk.Button(self.frame, text='Move', **self.button_options,
                                command=lambda: 
                                Thread(target=self.gui.move_file).start())
        self.b_delete = tk.Button(self.frame, text='Delete', 
                                  **self.button_options,
                                  command=lambda: 
                                  Thread(target=self.gui.delete_file).start())
        self.b_mkdir = tk.Button(self.frame, text='New directory...', 
                                 **self.button_options,
                                 command=lambda: self.gui.make_dir())
        self.b_mkfile = tk.Button(self.frame, text='New File...', 
                                  **self.button_options, 
                                  command=lambda: self.gui.make_file())
        
        self.b_open.grid(row=7, column=0, rowspan=1, columnspan=1, 
                         **self.padding, sticky='ew')
        self.b_copy.grid(row=7, column=1, rowspan=1, columnspan=1, 
                         **self.padding, sticky='ew')
        self.b_move.grid(row=7, column=2, rowspan=1, columnspan=1, 
                         **self.padding, sticky='ew')
        self.b_delete.grid(row=7, column=3, rowspan=1, columnspan=1, 
                           **self.padding, sticky='ew')
        self.b_mkdir.grid(row=8, column=0, rowspan=1, columnspan=2, 
                          **self.padding, sticky='ew')
        self.b_mkfile.grid(row=8, column=2, rowspan=1, columnspan=2, 
                           **self.padding, sticky='ew')
        

class Cell():
    def __init__(self, gui, frame, index, file):
        self.gui = gui
        self.frame = frame
        self.index = index
        self.file = file
        self.color = self.gui.main_color
        self.obj = None

    def draw(self):
        if self.obj:
            self.obj.destroy()
        self.obj = tk.Text(self.frame, wrap='none', bg=self.color, bd=0, 
                           height=1, highlightthickness=2, 
                           highlightbackground=self.gui.main_color,
                           cursor='arrow', width=50, fg=self.gui.font_color, 
                           font=self.gui.font, padx=2, pady=2, takefocus=0)
        self.obj.grid(row=self.index, column=0)

        name = self.file.name
        if self.file.type == 'directory':
            name = '● ' + name
        self.obj.insert(tk.END, name)
        self.obj.config(state=tk.DISABLED)

        self.obj.bind('<Enter>', lambda e: 
                      self.obj.config(highlightbackground=
                                      self.gui.highlight_color))

        self.obj.bind('<Leave>', lambda e: 
                      self.obj.config(highlightbackground=self.gui.main_color))

        self.obj.bind('<Button-1>', lambda e: self.click())

        self.obj.bind('<Button-3>', lambda e: 
                      self.gui.create_contextmenu(self))

    def click(self):
        if self.gui.cursor - self.gui.current_row == self.index:
            if self.gui.root.focus_get().master in (None, self.gui.left_frame):
                self.gui.move_to_dir()
        else:
            self.gui.set_cursor(self.index)

class GUI():
    WIDTH = 720
    HEIGHT = 480

    def __init__(self):
        self.root = tk.Tk()

        self.themeconfigure = ThemeConfigure(self)
        self.font = ('Arial', 10)

        self.configure_screen()
        self.configure_layout()
        self.configure_binds()

        self.manager = Manager(os.getcwd().split(os.path.sep)[0] + os.path.sep)

        self.current_row = 0
        self.cursor = 0
        self.cells = []

        self.editing_window = 0 # for multi threading
        self.max_rows = 0
        Thread(target=self.set_max_rows, args=(GUI.HEIGHT,)).start()

        self.copied_file = None
        self.moving_file = None

    def check_focus(self, e):
        focus = self.root.focus_get().master

        if focus == self.top_frame:
            if e.keysym == 'Return':
                if os.path.exists(self.bar.dir.get()):
                    self.show_dir(dir=os.path.normpath(self.bar.dir.get()))
                    self.root.focus()
            elif e.keysym == 'Escape':
                self.root.focus()
        
        if focus == self.left_frame:
            if e.keysym == 'Return':
                self.show_dir(dir=self.bar.dir.get())
                self.root.focus()
            elif e.keysym == 'Escape':
                self.return_to_dir()
                self.root.focus()

        if focus == self.right_frame:
            if e.keysym == 'Return':
                self.rename_file()
                self.root.focus()
            elif e.keysym == 'Escape':
                self.root.focus()

        if focus == None:
            if e.keysym == 'Return':
                self.move_to_dir()
            elif e.keysym == 'Escape':
                self.return_to_dir()

    def create_contextmenu(self, cell):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.contextmenu = ContextMenu(self, self.left_frame, x, y, cell)

    def rename_file(self):
        name = self.infowindow.title.get()
        self.manager.rename_file(self.get_current_cell().file, name)
        self.show_dir(force=True)
        self.focus_on_file(name)
        self.update()

    def make_dir(self):
        name = self.manager.make_dir()
        self.show_dir(force=True)
        self.focus_on_file(name)
        self.update()
        self.infowindow.title.focus()

    def make_file(self):
        name = self.manager.make_file()
        self.show_dir(force=True)
        self.focus_on_file(name)
        self.update()
        self.infowindow.title.focus()

    def delete_file(self):
        self.manager.delete_file(self.get_current_cell().file.fulldir)
        self.show_dir(force=True)

    def copy_file(self):
        self.copied_file = self.get_current_cell().file.fulldir
        self.infowindow.copy_show(self.copied_file)

    def paste_action(self):
        name = self.manager.paste_file(self.copied_file, 
                                       self.manager.current_dir)
        self.show_dir(force=True)
        self.focus_on_file(name)
        self.update()

    def move_file(self):
        self.moving_file = self.get_current_cell().file.fulldir
        self.infowindow.move_show(self.moving_file)

    def move_complete(self):
        name = self.manager.move_file(self.moving_file, 
                                      self.manager.current_dir)
        self.show_dir(force=True)
        if self.moving_file == self.copied_file:
            self.infowindow.copy_hide()
        self.moving_file = None
        self.infowindow.move_hide()
        self.focus_on_file(name)
        self.update()

    def get_current_cell(self):
        return self.cells[self.cursor - self.current_row]

    def focus_on_file(self, filename):
        cursor = 0
        for file in self.manager.files:
            if file.name == filename:
                break
            cursor += 1
        self.set_absolute_position(cursor)

    def set_absolute_position(self, position):
        self.current_row = max(position - self.max_rows + 1, 0)
        self.cursor = position
        self.show_dir(force=True, reset_cursor=False)

    def set_cursor(self, position):
        self.get_current_cell().color = self.main_color
        self.get_current_cell().draw()
        self.cursor = position + self.current_row
        self.get_current_cell().color = self.highlight_color
        self.get_current_cell().draw()
        self.update(bar=False)

    def move_cursor(self, direction):
        if 0 <= self.cursor + direction < self.manager.dirlen:
            self.get_current_cell().color = self.main_color
            self.get_current_cell().draw()
            self.cursor += direction
            if ((self.cursor - self.current_row >= len(self.cells) - 1) 
                and (self.cursor + 1 < self.manager.dirlen)):
                self.current_row += 1
                self.show_dir(reset_cursor=False)
            if ((self.cursor - self.current_row <= 0) 
                and (self.cursor - 1 >= 0)):
                self.current_row -= 1
                self.show_dir(reset_cursor=False)
            self.get_current_cell().color = self.highlight_color
            self.get_current_cell().draw()

            self.update(bar=False)

    def move_to_dir(self):
        isfile = self.manager.change_dir(self.get_current_cell().file.fulldir,
                                self.current_row, self.cursor)
        self.show_dir(reset_cursor=not(isfile))

    def return_to_dir(self):
        if self.manager.history_cursor > 0:
            self.backward()
        else:
            self.manager.change_dir(os.path.dirname(self.manager.current_dir),
                                    self.current_row, self.cursor)
            self.show_dir()

    def forward(self):
        result = self.manager.forward()
        if result:
            self.current_row, self.cursor = result
            self.show_dir(cursor=self.cursor,
                          current_row=self.current_row)

    def backward(self):
        result = self.manager.backward()
        if result:
            self.current_row, self.cursor = result
            self.show_dir(cursor=self.cursor,
                          current_row=self.current_row)

    def show_dir(self, dir=None, reset_cursor=True, cursor=0, current_row=0, 
                 force=False):
        if dir is not None:
            self.manager.change_dir(dir, cursor=self.cursor, 
                                    current_row=self.current_row)
        if force:
            self.manager.change_dir(self.manager.current_dir)

        for c in self.cells:
            c.obj.destroy()
        self.cells = []

        if len(self.manager.files) > 0:
            if reset_cursor:
                self.cursor = cursor
                self.current_row = current_row
            if self.cursor - self.current_row >= len(self.manager.files):
                self.cursor = 0
                self.current_row = 0

            current_files = (self.manager
                             .files[self.current_row: 
                                    self.current_row + self.max_rows + 1])
            for i, file in enumerate(current_files):
                self.cells.append(Cell(self, self.left_frame, i, file))
                self.cells[-1].draw()

            self.get_current_cell().color = self.highlight_color
            self.get_current_cell().draw()
        
        self.update()

    def update(self, bar=True, info=True):
        if bar:
            self.bar.set_dir(self.manager.current_dir)
        if info and len(self.cells):
            self.infowindow.update(self.get_current_cell())
    
    def update_theme(self):
        self.root.configure(bg=self.main_color)
        self.left_frame.configure(bg=self.main_color)
        self.right_frame.configure(bg=self.main_color)
        self.top_frame.configure(bg=self.main_color)
        self.show_dir(reset_cursor=False)

    def configure_screen(self):
        self.root.title('PyManager')
        self.root.geometry(f'{GUI.WIDTH}x{GUI.HEIGHT}')
        self.root.configure(bg=self.main_color)
        self.root.iconphoto(False, tk.PhotoImage(file="icons/logo.png"))
        self.root.minsize(480, 360)

    def configure_layout(self):
        self.left_frame = tk.Frame(self.root, bg=self.main_color)
        self.right_frame = tk.Frame(self.root, bg=self.main_color, width=20)
        self.top_frame = tk.Frame(self.root, bg=self.main_color,
                                  borderwidth=1, relief=tk.RIDGE)

        self.left_frame.grid(row=1, column=0, sticky='nsew', padx=2)
        self.right_frame.grid(row=1, column=1, sticky='n', padx=5, pady=5)
        self.top_frame.grid(row=0, column=0, columnspan=2, sticky='ew')

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(2, weight=1)
        self.right_frame.grid_columnconfigure(3, weight=1)

        self.top_frame.grid_columnconfigure(3, weight=1)

        self.infowindow = InfoWindow(self.right_frame, self)

        self.bar = Bar(self, self.top_frame)

    def configure_binds(self):
        self.root.bind_all('<Up>', lambda e: self.move_cursor(-1))
        self.root.bind_all('<Down>', lambda e: self.move_cursor(1))
        self.root.bind_all('<Return>', lambda e: self.check_focus(e))
        self.root.bind_all('<Escape>', lambda e: self.check_focus(e))
        self.root.bind_all('<Button-4>', lambda e: self.backward())
        self.root.bind_all('<Button-5>', lambda e: self.forward())
        self.root.bind_all('<MouseWheel>', lambda e: 
                           self.move_cursor(-1 if e.delta > 0 else 1))

        self.left_frame.bind("<Configure>", lambda e: 
                             Thread(target=self.set_max_rows, 
                                    args=(e.height, )).start())
        self.right_frame.bind("<Configure>", lambda e: 
                              Thread(target=self.set_info_width, 
                                     args=(e.x, )).start())

    def run(self):
        self.root.mainloop()
            
    def set_max_rows(self, height):
        current = self.editing_window
        self.editing_window += 1
        time.sleep(0.05)
        if self.editing_window == current + 1:
            old_max_rows = self.max_rows
            new_max_rows = height // 25
            if self.max_rows != new_max_rows:
                reset = self.cursor - self.current_row >= new_max_rows
                self.max_rows = new_max_rows
                if old_max_rows < self.manager.dirlen:
                    self.show_dir(reset_cursor=reset)

    def set_info_width(self, width):
        new_width = 10 + width // 10
        if self.infowindow.title['width'] not in range(new_width - 2, 
                                                       new_width + 2):
            self.infowindow.title.configure(width=new_width)
            self.infowindow.image_size = self.right_frame.winfo_width() // 2
