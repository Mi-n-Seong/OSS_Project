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
        self.preview_image = None  # 미리보기 이미지 참조 유지

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
            opt_frame,
            text="📁 폴더 선택",
            command=self.select_folder
        )
        self.btn_folder.grid(row=0, column=0, padx=15)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        ttk.Checkbutton(
            opt_frame,
            text="중복 이미지 삭제",
            variable=self.opt_dup
        ).grid(row=0, column=1)

        ttk.Checkbutton(
            opt_frame,
            text="유사 이미지 묶음",
            variable=self.opt_sim
        ).grid(row=0, column=2)

        ttk.Checkbutton(
            opt_frame,
            text="해상도 별 분류",
            variable=self.opt_res
        ).grid(row=0, column=3)

        ttk.Checkbutton(
            opt_frame,
            text="전체 선택",
            variable=self.opt_auto,
            command=self.apply_auto
        ).grid(row=0, column=4)

        self.btn_run = ttk.Button(
            opt_frame,
            text="🚀 정리 실행",
            command=self.run_organize
        )
        self.btn_run.grid(row=0, column=5, padx=15)

        # ---------- 메인 레이아웃 ----------
        main_frame = tk.Frame(root, bg="#1e1f22")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 좌측 이미지 리스트
        left = tk.Frame(main_frame, bg="#1e1f22", width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left,
            text="📃 이미지 목록",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 12, "bold")
        ).pack(pady=5)

        self.listbox = tk.Listbox(
            left,
            bg="#2a2b2e",
            fg="white",
            selectbackground="#3b82f6",
            font=("Malgun Gothic", 10)
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)

        # 우측: 미리보기 + 로그
        right = tk.Frame(main_frame, bg="#1e1f22")
        right.pack(side="right", fill="both", expand=True)

        # 미리보기 영역
        preview_frame = tk.Frame(right, bg="#1e1f22", height=320)
        preview_frame.pack(fill="x")
        preview_frame.pack_propagate(False)

        tk.Label(
            preview_frame,
            text="🖼 이미지 미리보기",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 12, "bold")
        ).pack(pady=5)

        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg="#2a2b2e",
            height=280
        )
        self.preview_canvas.pack(fill="x", padx=10, pady=5)

        # 로그 영역
        log_frame = tk.Frame(right, bg="#1e1f22")
        log_frame.pack(fill="both", expand=True)

        tk.Label(
            log_frame,
            text="📄 로그 출력",
            fg="white",
            bg="#1e1f22",
            font=("Malgun Gothic", 12, "bold")
        ).pack(pady=5)

        self.log_box = tk.Text(
            log_frame,
            bg="#2a2b2e",
            fg="white",
            font=("Malgun Gothic", 10),
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------- 자동 정리 체크 --------------------
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
    def show_preview(self, event=None):
        if not self.listbox.curselection():
            return

        idx = self.listbox.curselection()[0]
        img_path = self.image_list[idx]

        try:
            img = Image.open(img_path)
            img.thumbnail((500, 260))
            self.preview_image = ImageTk.PhotoImage(img)
        except Exception:
            return

        self.preview_canvas.delete("all")
        canvas_w = int(self.preview_canvas.winfo_width() or 500)
        canvas_h = int(self.preview_canvas.winfo_height() or 260)

        self.preview_canvas.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=self.preview_image
        )

    # -------------------- 정리 실행 버튼 --------------------
    def run_organize(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        # 정확한 중복 시 삭제 팝업
        if self.opt_dup.get():
            if messagebox.askyesno(
                "경고",
                "중복 이미지가 발견되면\n대표 1개를 제외한 나머지는 삭제됩니다.\n계속할까요?"
            ) is False:
                return

        self.btn_run.config(state="disabled")

        # 로그 초기화
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert(tk.END, "[INFO] 정리 작업을 시작합니다...\n")
        self.log_box.configure(state="disabled")

        thread = threading.Thread(target=self._worker)
        thread.daemon = True
        thread.start()

    # -------------------- 백그라운드 작업 --------------------
    def _worker(self):
        summary, logs = organize_images(
            self.selected_folder,
            move_duplicates=self.opt_dup.get(),
            move_similar=self.opt_sim.get(),
            sort_resolution=self.opt_res.get(),
            auto=self.opt_auto.get(),
            delete_duplicates=self.opt_dup.get()   # ★ 정확한 중복 체크 → 자동 삭제
        )

        self.root.after(0, lambda: self._update_log(summary, logs))

    # -------------------- 결과 로그 업데이트 --------------------
    def _update_log(self, summary, logs):
        self.btn_run.config(state="normal")

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)

        self.log_box.insert(tk.END, "===== 요약 =====\n")
        if summary:
            for k, v in summary.items():
                self.log_box.insert(tk.END, f"{k}: {v}\n")
        else:
            self.log_box.insert(tk.END, "실행된 작업 없음\n")

        self.log_box.insert(tk.END, "\n===== 상세 로그 =====\n")
        if logs:
            for line in logs:
                self.log_box.insert(tk.END, line + "\n")
        else:
            self.log_box.insert(tk.END, "(상세 로그 없음)\n")

        self.log_box.configure(state="disabled")

        messagebox.showinfo("완료", "정리가 완료되었습니다!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
