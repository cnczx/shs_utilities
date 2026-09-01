import tkinter as tk
import random
import json
import ctypes
import webbrowser
from tkinter import messagebox

BORDER_COLOR = "#B0B0B0"

class RandomChoiceApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("随机选号")
        # 主窗口固定为 200x150
        self.root.geometry("200x150")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.configure(bg=BORDER_COLOR)

        self.settings_file = "random_choice_settings.json"
        self.load_settings()

        self.settings_window = None
        self.info_window = None

        # 内部容器尺寸 = 窗口尺寸 - 2*边框
        self.main_container = tk.Frame(self.root, bg='SystemButtonFace',
                                       highlightthickness=0, bd=0)
        self.main_container.place(x=2, y=2, width=196, height=146)

        self.create_widgets()
        self.position_window_left_bottom()
        self.bind_drag_events(self.root)
        self.bind_drag_events(self.main_container)

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.min_val = int(data.get('min_val', 1))
                self.max_val = int(data.get('max_val', 100))
                self.exclude_list = [int(x) for x in data.get('exclude_list', [])]
        except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
            self.min_val = 1
            self.max_val = 100
            self.exclude_list = []

    def save_settings_to_file(self):
        data = {
            'min_val': self.min_val,
            'max_val': self.max_val,
            'exclude_list': self.exclude_list
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def create_widgets(self):
        # 左上角标题（字体稍缩小）
        self.title_label = tk.Label(self.main_container, text="随机选号",
                                    font=("Arial", 9))
        self.title_label.place(relx=0.0, x=5, y=3, anchor="nw")

        # 右上角红色衬底 + 关闭按钮（尺寸微调）
        self.close_bg = tk.Frame(self.main_container, bg="red", width=18, height=18)
        self.close_bg.place(relx=1.0, x=-4, y=4, anchor="ne")
        self.close_bg.pack_propagate(False)
        self.close_btn = tk.Button(self.close_bg, text="×", font=("Arial", 10),
                                   command=self.root.destroy, relief="flat",
                                   bd=0, highlightthickness=0,
                                   bg="red", fg="white",
                                   activebackground="darkred",
                                   activeforeground="white")
        self.close_btn.pack(fill="both", expand=True)

        # 中间 Random Choice 按钮（字体稍缩小）
        self.random_btn = tk.Button(self.main_container, text="随机选号",
                                    font=("Arial", 12), width=12,
                                    command=self.random_choice)
        self.random_btn.place(relx=0.5, rely=0.5, anchor="center")

        # 结果显示标签
        self.result_label = tk.Label(self.main_container, text="", font=("Arial", 14),
                                     fg="blue")
        self.result_label.place(relx=0.5, rely=0.75, anchor="center")

        # 右下角 Settings 按钮（字体稍缩小）
        self.settings_btn = tk.Button(self.main_container, text="设置",
                                      font=("Arial", 7), relief="ridge",
                                      command=self.open_settings)
        self.settings_btn.place(relx=1.0, rely=1.0, x=-4, y=-4, anchor="se")

    def get_work_area(self):
        try:
            class RECT(ctypes.Structure):
                _fields_ = [('left', ctypes.c_long),
                            ('top', ctypes.c_long),
                            ('right', ctypes.c_long),
                            ('bottom', ctypes.c_long)]
            rect = RECT()
            ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
            return rect.left, rect.top, rect.right, rect.bottom
        except:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            return 0, 0, screen_w, screen_h - 40

    def position_window_left_bottom(self):
        self.root.update_idletasks()
        work_left, work_top, work_right, work_bottom = self.get_work_area()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        x = work_left
        y = work_bottom - win_height
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")

    def bind_drag_events(self, widget):
        widget.bind("<Button-1>", lambda e, w=widget: self.start_drag(e, w))
        widget.bind("<B1-Motion>", lambda e, w=widget: self.on_drag(e, w))

    def start_drag(self, event, widget):
        if event.widget == widget:
            top = widget.winfo_toplevel()
            top._drag_start_x = event.x_root - top.winfo_x()
            top._drag_start_y = event.y_root - top.winfo_y()

    def on_drag(self, event, widget):
        top = widget.winfo_toplevel()
        if hasattr(top, '_drag_start_x') and hasattr(top, '_drag_start_y'):
            x = event.x_root - top._drag_start_x
            y = event.y_root - top._drag_start_y
            top.geometry(f"+{x}+{y}")

    def random_choice(self):
        candidates = [n for n in range(self.min_val, self.max_val + 1)
                      if n not in self.exclude_list]
        if not candidates:
            self.result_label.config(text="无可用号码")
            return
        result = random.choice(candidates)
        self.result_label.config(text=str(result))

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("设置")
        # 设置窗口固定为 200x150
        self.settings_window.geometry("150x150")
        self.settings_window.attributes('-topmost', True)
        self.settings_window.overrideredirect(True)
        self.settings_window.resizable(False, False)
        self.settings_window.configure(bg=BORDER_COLOR)
        self.settings_window.withdraw()  # 先隐藏，避免闪烁

        # 内部容器尺寸
        self.settings_container = tk.Frame(self.settings_window, bg='SystemButtonFace')
        self.settings_container.place(x=2, y=2, width=146, height=146)

        # 左上角标题（字体缩小）
        title_label = tk.Label(self.settings_container, text="设置",
                               font=("Arial", 10))
        title_label.grid(row=0, column=0, columnspan=3, pady=(2, 2))

        # 最小值输入（字体缩小，间距减小）
        tk.Label(self.settings_container, text="最小值:", font=("Arial", 8)).grid(row=1, column=0,
                                                                              padx=3, pady=2, sticky="e")
        self.min_entry = tk.Entry(self.settings_container, width=8, font=("Arial", 8))
        self.min_entry.grid(row=1, column=1, padx=3, pady=2)
        self.min_entry.insert(0, str(self.min_val))

        # 最大值输入
        tk.Label(self.settings_container, text="最大值:", font=("Arial", 8)).grid(row=2, column=0,
                                                                              padx=3, pady=2, sticky="e")
        self.max_entry = tk.Entry(self.settings_container, width=8, font=("Arial", 8))
        self.max_entry.grid(row=2, column=1, padx=3, pady=2)
        self.max_entry.insert(0, str(self.max_val))

        # 排除项输入（标签缩短）
        tk.Label(self.settings_container, text="排除项:", font=("Arial", 8)).grid(row=3, column=0,
                                                                              padx=3, pady=2, sticky="e")
        self.exclude_entry = tk.Entry(self.settings_container, width=14, font=("Arial", 8))
        self.exclude_entry.grid(row=3, column=1, padx=3, pady=2)
        self.exclude_entry.insert(0, ", ".join(map(str, self.exclude_list)))

        # 按钮行：Save 居中
        btn_frame = tk.Frame(self.settings_container)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(4, 18), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=0)
        btn_frame.grid_columnconfigure(2, weight=1)

        save_btn = tk.Button(btn_frame, text="保存", font=("Arial", 8),
                             command=self.save_settings)
        save_btn.grid(row=0, column=1, padx=3)

        # Info 按钮右下角（字体缩小）
        info_btn = tk.Button(self.settings_container, text="ⓘ", font=("Arial", 8),
                             relief="flat", bd=0, highlightthickness=0,
                             command=self.open_info_window)
        info_btn.place(relx=1.0, rely=1.0, x=-3, y=-3, anchor="se")

        # 不再动态调整高度，直接使用固定尺寸
        self.bind_drag_events(self.settings_window)
        self.bind_drag_events(self.settings_container)

        self.position_settings_window()
        self.settings_window.deiconify()

    def position_settings_window(self):
        self.settings_window.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_w = self.root.winfo_width()
        main_h = self.root.winfo_height()
        settings_w = self.settings_window.winfo_width()
        settings_h = self.settings_window.winfo_height()

        x = main_x + main_w + 10
        y = main_y + (main_h - settings_h) // 2

        work_left, work_top, work_right, work_bottom = self.get_work_area()
        if x + settings_w > work_right:
            x = work_right - settings_w
        if y + settings_h > work_bottom:
            y = work_bottom - settings_h
        if y < work_top:
            y = work_top
        if x < work_left:
            x = work_left

        self.settings_window.geometry(f"+{x}+{y}")

    def open_info_window(self):
        if self.info_window and self.info_window.winfo_exists():
            self.info_window.deiconify()
            self.info_window.lift()
            self.info_window.focus_force()
            return

        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("关于")
        self.info_window.geometry("320x100")
        self.info_window.attributes('-topmost', True)
        self.info_window.overrideredirect(True)
        self.info_window.resizable(False, False)
        self.info_window.configure(bg=BORDER_COLOR)
        self.info_window.withdraw()

        info_container = tk.Frame(self.info_window, bg='SystemButtonFace')
        info_container.pack(fill="both", expand=True, padx=2, pady=2)

        title_label = tk.Label(info_container, text="关于", font=("Arial", 12))
        title_label.place(x=5, y=5, anchor="nw")

        close_bg = tk.Frame(info_container, bg="red", width=20, height=20)
        close_bg.place(relx=1.0, x=-5, y=5, anchor="ne")
        close_bg.pack_propagate(False)
        close_btn = tk.Button(close_bg, text="×", font=("Arial", 12),
                              command=self.close_info_window, relief="flat",
                              bd=0, highlightthickness=0,
                              bg="red", fg="white",
                              activebackground="darkred",
                              activeforeground="white")
        close_btn.pack(fill="both", expand=True)

        url = "https://github.com/cnczx/shs_utilities"
        link_label = tk.Label(info_container, text=url, font=("Arial", 10, "underline"),
                              fg="blue", cursor="hand2")
        link_label.place(relx=0.5, rely=0.6, anchor="center")
        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))

        self.bind_drag_events(self.info_window)
        self.bind_drag_events(info_container)

        self.position_info_window()
        self.info_window.deiconify()
        self.info_window.lift()
        self.info_window.focus_force()

    def position_info_window(self):
        self.info_window.update_idletasks()
        if self.settings_window and self.settings_window.winfo_exists():
            base = self.settings_window
        else:
            base = self.root
        base_x = base.winfo_x()
        base_y = base.winfo_y()
        base_w = base.winfo_width()
        base_h = base.winfo_height()
        info_w = self.info_window.winfo_width()
        info_h = self.info_window.winfo_height()

        x = base_x + base_w + 10
        y = base_y + (base_h - info_h) // 2

        work_left, work_top, work_right, work_bottom = self.get_work_area()
        if x + info_w > work_right:
            x = work_right - info_w
        if y + info_h > work_bottom:
            y = work_bottom - info_h
        if y < work_top:
            y = work_top
        if x < work_left:
            x = work_left

        if x < 0 or y < 0 or x + info_w > self.root.winfo_screenwidth() or y + info_h > self.root.winfo_screenheight():
            x = (self.root.winfo_screenwidth() - info_w) // 2
            y = (self.root.winfo_screenheight() - info_h) // 2

        self.info_window.geometry(f"+{x}+{y}")

    def close_info_window(self):
        if self.info_window:
            self.info_window.destroy()
            self.info_window = None

    def save_settings(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            if min_val > max_val:
                messagebox.showerror("错误", "最小值不能大于最大值", parent=self.settings_window)
                return
            exclude_str = self.exclude_entry.get().strip()
            if exclude_str:
                exclude_list = [int(x.strip()) for x in exclude_str.split(',') if x.strip()]
            else:
                exclude_list = []
            self.min_val = min_val
            self.max_val = max_val
            self.exclude_list = exclude_list
            self.save_settings_to_file()
            self.settings_window.destroy()
            self.settings_window = None
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数", parent=self.settings_window)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RandomChoiceApp()
    app.run()
