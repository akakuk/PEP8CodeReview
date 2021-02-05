import code_parser as cp
import file_manager as fm
import threading
import multiprocessing
import concurrent.futures as cf
import tkinter as tk
from tkinter import filedialog


class PEP8_CodeChecker:


    def __init__(self):
        self.n_core_max = multiprocessing.cpu_count()
        self.n_core_cur = self.n_core_max
        self.initial_dir = "./"
        self.window = tk.Tk()
        self.create_maps = tk.BooleanVar()
        self.window.geometry("640x480")
        self.window.resizable(False, False)
        self.window.title("PEP8 Code Check")
        self.lbl_cores = tk.Label(self.window, text="Number of Cores:")
        self.lbl_cores.place(x=400, y=102)
        self.cbx_create_maps = tk.Checkbutton(self.window, text="Create Maps", variable=self.create_maps)
        print(self.create_maps)
        self.cbx_create_maps.place(x=80, y= 120)
        self.btn_select_dir = tk.Button(self.window, text="Select", command=self.select_dir)
        self.btn_select_dir.configure(height=1, width=12)
        self.btn_select_dir.place(x=450, y=47)
        self.btn_add_core = tk.Button(self.window, text="+", command=self.add_core)
        self.btn_add_core.configure(height=1, width=6)
        self.btn_add_core.place(x=550, y=90)
        self.btn_remove_core = tk.Button(self.window, text="-", command=self.remove_core)
        self.btn_remove_core.configure(height=1, width=6)
        self.btn_remove_core.place(x=550, y=115)
        self.btn_start = tk.Button(self.window, text="Start", command=self.start_parsing)
        self.btn_start.place(x=210, y=320)
        self.btn_start.configure(height=5, width=30)
        self.entry_core = tk.Entry(self.window, state="normal")
        self.entry_core.insert(24, str(self.n_core_cur))
        self.entry_core.configure(width=3)
        self.entry_core.place(x=515, y=103)
        self.entry_path = tk.Entry(self.window)
        self.entry_path.insert(12, "Select path")
        self.entry_path.place(x=75, y=50)
        self.entry_path.configure(width=60)
        self.window.mainloop()

    def select_dir(self):
        self.path = tk.filedialog.askdirectory(initialdir=self.initial_dir, title="Select")
        self.initial_dir = self.path
        self.entry_path.delete(0, "end")
        self.entry_path.insert(12, self.path)
        print(self.path)
        self.get_filelist()
        print(self.filelist)

    def add_core(self):
        if(self.n_core_cur < self.n_core_max):
            self.n_core_cur += 1
            self.entry_core.delete(0, "end")
            self.entry_core.insert(24, str(self.n_core_cur))

    def remove_core(self):
        if(self.n_core_cur > 0):
            self.n_core_cur -= 1
            self.entry_core.delete(0, "end")
            self.entry_core.insert(24, str(self.n_core_cur))

    def start_parsing(self):
        self.btn_add_core.configure(state="disabled")
        self.btn_remove_core.configure(state="disabled")
        with cf.ThreadPoolExecutor(self.n_core_cur) as executor:
            futures = []
            for f in self.filelist:
                futures.append(executor.submit(cp.CodeParser(f,create_maps=self.create_maps.get()).parse_all))
            for future in cf.as_completed(futures):
                pass
        self.btn_add_core.configure(state="normal")
        self.btn_remove_core.configure(state="normal")

    def get_filelist(self):
        with cf.ThreadPoolExecutor(self.n_core_cur) as executor:
            future = executor.submit(fm.get_paths, self.path)
            self.filelist = future.result()
            print(self.filelist)

if __name__ == "__main__":
    PEP8_CodeChecker()
