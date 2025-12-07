import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from PIL import Image, ImageTk

from src.img_organizer import organize_images


class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📂 이미지 정리 프로그램")
        self.root.geometry("1100x700")
        self.root.configure(bg="#1e1f22")

        self.selected_folder: Path | None = None
        self.image_list: list[Path] = []
        self.preview_image = None

        # ---------- STYLE ----------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        padding=6, background="#3b82f6",
                        foreground="white", font=("Malgun Gothic", 11))

        style.configure("TCheckbutton",
                        background="#1e1f22", foreground="white",
                        font=("Malgun Gothic", 11))

        style.map("TButton",
                  background=[("active", "#444444")],
                  foreground=[("active", "white")])

        # ---------- UI ----------
        title = tk.Label(
            root, text="📁 이미지 정리 도구",
            fg="white", bg="#1e1f22",
            font=("Malgun Gothic", 22, "bold")
        )
        title.pack(pady=15)

        opt_frame = tk.Frame(root, bg="#1e1f22")
        opt_frame.pack(fill="x")

        self.btn_folder = ttk.Button(
            opt_frame, text="📁 폴더 선택",
            command=self.select_folder
        )
        self.btn_folder.grid(row=0, column=0, padx=15)

        # 옵션들
        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()
        self.opt_delete = tk.BooleanVar()  # 🔥 삭제 옵션 추가

        ttk.Checkbutton(opt_frame, text="정확한 중복", variable=self.opt_dup).grid(row=0, column=1)
        ttk.Checkbutton(opt_frame, text="유사 이미지", variable=self.opt_sim).grid(row=0, column=2)
        ttk.Checkbutton(opt_frame, text="해상도 정리", variable=self.opt_res).grid(row=0, column=3)
        ttk.Checkbutton(opt_frame, text="자동정리", variable=self.opt_auto,
                        command=self.apply_auto).grid(row=0, column=4)

        ttk.Checkbutton(opt_frame, text="중복 삭제(휴지통)", variable=self.opt_delete,
                        ).grid(row=1, column=1, pady=5)

        self.btn_run = ttk.Button(
            opt_frame, text="🚀 정리 실행",
            command=self.run_organize
        )
        self.btn_run.grid(row=0, column=5, padx=15)

        # 좌측 리스트 + 우측 미리보기/로그
        main_frame = tk.Frame(root, bg="#1e1f22")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 좌측 리스트
        left = tk.Frame(main_frame, bg="#1e1f22", width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="📃 이미지 목록", fg="white", bg="#1e1f22",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(
            left, bg="#2a2b2e", fg="white",
            selectbackground="#3b82f6", font=("Malgun Gothic", 10)
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)

        # 우측
        right = tk.Frame(main_frame, bg="#1e1f22")
        right.pack(side="right", fill="both", expand=True)

        preview_frame = tk.Frame(right, bg="#1e1f22", height=320)
        preview_frame.pack(fill="x")
        preview_frame.pack_propagate(False)

        tk.Label(preview_frame, text="🖼 이미지 미리보기",
                 fg="white", bg="#1e1f22",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.preview_canvas = tk.Canvas(
            preview_frame, bg="#2a2b2e", height=280
        )
        self.preview_canvas.pack(fill="x", padx=10, pady=5)

        # 로그 영역
        log_frame = tk.Frame(right, bg="#1e1f22")
        log_frame.pack(fill="both", expand=True)

        tk.Label(log_frame, text="📄 로그 출력",
                 fg="white", bg="#1e1f22",
                 font=("Malgun Gothic", 12, "bold")).pack(pady=5)

        self.log_box = tk.Text(
            log_frame, bg="#2a2b2e",
            fg="white", font=("Malgun Gothic", 10),
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------- 자동정리 --------------------
    def apply_auto(self):
        if self.opt_auto.get():
            self.opt_dup.set(True)
            self.opt_sim.set(True)
            self.opt_res.set(True)

    # -------------------- 폴더 선택 --------------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
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

    # -------------------- 미리보기 --------------------
    def show_preview(self, event=None):
        if not self.listbox.curselection():
            return

        idx = self.listbox.curselection()[0]
        img_path = self.image_list[idx]

        try:
            img = Image.open(img_path)
            img.thumbnail((500, 260))
            self.preview_image = ImageTk.PhotoImage(img)
        except:
            return

        self.preview_canvas.delete("all")
        w = int(self.preview_canvas.winfo_width() or 500)
        h = int(self.preview_canvas.winfo_height() or 260)

        self.preview_canvas.create_image(
            w // 2, h // 2, image=self.preview_image
        )

    # -------------------- 정리 실행 --------------------
    def run_organize(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        # 삭제 선택 시 확인 팝업
        if self.opt_delete.get():
            check = messagebox.askyesno(
                "경고",
                "정확한 중복 이미지가 모두 휴지통으로 삭제됩니다.\n계속하시겠습니까?"
            )
            if not check:
                return

        self.btn_run.config(state="disabled")

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert(tk.END, "[INFO] 정리 작업을 시작합니다...\n")
        self.log_box.configure(state="disabled")

        thread = threading.Thread(target=self._worker)
        thread.daemon = True
        thread.start()

    # -------------------- 작업 스레드 --------------------
    def _worker(self):
        dup = self.opt_dup.get()
        sim = self.opt_sim.get()
        res = self.opt_res.get()
        auto = self.opt_auto.get()
        delete = self.opt_delete.get()

        summary, logs = organize_images(
            self.selected_folder,
            move_duplicates=dup,
            move_similar=sim,
            sort_resolution=res,
            auto=auto,
            copy_mode=True,
            delete_duplicates=delete,
        )

        self.root.after(0, lambda: self._update_log(summary, logs))

    # -------------------- 로그 업데이트 --------------------
    def _update_log(self, summary, logs):
        self.btn_run.config(state="normal")

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)

        self.log_box.insert(tk.END, "===== 요약 =====\n")
        for k, v in summary.items():
            self.log_box.insert(tk.END, f"{k}: {v}\n")

        self.log_box.insert(tk.END, "\n===== 상세 로그 =====\n")
        for line in logs:
            self.log_box.insert(tk.END, line + "\n")

        self.log_box.configure(state="disabled")

        messagebox.showinfo("완료", "정리가 완료되었습니다!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
