import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from src.img_organizer import organize_images


class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        root.title("🖼 이미지 정리 프로그램")
        root.geometry("720x520")
        root.configure(bg="#f2f2f2")

        self.root.option_add("*Font", "맑은 고딕 10")

        # =================== 상단 제목 ===================
        top_frame = tk.Frame(root, bg="#f2f2f2")
        top_frame.pack(fill="x", pady=10)

        self.lbl_title = tk.Label(
            top_frame,
            text="이미지 정리 프로그램",
            font=("맑은 고딕", 16, "bold"),
            bg="#f2f2f2"
        )
        self.lbl_title.pack()

        # =================== 폴더 선택 ===================
        path_frame = tk.Frame(root, bg="#f2f2f2")
        path_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(path_frame, text="📁 정리할 폴더:", bg="#f2f2f2").pack(side="left")

        self.path_var = tk.StringVar()
        self.entry_path = tk.Entry(path_frame, textvariable=self.path_var, width=50)
        self.entry_path.pack(side="left", padx=10)

        ttk.Button(path_frame, text="찾기", command=self.select_folder).pack(side="left")

        # =================== 옵션 체크 ===================
        option_frame = tk.LabelFrame(root, text="정리 옵션", padx=15, pady=10)
        option_frame.pack(fill="x", padx=20, pady=10)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()
        self.opt_auto = tk.BooleanVar()

        ttk.Checkbutton(option_frame, text="정확한 중복 정리", variable=self.opt_dup).pack(anchor="w")
        ttk.Checkbutton(option_frame, text="유사 이미지 정리", variable=self.opt_sim).pack(anchor="w")
        ttk.Checkbutton(option_frame, text="해상도별 정리 (범위)", variable=self.opt_res).pack(anchor="w")
        ttk.Checkbutton(option_frame, text="전체 자동 정리 (--auto)", variable=self.opt_auto).pack(anchor="w")

        # =================== 실행 버튼 ===================
        btn_frame = tk.Frame(root, bg="#f2f2f2")
        btn_frame.pack(pady=10)

        self.btn_run = tk.Button(
            btn_frame,
            text="정리 실행",
            width=15,
            height=2,
            bg="#4a72ff",
            fg="white",
            font=("맑은 고딕", 12, "bold"),
            command=self.run,
            relief="flat",
            activebackground="#3f63e0",
        )
        self.btn_run.pack()

        # =================== 로그 출력 ===================
        log_frame = tk.LabelFrame(root, text="정리 로그", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.txt_log = tk.Text(
            log_frame,
            height=15,
            state="disabled",
            bg="#ffffff"
        )
        self.txt_log.pack(fill="both", expand=True)

    # ------------------------ 기능 ------------------------

    def log(self, text):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", text + "\n")
        self.txt_log.configure(state="disabled")
        self.txt_log.see("end")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def run(self):
        folder = self.path_var.get().strip()
        if not folder:
            messagebox.showerror("오류", "폴더를 선택하세요.")
            return

        root_path = Path(folder)

        # 로그 초기화
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

        self.log(f"[INFO] 선택한 폴더: {root_path}")

        try:
            summary, logs = organize_images(
                root_path,
                move_duplicates=self.opt_dup.get(),
                move_similar=self.opt_sim.get(),
                sort_resolution=self.opt_res.get(),
                sort_ext=False,
                sort_date=False,
                auto=self.opt_auto.get(),
            )

            self.log("\n===== 실행 결과 =====")
            for k, v in summary.items():
                self.log(f"{k}: {v}")

            self.log("\n===== 상세 로그 =====")
            for line in logs:
                self.log(line)

            messagebox.showinfo("완료", "이미지 정리가 완료되었습니다.")

        except Exception as e:
            self.log(f"[ERROR] {e}")
            messagebox.showerror("오류 발생", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
