import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from src.img_org import organize_images


# =================== GUI ======================
class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📂 이미지 정리 프로그램")
        self.root.geometry("850x600")
        self.root.configure(bg="#1e1f22")

        self.selected_folder = None
        self.image_list = []

        # ---------- STYLE ----------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TButton",
            padding=6,
            background="#3b82f6",
            foreground="white",
            font=("Malgun Gothic", 11)
        )
        style.configure(
            "TCheckbutton",
            background="#1e1f22",
            foreground="white",
            font=("Malgun Gothic", 11)
        )
        style.configure("TProgressbar",
                        troughcolor="#2a2b2e",
                        background="#3b82f6")

        # hover 색 어둡게 고정 (밝게 변하는 문제 해결)
        style.map(
            "TButton",
            background=[("active", "#444444")],
            foreground=[("active", "white")]
        )
        style.map(
            "TCheckbutton",
            background=[("active", "#444444")],
            foreground=[("active", "white")]
        )

        # ---------- 제목 ----------
        title = tk.Label(
            root,
            text="📁 이미지 자동/수동 정리 도구",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 22, "bold")
        )
        title.pack(pady=15)

        # ---------- 폴더 선택 + 옵션 ----------
        option_frame = tk.Frame(root, bg="#1e1f22")
        option_frame.pack(fill="x")

        self.btn_select = ttk.Button(
            option_frame,
            text="📁 정리할 폴더 선택",
            command=self.select_folder
        )
        self.btn_select.grid(row=0, column=0, padx=20, pady=10)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        ttk.Checkbutton(option_frame, text="정확한 중복 정리", variable=self.opt_dup).grid(row=0, column=1, padx=10)
        ttk.Checkbutton(option_frame, text="유사 이미지 정리", variable=self.opt_sim).grid(row=0, column=2, padx=10)
        ttk.Checkbutton(option_frame, text="해상도 범위 정리", variable=self.opt_res).grid(row=0, column=3, padx=10)

        ttk.Checkbutton(
            option_frame,
            text="자동 정리",
            variable=self.opt_auto,
            command=self.apply_auto
        ).grid(row=0, column=4, padx=10)

        # ---------- 중앙 리스트 ----------
        center_frame = tk.Frame(root, bg="#1e1f22")
        center_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(center_frame, text="📃 이미지 목록", bg="#1e1f22", fg="white",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(
            center_frame,
            bg="#2a2b2e",
            fg="white",
            selectbackground="#3b82f6",
            font=("Malgun Gothic", 10)
        )
        self.listbox.pack(fill="both", expand=True)

        # ---------- 진행바 + 실행버튼 ----------
        bottom = tk.Frame(root, bg="#1e1f22")
        bottom.pack(fill="x")

        self.progress = ttk.Progressbar(bottom, length=500, mode="determinate")
        self.progress.pack(pady=10)

        self.btn_run = ttk.Button(bottom, text="🚀 정리 실행", command=self.run_organize)
        self.btn_run.pack(pady=5)

    # 옵션 - 자동 정리 선택 시 체크 자동 ON
    def apply_auto(self):
        if self.opt_auto.get():
            self.opt_dup.set(True)
            self.opt_sim.set(True)
            self.opt_res.set(True)

    # 폴더 선택
    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.selected_folder = Path(folder)
        self.load_images()

    # 이미지 리스트 로드
    def load_images(self):
        exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        self.image_list.clear()
        self.listbox.delete(0, tk.END)

        for p in self.selected_folder.rglob("*"):
            if p.suffix.lower() in exts:
                self.image_list.append(p)
                self.listbox.insert(tk.END, p.name)

    # 정리 실행
    def run_organize(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        dup = self.opt_dup.get()
        sim = self.opt_sim.get()
        res = self.opt_res.get()
        auto = self.opt_auto.get()

        summary, logs = organize_images(
            self.selected_folder,
            move_duplicates=dup,
            move_similar=sim,
            sort_resolution=res,
            auto=auto,
            copy_mode=True
        )

        # 진행바 애니메이션
        total = len(self.image_list)
        self.progress["maximum"] = total
        self.progress["value"] = 0

        for _ in range(total):
            self.progress["value"] += 1
            self.root.update()

        messagebox.showinfo("완료", "이미지 정리가 완료되었습니다!")


# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
