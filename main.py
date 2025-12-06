from pathlib import Path
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox

from src.img_organizer import organize_images
from src.report_generator import generate_html_report


# ===================== CLI 진입점 =====================

def run_cli():
    parser = argparse.ArgumentParser(description="이미지 정리 프로그램")

    parser.add_argument(
        "root",
        nargs="?",
        help="정리할 이미지 폴더 경로 (GUI 모드에서는 생략 가능)"
    )

    # 모드
    parser.add_argument(
        "--gui",
        action="store_true",
        help="GUI 모드 실행"
    )

    # 옵션 B 세트
    parser.add_argument("--move-duplicates", action="store_true", help="정확한 중복 이미지 정리")
    parser.add_argument("--move-similar", action="store_true", help="유사 이미지 정리")
    parser.add_argument("--sort-resolution", action="store_true", help="해상도 기준 정리")
    parser.add_argument("--sort-ext", action="store_true", help="확장자 기준 정리")
    parser.add_argument("--sort-date", action="store_true", help="촬영 날짜 기준 정리")
    parser.add_argument("--auto", action="store_true", help="모든 기능 자동 수행")

    args = parser.parse_args()

    # GUI 모드
    if args.gui:
        launch_gui()
        return

    # CLI 모드
    if not args.root:
        print("[ERROR] CLI 모드에서는 root 폴더를 지정해야 합니다.")
        return

    root = Path(args.root)
    if not root.exists():
        print("[ERROR] 폴더가 존재하지 않습니다:", root)
        return

    summary, logs = organize_images(
        root,
        move_duplicates=args.move_duplicates,
        move_similar=args.move_similar,
        sort_resolution=args.sort_resolution,
        sort_ext=args.sort_ext,
        sort_date=args.sort_date,
        auto=args.auto,
    )

    # 리포트 생성
    report_path = root / "_report" / "report.html"
    generate_html_report(report_path, summary, logs)
    print(f"\n[INFO] 리포트 생성: {report_path}")


# ===================== GUI =====================

class OrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 정리 프로그램")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        self.bg = "#1e1e1e"
        self.fg = "#e5e5e5"
        self.entry_bg = "#2b2b2b"
        self.btn_bg = "#3a3a3a"
        self.btn_blue = "#5c6bc0"

        # --- 제목 ---
        tk.Label(
            root,
            text="이미지 정리 프로그램",
            font=("Segoe UI", 20, "bold"),
            fg=self.fg,
            bg=self.bg,
        ).pack(pady=10)

        # --- 폴더 선택 영역 ---
        self.path_var = tk.StringVar()
        path_frame = tk.Frame(root, bg=self.bg)
        path_frame.pack(pady=5)

        tk.Button(
            path_frame,
            text="폴더 선택",
            command=self.select_folder,
            bg=self.btn_bg,
            fg=self.fg,
            width=12,
            relief="flat",
        ).grid(row=0, column=0, padx=5)

        tk.Entry(
            path_frame,
            textvariable=self.path_var,
            width=60,
            bg=self.entry_bg,
            fg=self.fg,
            relief="flat",
        ).grid(row=0, column=1, padx=5)

        # --- 옵션 체크박스 ---
        opt_frame = tk.LabelFrame(
            root,
            text="정리 옵션",
            fg=self.fg,
            bg=self.bg,
            padx=10,
            pady=10,
            labelanchor="n",
        )
        opt_frame.pack(pady=10)

        self.var_auto = tk.BooleanVar(value=False)
        self.var_dup = tk.BooleanVar(value=True)
        self.var_sim = tk.BooleanVar(value=True)
        self.var_res = tk.BooleanVar(value=True)
        self.var_ext = tk.BooleanVar(value=True)
        self.var_date = tk.BooleanVar(value=True)

        # 자동 정리
        tk.Checkbutton(
            opt_frame,
            text="전체 자동 정리 (--auto)",
            variable=self.var_auto,
            command=self.on_auto_toggle,
            bg=self.bg,
            fg="#ffd54f",
            selectcolor=self.bg,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=3)

        # 개별 옵션
        tk.Checkbutton(
            opt_frame,
            text="정확한 중복 이미지 정리",
            variable=self.var_dup,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).grid(row=1, column=0, sticky="w", pady=2)

        tk.Checkbutton(
            opt_frame,
            text="유사 이미지 정리",
            variable=self.var_sim,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).grid(row=1, column=1, sticky="w", pady=2)

        tk.Checkbutton(
            opt_frame,
            text="해상도 기준 정리",
            variable=self.var_res,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).grid(row=2, column=0, sticky="w", pady=2)

        tk.Checkbutton(
            opt_frame,
            text="확장자 기준 정리",
            variable=self.var_ext,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).grid(row=2, column=1, sticky="w", pady=2)

        tk.Checkbutton(
            opt_frame,
            text="촬영 날짜 기준 정리",
            variable=self.var_date,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).grid(row=3, column=0, sticky="w", pady=2)

        # --- 실행 버튼 ---
        tk.Button(
            root,
            text="정리 실행",
            command=self.run_organize,
            bg=self.btn_blue,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=20,
            relief="flat",
        ).pack(pady=10)

        # --- 로그 창 ---
        self.log = tk.Text(
            root,
            bg=self.entry_bg,
            fg=self.fg,
            relief="flat",
            font=("Consolas", 11),
        )
        self.log.pack(expand=True, fill="both", padx=10, pady=10)

    def log_print(self, msg: str):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.log_print(f"[INFO] 선택한 폴더: {folder}")

    def on_auto_toggle(self):
        # 자동 정리 체크되면 나머지 옵션은 전부 체크만 하고 비활성화
        auto = self.var_auto.get()
        state = tk.DISABLED if auto else tk.NORMAL

        if auto:
            self.var_dup.set(True)
            self.var_sim.set(True)
            self.var_res.set(True)
            self.var_ext.set(True)
            self.var_date.set(True)

        # 체크박스 비활성화/활성화는 조금 귀찮아서 여기선 단순히 옵션 값만 처리하고
        # 실제 실행 시에 auto=True 이면 개별 옵션은 무시하지 않고 "전부 사용"으로 처리함.

    def run_organize(self):
        folder = self.path_var.get()
        if not folder:
            messagebox.showerror("오류", "폴더를 먼저 선택하세요.")
            return

        root_path = Path(folder)
        if not root_path.exists():
            messagebox.showerror("오류", "폴더가 존재하지 않습니다.")
            return

        self.log_print("\n[INFO] 정리 시작...\n")

        summary, logs = organize_images(
            root_path,
            move_duplicates=self.var_dup.get(),
            move_similar=self.var_sim.get(),
            sort_resolution=self.var_res.get(),
            sort_ext=self.var_ext.get(),
            sort_date=self.var_date.get(),
            auto=self.var_auto.get(),
        )

        for line in logs:
            self.log_print(line)

        report_path = root_path / "_report" / "report.html"
        generate_html_report(report_path, summary, logs)
        self.log_print(f"\n[INFO] 리포트 생성: {report_path}")
        messagebox.showinfo("완료", "이미지 정리가 완료되었습니다!")



def launch_gui():
    root = tk.Tk()
    app = OrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_cli()
