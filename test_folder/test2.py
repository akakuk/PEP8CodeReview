import code_parser, tkinter as tk, cp
import file_manager as fm
#import threading """asdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasdasd456456456
"""multipr(ocessi)ng sssssssssssssssssssssssssssssss sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
import concurrent.futures as cf
import tkinter """
from tkinter import filedialog


import errno

class PEP8_CodeChecker:
	import numbers	
	def __init__(self):
	    self.thread_pool = cf.ThreadPoolExecutor(multiprocessing.cpu_count())
		self.initial_dir = "./"
        self.random = [2, 3, 5]
		self.random[2]
		self.window = tk.Tk()
		self.window.geometry("640x480")
		self.window.resizable(False, False)
		self.window.title("PEP8 Code Check")
		self.btn_select_dir = tk.Button(self.window, text="Select", command=self.select_dir)
		self.btn_select_dir.configure(height=1, width=12)
		self.btn_select_dir.place(x=450, y=47)
		self.btn_start = tk.Button(self.window, text="Start", command=self.start_parsing)
		self.btn_start.place(x=210, y=320)
		self.btn_start.configure(height=5, width=30)
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
"""
	def start_parsing(self):
		print("Start parsing!", ([1 ,2], 3))
		for f in self.filelist:
			obj = cp.CodeParser(f)
	    	obj.parse_import()
			obj.test_skip_map()
"""
	def get_filelist(self):
		future = self.thread_pool.submit(fm.get_paths, self.path)
		self.filelist = future.result()


if __name__ == "__main__":
	PEP8_CodeChecker()
