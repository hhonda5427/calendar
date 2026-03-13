# -*- coding: utf-8 -*-
"""
休日カレンダーアプリ
カレンダーを表示し、日付をクリックして休日を指定し、日付・休日名のCSVを出力します。
"""
import calendar
import csv
import io
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime


# パステルカラー
COLORS = {
    "bg": "#fff8f5",
    "panel_bg": "#faf0f5",
    "day_normal": "#f5f0fa",
    "day_holiday": "#e0f0e8",
    "day_normal_active": "#ebe5f5",
    "day_holiday_active": "#c8e6d4",
    "weekday_bg": "#f0e8f0",
}

WEEKDAY_NAMES = ["月", "火", "水", "木", "金", "土", "日"]


def _get_app_dir():
    """スクリプトまたは exe があるフォルダを返す（PyInstaller 対応）"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _normalize_date_str(s):
    """yyyy/mm/dd, yyyy/m/dd, yyyy/mm/d, yyyy/m/d を yyyy/mm/dd に正規化。失敗時は None。"""
    s = s.strip()
    if not s or "/" not in s:
        return None
    parts = s.split("/")
    if len(parts) != 3:
        return None
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(y, m, d)
        return f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}"
    except (ValueError, TypeError):
        return None


def _nth_weekday_name(date_key):
    """日付から「第N曜日」を返す。例: 2025/03/08 → 第2土曜日"""
    try:
        y, m, d = map(int, date_key.split("/"))
        dt = datetime(y, m, d)
        # 月曜=0 ... 日曜=6
        wd = dt.weekday()
        n = (d - 1) // 7 + 1
        return f"第{n}{WEEKDAY_NAMES[wd]}曜日"
    except Exception:
        return ""


class HolidayCalendarApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("休日カレンダー - CSV出力")
        self.root.geometry("520x420")
        self.root.minsize(400, 360)
        self.root.configure(bg=COLORS["bg"])

        # 日付 -> 休日名（空文字で「名前なし休日」）
        self.holidays = {}
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month

        self._setup_styles()
        self._build_ui()
        self._load_tokai_calendar_if_exists()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure(".", background=COLORS["bg"])
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground="#2d2d2d")
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), background=COLORS["panel_bg"])
        style.configure("Month.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Weekday.TLabel", font=("Segoe UI", 9, "bold"), background=COLORS["weekday_bg"])
        style.configure("TLabelframe", background=COLORS["panel_bg"])
        style.configure("TLabelframe.Label", background=COLORS["panel_bg"], foreground="#2d2d2d")
        style.configure("TButton", background="#e8e0f0")

    def _build_ui(self):
        # メインコンテナ
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # 上部: ナビゲーション + 月表示 + CSV
        nav_frame = ttk.Frame(main)
        nav_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(nav_frame, text="◀ 前月", command=self._prev_month).pack(side=tk.LEFT, padx=2)
        self.month_label = ttk.Label(nav_frame, text="", style="Month.TLabel")
        self.month_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(nav_frame, text="翌月 ▶", command=self._next_month).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav_frame, text="CSVに保存...", command=self._save_csv).pack(side=tk.RIGHT, padx=4)
        ttk.Button(nav_frame, text="CSVを読み込み...", command=self._load_csv).pack(side=tk.RIGHT, padx=2)

        # カレンダー
        cal_frame = ttk.LabelFrame(main, text="日付をクリックで休日の指定／解除", padding=8)
        cal_frame.pack(fill=tk.BOTH, expand=True)
        self.cal_container = ttk.Frame(cal_frame)
        self.cal_container.pack(fill=tk.BOTH, expand=True)
        self._day_buttons = []

        self._refresh_calendar()

    def _get_month_text(self):
        return f"{self.current_year}年 {self.current_month}月"

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._refresh_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._refresh_calendar()

    def _refresh_calendar(self):
        self.month_label.config(text=self._get_month_text())
        for w in self.cal_container.winfo_children():
            w.destroy()
        self._day_buttons.clear()

        # 曜日ヘッダー（日曜始まり）
        weekdays = ["日", "月", "火", "水", "木", "金", "土"]
        for i, wd in enumerate(weekdays):
            lbl = ttk.Label(self.cal_container, text=wd, style="Weekday.TLabel")
            lbl.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
        for i in range(7):
            self.cal_container.columnconfigure(i, weight=1)

        cal = calendar.Calendar(calendar.SUNDAY)
        weeks = cal.monthdays2calendar(self.current_year, self.current_month)
        for r, week in enumerate(weeks):
            for c, (day, _) in enumerate(week):
                if day == 0:
                    ttk.Label(self.cal_container, text="").grid(row=r + 1, column=c, padx=2, pady=2)
                    continue
                date_key = f"{self.current_year}/{self.current_month:02d}/{day:02d}"
                is_holiday = date_key in self.holidays
                name = self.holidays.get(date_key, "")
                btn_text = f"{day}\n{name}" if name else str(day)
                btn = tk.Button(
                    self.cal_container,
                    text=btn_text,
                    font=("Segoe UI", 9),
                    relief=tk.RAISED,
                    bd=1,
                    cursor="hand2",
                    bg=COLORS["day_holiday"] if is_holiday else COLORS["day_normal"],
                    fg="#2d2d2d",
                    activebackground=COLORS["day_holiday_active"] if is_holiday else COLORS["day_normal_active"],
                    wraplength=64,
                )
                btn.grid(row=r + 1, column=c, sticky="nsew", padx=2, pady=2)
                btn.bind("<Button-1>", lambda e, dk=date_key: self._on_date_click(dk))
                btn.bind("<Button-3>", lambda e, dk=date_key: self._on_date_right_click(dk))
                self._day_buttons.append((date_key, btn))
        for r in range(len(weeks) + 1):
            self.cal_container.rowconfigure(r, weight=1)

    def _on_date_click(self, date_key):
        if date_key in self.holidays:
            del self.holidays[date_key]
        else:
            self.holidays[date_key] = _nth_weekday_name(date_key)
        self._refresh_calendar()

    def _on_date_right_click(self, date_key):
        """右クリックで休日名を編集（休日指定済みの日のみ）"""
        if date_key not in self.holidays:
            messagebox.showinfo("編集", "休日として指定されている日のみ、右クリックで休日名を編集できます。", parent=self.root)
            return
        current_name = self.holidays[date_key]
        new_name = simpledialog.askstring(
            "休日名の編集",
            f"日付: {date_key}\n休日名を入力してください。",
            initialvalue=current_name,
            parent=self.root,
        )
        if new_name is not None:
            self.holidays[date_key] = new_name.strip()
            self._refresh_calendar()

    def _save_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("すべて", "*.*")],
            initialdir=_get_app_dir(),
            initialfile="holiday_calendar.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["日付", "休日名"])
                for date_key in sorted(self.holidays.keys()):
                    writer.writerow([date_key, self.holidays[date_key]])
            messagebox.showinfo("保存完了", f"保存しました:\n{path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました:\n{e}", parent=self.root)

    def _parse_csv_rows(self, path):
        """CSVから (日付, 休日名) のリストを返す。ヘッダー行は自動判定してスキップ。"""
        encodings = ("utf-8-sig", "utf-8", "cp932", "shift_jis")
        content = None
        for enc in encodings:
            try:
                with open(path, "rb") as f:
                    content = f.read().decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if content is None:
            raise ValueError("CSVの文字コードを判別できませんでした。")
        rows = []
        reader = csv.reader(io.StringIO(content))
        for i, row in enumerate(reader):
            if not row or not row[0].strip():
                continue
            # 1行目がヘッダーかどうか（「日付」または日付形式でない）
            raw_date = row[0].strip()
            if i == 0 and (raw_date == "日付" or "/" not in raw_date):
                continue
            date_str = _normalize_date_str(raw_date)
            if date_str is None:
                continue
            name_str = row[1].strip() if len(row) > 1 else ""
            rows.append((date_str, name_str))
        return rows

    def _load_tokai_calendar_if_exists(self):
        """同一ディレクトリに tokai-calendar.csv があれば読み込む"""
        try:
            base = _get_app_dir()
            path = os.path.join(base, "tokai-calendar.csv")
            if not os.path.isfile(path):
                return
            for date_str, name_str in self._parse_csv_rows(path):
                self.holidays[date_str] = name_str
            self._refresh_calendar()
        except Exception:
            pass

    def _load_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("すべて", "*.*")],
            initialdir=_get_app_dir(),
            initialfile="tokai-calendar.csv",
        )
        if not path:
            return
        try:
            loaded = {}
            for date_str, name_str in self._parse_csv_rows(path):
                loaded[date_str] = name_str
            self.holidays.update(loaded)
            self._refresh_calendar()
            messagebox.showinfo("読み込み完了", f"{len(loaded)}件を読み込みました。", parent=self.root)
        except Exception as e:
            messagebox.showerror("エラー", f"読み込みに失敗しました:\n{e}", parent=self.root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HolidayCalendarApp()
    app.run()
