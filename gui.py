import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path

from src.img_org import organize_images


# =================== GUI ======================
class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📂 이미지 정리 프로그램")
        self.root.geometry("1050x650")
        self.root.configure(bg="#1e1f22")

        self.selected_folder = None
        self.image_list = []
        self.thumbnail_cache = {}

        # ---------- STYLE 적용 ----------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TButton",
            font=("Malgun Gothic", 11),
            padding=6,
            background="#3b82f6",
            foreground="white"
        )
        style.configure("TCheckbutton", background="#1e1f22", foreground="white")
        style.configure("TProgressbar", troughcolor="#2a2b2e", background="#3b82f6")

        # ---------- 상단 ----------
        title = tk.Label(
            root,
            text="📁 이미지 자동/수동 정리 도구",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 22, "bold")
        )
        title.pack(pady=15)

        # ---------- 옵션 + 폴더 선택 ----------
        option_frame = tk.Frame(root, bg="#1e1f22")
        option_frame.pack(fill="x")

        self.btn_select = ttk.Button(
            option_frame,
            text="📁 정리할 폴더 선택",
            command=self.select_folder
        )
        self.btn_select.grid(row=0, column=0, padx=20, pady=10)

        # 옵션 체크박스
        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        ttk.Checkbutton(option_frame, text="정확한 중복 정리", variable=self.opt_dup).grid(row=0, column=1)
        ttk.Checkbutton(option_frame, text="유사 이미지 정리", variable=self.opt_sim).grid(row=0, column=2)
        ttk.Checkbutton(option_frame, text="해상도 정리 (범위별)", variable=self.opt_res).grid(row=0, column=3)

        ttk.Checkbutton(
            option_frame,
            text="자동 정리 (모든 옵션 적용)",
            variable=self.opt_auto,
            command=self.apply_auto
        ).grid(row=0, column=4)

        # ---------- 중간 영역 ----------
        body = tk.Frame(root, bg="#1e1f22")
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # 좌측 리스트
        left_frame = tk.Frame(body, bg="#2a2b2e", width=300)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="📃 이미지 목록", bg="#2a2b2e", fg="white",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(left_frame, bg="#1e1f22", fg="white",
                                  selectbackground="#3b82f6", font=("Malgun Gothic", 10))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)

        # 이미지 미리보기
        right_frame = tk.Frame(body, bg="#2a2b2e")
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="🖼 이미지 미리보기", fg="white", bg="#2a2b2e",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.canvas = tk.Canvas(right_frame, bg="#1e1f22")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------- 진행바 + 실행 버튼 ----------
        bottom = tk.Frame(root, bg="#1e1f22")
        bottom.pack(fill="x")

        self.progress = ttk.Progressbar(bottom, length=500, mode="determinate")
        self.progress.pack(pady=10)

        self.btn_run = ttk.Button(bottom, text="🚀 정리 실행", command=self.run_organize)
        self.btn_run.pack(pady=5)

    # =========================================================
    # 옵션 - 자동 정리
    def apply_auto(self):
        if self.opt_auto.get():
            self.opt_dup.set(True)
            self.opt_sim.set(True)
            self.opt_res.set(True)

    # =========================================================
    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.selected_folder = Path(folder)
        self.load_images()

    # =========================================================
    def load_images(self):
        exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        self.image_list.clear()
        self.listbox.delete(0, tk.END)

        for p in self.selected_folder.rglob("*"):
            if p.suffix.lower() in exts:
                self.image_list.append(p)
                self.listbox.insert(tk.END, p.name)

    # =========================================================
    def show_preview(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        img_path = self.image_list[index]

        try:
            img = Image.open(img_path)
            img.thumbnail((700, 700))
            img = ImageTk.PhotoImage(img)
        except:
            return

        self.canvas.delete("all")
        self.canvas.create_image(350, 350, image=img)
        self.canvas.image = img

    # =========================================================
    def run_organize(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        # 옵션 읽기
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

        # 진행률
        total = len(self.image_list)
        self.progress["value"] = 0
        self.progress["maximum"] = total
        for _ in range(total):
            self.progress["value"] += 1
            self.root.update()

        messagebox.showinfo("완료", "이미지 정리가 완료되었습니다!")
