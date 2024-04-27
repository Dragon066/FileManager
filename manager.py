import os
import shutil
import datetime as dt
import sys


class File():
    def __init__(self, dir):
        self.fulldir = dir
        self.dir = os.path.dirname(self.fulldir)
        self.name = os.path.basename(self.fulldir)
        self.type = 'file' if os.path.isfile(self.fulldir) else 'directory'

        if self.type == 'file':
            self.ext = self.name[self.name.rfind(".") + 1:]
        else:
            self.ext = '←' # because '←' is first in 
                           # char table (need for sorting)
        
        stat = os.stat(self.fulldir)
        self.size = stat.st_size
        self.ctime = dt.datetime.fromtimestamp(stat.st_ctime)
        self.mtime = dt.datetime.fromtimestamp(stat.st_mtime)
        

class Manager():
    def __init__(self, current_dir):
        self.current_dir = current_dir
        self.history = [[self.current_dir, 0, 0]]
        self.history_cursor = 0
        self.sorting_by = 'name'
        self.sorting_ascending = True
        self.update_files(self.current_dir)

    def update_files(self, dir):
        try:
            self.files = [
                File(os.path.join(dir, f))
                for f in os.listdir(dir)
            ]
            self.sort_files()
            self.dirlen = len(self.files)
        except PermissionError as e:
            from tkinter.messagebox import showerror
            showerror('Error', e)

    def sort_files(self):
        self.files.sort(key=lambda x: x.__getattribute__(self.sorting_by), 
                        reverse=not self.sorting_ascending)

    def change_dir(self, dir, current_row=0, cursor=0):
        if os.path.isfile(dir):
            os.startfile(dir)
            return True
        else:
            self.update_history(dir, current_row, cursor)
            self.current_dir = dir
            self.update_files(self.current_dir)
            return False

    def update_history(self, dir, current_row, cursor):
        if dir != self.history[self.history_cursor][0]:
            self.history = self.history[:self.history_cursor + 1]
            self.history[self.history_cursor] = [self.current_dir, 
                                                 current_row, cursor]
            self.history.append([dir, 0, 0])
            self.history_cursor += 1

    def forward(self):
        if self.history_cursor < len(self.history) - 1:
            self.history_cursor += 1
            self.current_dir = self.history[self.history_cursor][0]
            self.update_files(self.current_dir)
            return self.history[self.history_cursor][1:]

    def backward(self):
        if self.history_cursor > 0:
            self.history_cursor -= 1
            self.current_dir = self.history[self.history_cursor][0]
            self.update_files(self.current_dir)
            return self.history[self.history_cursor][1:]
        
    def make_dir(self):
        basename = 'New Directory'
        if os.path.exists(os.path.join(self.current_dir, basename)):
            num = 1
            while os.path.exists(os.path.join(self.current_dir, 
                                              f"{basename} ({num})")):
                num += 1
            basename = f"{basename} ({num})"
        
        os.mkdir(os.path.join(self.current_dir, basename))
        return basename
    
    def make_file(self):
        basename = 'New File'
        if os.path.exists(os.path.join(self.current_dir, basename)):
            num = 1
            while os.path.exists(os.path.join(self.current_dir, 
                                              f"{basename} ({num})")):
                num += 1
            basename = f"{basename} ({num})"
        
        open(os.path.join(self.current_dir, basename), 'a').close()
        return basename

    def delete_file(self, path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    def rename_file(self, file, new_name):
        new_file = os.path.join(file.dir, new_name)
        if not os.path.exists(new_file):
            os.rename(file.fulldir, os.path.join(file.dir, new_name))

    def paste_file(self, src, dst):
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            return src.split(os.path.sep)[-1]
        else:
            shutil.copytree(src, os.path.join(dst, src.split(os.path.sep)[-1]))
            return src.split(os.path.sep)[-1]

    def move_file(self, src, dst):
        if os.path.isfile(src):
            shutil.move(src, os.path.join(dst, src.split(os.path.sep)[-1]))
            return src.split(os.path.sep)[-1]
        else:
            shutil.move(src, os.path.join(dst, src.split(os.path.sep)[-1]), 
                        copy_function=shutil.copytree)
            return src.split(os.path.sep)[-1]
        
    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"
