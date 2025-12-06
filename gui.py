import tkinter as tk
from tkinter import filedialog
import subprocess
from pathlib import Path


# ---------------------------------------
# 프로젝트 루트 경로 (gui.py 기준 상위 폴더)
# ---------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# main.py 절대경로
MAIN_FILE = PROJECT_ROOT / "main.py"


class App:
    def __init__(self, root):
        self.root = root
        root.title("📁 이미지 정리 프로그램")
        root.geometry("900x600")
        root.minsize(900, 600)

        # === 다크모드 스타일 설정 ===
        bg = "#1e1e1e"
        fg = "#e5e5e5"
        btn_bg = "#3a3a3a"
        btn_fg = "#ffffff"
        entry_bg = "#2b2b2b"

        root.configure(bg=bg)

        # ===== 제목 =====
        title = tk.Label(
            root,
            text="이미지 정리 프로그램",
            font=("Segoe UI", 20, "bold"),
            fg=fg, bg=bg
        )
        title.pack(pady=10)

        # ===== 폴더 선택 =====
        frame = tk.Frame(root, bg=bg)
        frame.pack(pady=10)

        self.path_var = tk.StringVar()

        tk.Button(
            frame,
            text="폴더 선택",
            command=self.select_folder,
            bg=btn_bg, fg=btn_fg,
            font=("Segoe UI", 11),
            width=12, relief="flat"
        ).grid(row=0, column=0, padx=5)

        self.path_entry = tk.Entry(
            frame,
            textvariable=self.path_var,
            width=50,
            bg=entry_bg,
            fg=fg,
            relief="flat",
            font=("Segoe UI", 10)
        )
        self.path_entry.grid(row=0, column=1, padx=5)

        # ===== 자동 정리 버튼 =====
        btn_frame = tk.Frame(root, bg=bg)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="이미지 자동 정리",
            command=self.auto,
            bg="#5c6bc0",
            fg="white",
            width=30,
            height=2,
            font=("Segoe UI", 12, "bold"),
            relief="flat"
        ).pack(pady=5)

        # ===== 로그 박스 =====
        self.log = tk.Text(
            root,
            bg=entry_bg,
            fg=fg,
            relief="flat",
            font=("Consolas", 11)
        )
        self.log.pack(expand=True, fill="both", padx=10, pady=10)

        # 디버그용: main.py 경로 출력
        self.log_print(f"[DEBUG] PROJECT_ROOT = {PROJECT_ROOT}")
        self.log_print(f"[DEBUG] MAIN_FILE = {MAIN_FILE}")

    # ---------------------------------------
    # 로그 출력
    # ---------------------------------------
    def log_print(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    # ---------------------------------------
    # 폴더 선택 기능
    # ---------------------------------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        self.path_var.set(folder)
        self.log_print(f"[INFO] 선택한 폴더: {folder}")

    # ---------------------------------------
    # 자동 정리 실행
    # ---------------------------------------
    def auto(self):
        folder = self.path_var.get()

        if not folder:
            self.log_print("[ERROR] 폴더를 선택하세요.")
            return

        cmd = ["python", str(MAIN_FILE), folder, "--auto"]

        self.log_print(f"[CMD] {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            cwd=PROJECT_ROOT    # main.py가 있는 폴더에서 실행
        )

        if result.stdout:
            self.log_print(result.stdout)
        if result.stderr:
            self.log_print("[ERROR] " + result.stderr)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
