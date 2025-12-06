import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from src.img_organizer import organize_images


class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📂 이미지 정리 프로그램")
        self.root.geometry("1050x650")
        self.root.configure(bg="#1e1f22")

        self.selected_folder = None
        self.image_list = []
        self.thumbnail_cache = {}

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
            text="📁 이미지 정리 도구",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 22, "bold")
        )
        title.pack(pady=15)

        # ---------- 상단 옵션 ----------
        opt_frame = tk.Frame(root, bg="#1e1f22")
        opt_frame.pack(fill="x")

        self.btn_folder = ttk.Button(
            opt_frame, text="📁 폴더 선택", command=self.select_folder
        )
        self.btn_folder.grid(row=0, column=0, padx=15)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        ttk.Checkbutton(opt_frame, text="정확한 중복", variable=self.opt_dup).grid(row=0, column=1)
        ttk.Checkbutton(opt_frame, text="유사 이미지", variable=self.opt_sim).grid(row=0, column=2)
        ttk.Checkbutton(opt_frame, text="해상도 정리", variable=self.opt_res).grid(row=0, column=3)

        ttk.Checkbutton(
            opt_frame, text="자동정리", variable=self.opt_auto, command=self.apply_auto
        ).grid(row=0, column=4)

        self.btn_run = ttk.Button(
            opt_frame,
            text="🚀 정리 실행",
            command=self.run_organize
        )
        self.btn_run.grid(row=0, column=5, padx=15)

        # ---------- 탭 생성 ----------
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # =============== [ TAB 1 ] 이미지 목록 ===============
        tab_images = tk.Frame(notebook, bg="#1e1f22")
        notebook.add(tab_images, text="🖼 이미지 목록")

        # 좌측 리스트
        left = tk.Frame(tab_images, bg="#1e1f22", width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left, text="이미지 목록", fg="white", bg="#1e1f22",
            font=("Malgun Gothic", 12, "bold")
        ).pack(pady=5)

        self.listbox = tk.Listbox(
            left, bg="#2a2b2e", fg="white",
            selectbackground="#3b82f6",
            font=("Malgun Gothic", 10)
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)

        # 우측 미리보기
        right = tk.Frame(tab_images, bg="#1e1f22")
        right.pack(side="right", fill="both", expand=True)

        tk.Label(
            right, text="이미지 미리보기", fg="white", bg="#1e1f22",
            font=("Malgun Gothic", 12, "bold")
        ).pack(pady=5)

        self.canvas = tk.Canvas(right, bg="#2a2b2e")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # =============== [ TAB 2 ] 로그 탭 ===============
        tab_log = tk.Frame(notebook, bg="#1e1f22")
        notebook.add(tab_log, text="📄 로그")

        self.log_box = tk.Text(
            tab_log,
            bg="#2a2b2e",
            fg="white",
            font=("Malgun Gothic", 10),
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------- 옵션 자동 적용 --------------------
    def apply_auto(self):
        if self.opt_auto.get():
            self.opt_dup.set(True)
            self.opt_sim.set(True)
            self.opt_res.set(True)

    # -------------------- 폴더 선택 --------------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.selected_folder = Path(folder)
        self.load_images()

    # -------------------- 이미지 로딩 --------------------
    def load_images(self):
        self.image_list.clear()
        self.listbox.delete(0, tk.END)

        exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

        for p in self.selected_folder.rglob("*"):
            if p.suffix.lower() in exts:
                self.image_list.append(p)
                self.listbox.insert(tk.END, p.name)

    # -------------------- 이미지 미리보기 --------------------
    def show_preview(self, event):
        if not self.listbox.curselection():
            return

        idx = self.listbox.curselection()[0]
        img_path = self.image_list[idx]

        try:
            img = Image.open(img_path)
            img.thumbnail((800, 800))
            preview = ImageTk.PhotoImage(img)
        except:
            return

        self.canvas.delete("all")
        self.canvas.create_image(420, 300, image=preview)
        self.canvas.image = preview

    # -------------------- 정리 실행 --------------------
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

        # 로그 출력
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        for line in logs:
            self.log_box.insert(tk.END, line + "\n")
        self.log_box.configure(state="disabled")

        messagebox.showinfo("완료", "정리가 완료되었습니다!")


# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
