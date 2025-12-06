import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

from src.img_organizer import organize_images  # 정리 함수 import


# =========================
#   스타일 설정 함수
# =========================
def apply_style(widget):
    widget.configure(
        bg="#1e1f22",
        fg="#ffffff",
        font=("Malgun Gothic", 11),
        bd=0,
    )


def styled_button(master, text, command):
    btn = tk.Button(
        master,
        text=text,
        command=command,
        bg="#3a3b3e",
        fg="#ffffff",
        font=("Malgun Gothic", 11, "bold"),
        activebackground="#505154",
        activeforeground="#ffffff",
        relief="flat",
        padx=12,
        pady=6,
    )
    return btn


# =========================
#        메인 GUI 클래스
# =========================
class ImageOrganizerGUI:
    def __init__(self, root):
        self.root = root
        root.title("이미지 정리 프로그램")
        root.geometry("750x650")
        root.configure(bg="#1e1f22")

        # ===== 상단 타이틀 =====
        self.title_label = tk.Label(
            root,
            text="📂 이미지 자동 정리 도구",
            bg="#1e1f22",
            fg="#ffffff",
            font=("Malgun Gothic", 18, "bold"),
        )
        self.title_label.pack(pady=15)

        # ===== 폴더 선택 영역 =====
        folder_frame = tk.Frame(root, bg="#1e1f22")
        folder_frame.pack(pady=10)

        self.lbl_folder = tk.Label(
            folder_frame,
            text="📁 선택한 폴더: 없음",
            bg="#1e1f22",
            fg="#cccccc",
            font=("Malgun Gothic", 11),
        )
        self.lbl_folder.pack(side="left", padx=10)

        btn_select = styled_button(folder_frame, "폴더 선택", self.select_folder)
        btn_select.pack(side="left", padx=10)

        # ===== 옵션 영역 (카드 스타일) =====
        option_frame = tk.LabelFrame(
            root,
            text="정리 옵션 선택",
            bg="#2a2b2e",
            fg="#ffffff",
            font=("Malgun Gothic", 13, "bold"),
            padx=10,
            pady=10,
        )
        option_frame.pack(fill="x", padx=20, pady=10)

        self.opt_dup = tk.BooleanVar()
        self.opt_sim = tk.BooleanVar()
        self.opt_res = tk.BooleanVar()

        self.chk1 = tk.Checkbutton(
            option_frame, text="정확한 중복 정리", variable=self.opt_dup,
            bg="#2a2b2e", fg="#ffffff", selectcolor="#2a2b2e",
            font=("Malgun Gothic", 11)
        )
        self.chk1.pack(anchor="w")

        self.chk2 = tk.Checkbutton(
            option_frame, text="유사 이미지 정리", variable=self.opt_sim,
            bg="#2a2b2e", fg="#ffffff", selectcolor="#2a2b2e",
            font=("Malgun Gothic", 11)
        )
        self.chk2.pack(anchor="w")

        self.chk3 = tk.Checkbutton(
            option_frame, text="해상도 범위 정리", variable=self.opt_res,
            bg="#2a2b2e", fg="#ffffff", selectcolor="#2a2b2e",
            font=("Malgun Gothic", 11)
        )
        self.chk3.pack(anchor="w")

        # ===== 실행 버튼 =====
        btn_run = styled_button(root, "✨ 정리 실행", self.run)
        btn_run.pack(pady=15)

        # ===== 로그 영역 =====
        self.txt_log = scrolledtext.ScrolledText(
            root,
            width=88,
            height=18,
            bg="#121314",
            fg="#e0e0e0",
            font=("Consolas", 10),
            relief="flat",
            insertbackground="#ffffff",
        )
        self.txt_log.pack(padx=20, pady=10)

        # 초기 폴더 경로
        self.selected_folder = None

    # =========================
    #       폴더 선택
    # =========================
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = Path(folder)
            self.lbl_folder.config(text=f"📁 선택한 폴더: {folder}")

    # =========================
    #        정리 실행
    # =========================
    def run(self):
        if not self.selected_folder:
            messagebox.showerror("오류", "먼저 폴더를 선택하세요.")
            return

        summary, logs = organize_images(
            self.selected_folder,
            move_duplicates=self.opt_dup.get(),
            move_similar=self.opt_sim.get(),
            sort_resolution=self.opt_res.get(),
        )

        self.txt_log.delete(1.0, tk.END)

        self.txt_log.insert(tk.END, "====== 실행 결과 ======\n")
        for key, val in summary.items():
            self.txt_log.insert(tk.END, f"{key}: {val}\n")

        self.txt_log.insert(tk.END, "\n====== 상세 로그 ======\n")
        for line in logs:
            self.txt_log.insert(tk.END, line + "\n")


# =========================
#         실행부
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageOrganizerGUI(root)
    root.mainloop()
