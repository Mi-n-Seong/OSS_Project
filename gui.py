import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import subprocess


class App:
    def __init__(self, root):
        self.root = root
        root.title("이미지 정리 프로그램")

        self.path_var = tk.StringVar()

        tk.Button(root, text="폴더 선택", command=self.select_folder).pack()
        tk.Label(root, textvariable=self.path_var).pack()

        tk.Button(root, text="전체 자동 정리 (--auto)",
                  command=self.auto).pack()

        self.log = tk.Text(root, height=15, width=50)
        self.log.pack()

    def log_print(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def select_folder(self):
        folder = filedialog.askdirectory()
        self.path_var.set(folder)

    def auto(self):
        folder = self.path_var.get()
        if not folder:
            self.log_print("폴더를 선택하세요.")
            return

        cmd = f'python main.py "{folder}" --auto'

        self.log_print(f"실행: {cmd}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.log_print(result.stdout)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
