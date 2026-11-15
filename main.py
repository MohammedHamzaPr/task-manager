import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database
from translations import get_text

# ===== لوحات الألوان =====
THEMES = {
    "light": {
        "bg": "#F5F7FA",
        "card": "#FFFFFF",
        "text": "#2C3E50",
        "text_secondary": "#7F8C8D",
        "primary": "#4A90A4",
        "primary_hover": "#3A7A8C",
        "success": "#27AE60",
        "danger": "#E74C3C",
        "warning": "#F39C12",
        "border": "#DDE3EA",
        "entry_bg": "#FFFFFF",
        "header": "#4A90A4",
        "header_text": "#FFFFFF",
    },
    "dark": {
        "bg": "#1E2530",
        "card": "#2A3441",
        "text": "#E8EDF2",
        "text_secondary": "#95A5B5",
        "primary": "#5BA3B8",
        "primary_hover": "#4A8FA3",
        "success": "#2ECC71",
        "danger": "#E74C3C",
        "warning": "#F39C12",
        "border": "#3A4553",
        "entry_bg": "#232B37",
        "header": "#2A3441",
        "header_text": "#E8EDF2",
    }
}


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.current_user = None
        self.lang = "ar"
        self.theme = "light"
        self.colors = THEMES[self.theme]

        self.root.title(get_text(self.lang, "app_title"))
        self.root.geometry("1000x680")
        self.root.minsize(900, 600)
        self.center_window()
        self.root.configure(bg=self.colors["bg"])

        self.show_login()

    def center_window(self):
        self.root.update_idletasks()
        w, h = 1000, 680
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def t(self, key):
        return get_text(self.lang, key)

    def refresh_theme(self):
        self.colors = THEMES[self.theme]
        self.root.configure(bg=self.colors["bg"])

    def clear_root(self):
        # إزالة ربط عجلة الفأرة القديم إن وجد
        if hasattr(self, "_task_scroll_handler") and self._task_scroll_handler:
            try:
                self.root.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass
            self._task_scroll_handler = None
            self._task_canvas = None

        for widget in self.root.winfo_children():
            widget.destroy()
    # ============================================================
    # ============ 1. واجهة تسجيل الدخول =========================
    # ============================================================
    def show_login(self):
        self.clear_root()
        self.refresh_theme()
        c = self.colors

        main = tk.Frame(self.root, bg=c["bg"])
        main.pack(fill="both", expand=True)

        # بطاقة مركزية
        card = tk.Frame(main, bg=c["card"], highlightbackground=c["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=520)

        # أيقونة/عنوان
        tk.Label(card, text="✓", font=("Segoe UI", 42, "bold"),
                 bg=c["card"], fg=c["primary"]).pack(pady=(35, 5))
        tk.Label(card, text=self.t("login"), font=("Segoe UI", 22, "bold"),
                 bg=c["card"], fg=c["text"]).pack(pady=(0, 25))

        # اسم المستخدم
        tk.Label(card, text=self.t("username"), font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", padx=45)
        self.login_user = tk.Entry(card, font=("Segoe UI", 11), bg=c["entry_bg"],
                                    fg=c["text"], insertbackground=c["text"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=c["border"], highlightcolor=c["primary"])
        self.login_user.pack(pady=(4, 12), padx=45, fill="x", ipady=7)

        # كلمة المرور
        tk.Label(card, text=self.t("password"), font=("Segoe UI", 11),
                 bg=c["card"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", padx=45)
        self.login_pass = tk.Entry(card, font=("Segoe UI", 11), show="●", bg=c["entry_bg"],
                                    fg=c["text"], insertbackground=c["text"],
                                    relief="flat", highlightthickness=1,
                                    highlightbackground=c["border"], highlightcolor=c["primary"])
        self.login_pass.pack(pady=(4, 20), padx=45, fill="x", ipady=7)
        self.login_pass.bind("<Return>", lambda e: self.do_login())

        # زر الدخول
        btn = tk.Button(card, text=self.t("login_btn"), font=("Segoe UI", 12, "bold"),
                        bg=c["primary"], fg="white", relief="flat", cursor="hand2",
                        command=self.do_login, activebackground=c["primary_hover"],
                        activeforeground="white", bd=0)
        btn.pack(pady=(0, 15), padx=45, fill="x", ipady=9)
        btn.bind("<Enter>", lambda e: btn.config(bg=c["primary_hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=c["primary"]))

        # رابط إنشاء حساب
        link_frame = tk.Frame(card, bg=c["card"])
        link_frame.pack(pady=(0, 15))
        tk.Label(link_frame, text=self.t("no_account"), font=("Segoe UI", 10),
                 bg=c["card"], fg=c["text_secondary"]).pack(side="left", padx=(0, 4))
        signup_link = tk.Label(link_frame, text=self.t("create_account"),
                                font=("Segoe UI", 10, "underline"),
                                bg=c["card"], fg=c["primary"], cursor="hand2")
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.show_signup())

        # أزرار اللغة والثيم
        self._add_theme_lang_buttons(main)

    def _add_theme_lang_buttons(self, parent):
        c = self.colors
        frame = tk.Frame(parent, bg=c["bg"])
        frame.place(relx=0.5, rely=0.95, anchor="center")

        lang_text = "EN" if self.lang == "ar" else "AR"
        tk.Button(frame, text=lang_text, font=("Segoe UI", 10, "bold"),
                  bg=c["card"], fg=c["text"], relief="flat", cursor="hand2",
                  command=self.toggle_lang, width=5, bd=0).pack(side="left", padx=5)

        theme_text = "🌙" if self.theme == "light" else "☀"
        tk.Button(frame, text=theme_text, font=("Segoe UI", 11),
                  bg=c["card"], fg=c["text"], relief="flat", cursor="hand2",
                  command=self.toggle_theme, width=5, bd=0).pack(side="left", padx=5)

    def toggle_lang(self):
        self.lang = "en" if self.lang == "ar" else "ar"
        if self.current_user:
            self.db.update_user(self.current_user["id"], language=self.lang)
            self.current_user["language"] = self.lang
            self.show_main()
        else:
            self.show_login()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.refresh_theme()
        if self.current_user:
            self.db.update_user(self.current_user["id"], theme=self.theme)
            self.current_user["theme"] = self.theme
            self.show_main()
        else:
            self.show_login()

    def do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get().strip()
        if not username or not password:
            messagebox.showwarning(self.t("error"), self.t("fill_fields"))
            return
        user = self.db.verify_user(username, password)
        if user:
            self.current_user = user
            self.lang = user["language"]
            self.theme = user["theme"]
            self.refresh_theme()
            self.show_main()
        else:
            messagebox.showerror(self.t("error"), self.t("wrong_credentials"))

    # ============================================================
    # ============ 2. واجهة إنشاء الحساب =========================
    # ============================================================
    def show_signup(self):
        self.clear_root()
        self.refresh_theme()
        c = self.colors

        main = tk.Frame(self.root, bg=c["bg"])
        main.pack(fill="both", expand=True)

        card = tk.Frame(main, bg=c["card"], highlightbackground=c["border"], highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=620)

        tk.Label(card, text="👤", font=("Segoe UI", 42),
                 bg=c["card"], fg=c["primary"]).pack(pady=(30, 5))
        tk.Label(card, text=self.t("signup_title"), font=("Segoe UI", 20, "bold"),
                 bg=c["card"], fg=c["text"]).pack(pady=(0, 20))

        def add_field(label, show=None):
            tk.Label(card, text=label, font=("Segoe UI", 11),
                     bg=c["card"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", padx=45)
            e = tk.Entry(card, font=("Segoe UI", 11), show=show, bg=c["entry_bg"],
                         fg=c["text"], insertbackground=c["text"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=c["border"], highlightcolor=c["primary"])
            e.pack(pady=(4, 12), padx=45, fill="x", ipady=7)
            return e

        full_name = add_field(self.t("full_name"))
        username = add_field(self.t("username"))
        password = add_field(self.t("password"), show="●")
        confirm = add_field(self.t("confirm_password"), show="●")

        def do_signup(event=None):
            fn = full_name.get().strip()
            un = username.get().strip()
            pw = password.get().strip()
            cf = confirm.get().strip()

            if not un or not pw or not cf:
                messagebox.showwarning(self.t("error"), self.t("fill_fields"))
                return
            if pw != cf:
                messagebox.showerror(self.t("error"), self.t("passwords_mismatch"))
                return
            uid, ok = self.db.create_user(un, pw, fn)
            if ok:
                messagebox.showinfo(self.t("success"), self.t("success"))
                self.show_login()
            else:
                messagebox.showerror(self.t("error"), self.t("user_exists"))

        confirm.bind("<Return>", do_signup)

        btn = tk.Button(card, text=self.t("signup_btn"), font=("Segoe UI", 12, "bold"),
                        bg=c["primary"], fg="white", relief="flat", cursor="hand2",
                        command=do_signup, activebackground=c["primary_hover"], bd=0)
        btn.pack(pady=(5, 15), padx=45, fill="x", ipady=9)

        link_frame = tk.Frame(card, bg=c["card"])
        link_frame.pack(pady=(0, 15))
        tk.Label(link_frame, text=self.t("have_account"), font=("Segoe UI", 10),
                 bg=c["card"], fg=c["text_secondary"]).pack(side="left", padx=(0, 4))
        back = tk.Label(link_frame, text=self.t("back_to_login"),
                         font=("Segoe UI", 10, "underline"),
                         bg=c["card"], fg=c["primary"], cursor="hand2")
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self.show_login())

        self._add_theme_lang_buttons(main)

    # ============================================================
    # ============ 3. الواجهة الرئيسية ============================
    # ============================================================
    def show_main(self):
        self.clear_root()
        self.refresh_theme()
        c = self.colors

        # شريط علوي
        header = tk.Frame(self.root, bg=c["header"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=f"📋 {self.t('app_title')}", font=("Segoe UI", 16, "bold"),
                 bg=c["header"], fg=c["header_text"]).pack(side="left", padx=20)

        # أزرار يمين الشريط
        btns = tk.Frame(header, bg=c["header"])
        btns.pack(side="right", padx=15)

        def hbtn(text, cmd):
            b = tk.Button(btns, text=text, font=("Segoe UI", 10),
                          bg=c["header"], fg=c["header_text"], relief="flat",
                          cursor="hand2", command=cmd, bd=0, padx=10)
            b.pack(side="left", padx=3)
            b.bind("<Enter>", lambda e: b.config(bg=c["primary_hover"]))
            b.bind("<Leave>", lambda e: b.config(bg=c["header"]))
            return b

        hbtn(f"👤 {self.current_user['username']}", lambda: None)
        hbtn(f"📊 {self.t('reports')}", self.show_reports)
        hbtn(f"⚙ {self.t('settings')}", self.show_settings)
        hbtn(f"🚪 {self.t('logout')}", self.do_logout)
        hbtn("EN" if self.lang == "ar" else "AR", self.toggle_lang)
        hbtn("🌙" if self.theme == "light" else "☀", self.toggle_theme)

        # شريط الأدوات
        toolbar = tk.Frame(self.root, bg=c["bg"])
        toolbar.pack(fill="x", padx=20, pady=15)

        add_btn = tk.Button(toolbar, text=f"+ {self.t('add_task')}",
                            font=("Segoe UI", 11, "bold"),
                            bg=c["primary"], fg="white", relief="flat",
                            cursor="hand2", command=self.show_add_task_dialog,
                            activebackground=c["primary_hover"], bd=0)
        add_btn.pack(side="left", ipadx=15, ipady=7)

        # فلتر
        self.filter_var = tk.StringVar(value="all")
        filter_frame = tk.Frame(toolbar, bg=c["bg"])
        filter_frame.pack(side="right")

        for val, label in [("all", self.t("all")),
                           ("pending", self.t("pending")),
                           ("completed", self.t("completed"))]:
            rb = tk.Radiobutton(filter_frame, text=label, variable=self.filter_var,
                                value=val, font=("Segoe UI", 10), bg=c["bg"], fg=c["text"],
                                selectcolor=c["card"], activebackground=c["bg"],
                                activeforeground=c["text"], command=self.load_tasks,
                                cursor="hand2")
            rb.pack(side="left", padx=6)

        # منطقة المهام
        self.tasks_container = tk.Frame(self.root, bg=c["bg"])
        self.tasks_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_tasks()

    def load_tasks(self):
        for w in self.tasks_container.winfo_children():
            w.destroy()

        c = self.colors
        filt = self.filter_var.get() if hasattr(self, "filter_var") else "all"
        tasks = self.db.get_tasks(self.current_user["id"], None if filt == "all" else filt)

        if not tasks:
            tk.Label(self.tasks_container, text=self.t("no_tasks"),
                     font=("Segoe UI", 14), bg=c["bg"], fg=c["text_secondary"]).pack(pady=40)
            return

        # Canvas + Scrollbar
        canvas = tk.Canvas(self.tasks_container, bg=c["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tasks_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=c["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=960)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        # حفظ المراجع
        self._task_canvas = canvas
        self._task_scroll_handler = on_mousewheel
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        for task in tasks:
            self.create_task_card(scroll_frame, task)

    def create_task_card(self, parent, task):
        c = self.colors
        completed = task["status"] == "completed"

        card = tk.Frame(parent, bg=c["card"], highlightbackground=c["border"],
                        highlightthickness=1)
        card.pack(fill="x", pady=6, padx=2)

        # خط جانبي يدل على الأولوية
        priority_colors = {
            "high": c["danger"],
            "medium": c["warning"],
            "low": c["success"]
        }
        side = tk.Frame(card, bg=priority_colors.get(task["priority"], c["primary"]), width=5)
        side.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=c["card"])
        inner.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        # عنوان
        title_frame = tk.Frame(inner, bg=c["card"])
        title_frame.pack(fill="x")

        title_text = task["title"]
        if completed:
            title_text = "✓ " + title_text

        lbl = tk.Label(title_frame, text=title_text, font=("Segoe UI", 12, "bold"),
                       bg=c["card"], fg=c["text_secondary"] if completed else c["text"],
                       anchor="e" if self.lang == "ar" else "w")
        lbl.pack(side="right" if self.lang == "ar" else "left")

        # وصف
        if task["description"]:
            tk.Label(inner, text=task["description"], font=("Segoe UI", 10),
                     bg=c["card"], fg=c["text_secondary"],
                     anchor="e" if self.lang == "ar" else "w",
                     wraplength=700, justify="right" if self.lang == "ar" else "left").pack(
                fill="x", pady=(4, 0))

        # تفاصيل
        details = tk.Frame(inner, bg=c["card"])
        details.pack(fill="x", pady=(6, 0))

        prio_text = self.t(task["priority"])
        tk.Label(details, text=f"⚑ {self.t('priority')}: {prio_text}",
                 font=("Segoe UI", 9), bg=c["card"], fg=c["text_secondary"]).pack(side="right" if self.lang == "ar" else "left", padx=(0, 15))

        if task["due_date"]:
            tk.Label(details, text=f"📅 {task['due_date']}",
                     font=("Segoe UI", 9), bg=c["card"], fg=c["text_secondary"]).pack(side="right" if self.lang == "ar" else "left", padx=(0, 15))

        status_text = self.t("completed") if completed else self.t("pending")
        status_color = c["success"] if completed else c["warning"]
        tk.Label(details, text=f"● {status_text}", font=("Segoe UI", 9, "bold"),
                 bg=c["card"], fg=status_color).pack(side="right" if self.lang == "ar" else "left")

        # أزرار العمليات
        actions = tk.Frame(card, bg=c["card"])
        actions.pack(side="right", padx=15, pady=10)

        def abtn(text, color, cmd):
            b = tk.Button(actions, text=text, font=("Segoe UI", 9, "bold"),
                          bg=c["card"], fg=color, relief="flat", cursor="hand2",
                          command=cmd, bd=0, padx=6, pady=3)
            b.pack(side="top", pady=2, fill="x")
            b.bind("<Enter>", lambda e: b.config(bg=color, fg="white"))
            b.bind("<Leave>", lambda e: b.config(bg=c["card"], fg=color))
            return b

        abtn("✓" if not completed else "↺", c["success"],
             lambda t=task: self.toggle_task(t["id"]))
        abtn("✎", c["primary"], lambda t=task: self.show_edit_task_dialog(t))
        abtn("🗑", c["danger"], lambda t=task: self.delete_task(t["id"]))

    def toggle_task(self, task_id):
        self.db.toggle_task_status(task_id)
        self.load_tasks()

    def delete_task(self, task_id):
        if messagebox.askyesno(self.t("confirm_delete"), self.t("confirm_delete")):
            self.db.delete_task(task_id)
            self.load_tasks()

    def show_add_task_dialog(self):
        self._task_dialog()

    def show_edit_task_dialog(self, task):
        self._task_dialog(task)

    def _task_dialog(self, task=None):
        c = self.colors
        is_edit = task is not None

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("edit_task") if is_edit else self.t("add_task"))
        dlg.geometry("480x520")
        dlg.configure(bg=c["bg"])
        dlg.transient(self.root)
        dlg.grab_set()

        # توسيط
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() - 480) // 2
        y = (dlg.winfo_screenheight() - 520) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text=self.t("edit_task") if is_edit else self.t("add_task"),
                 font=("Segoe UI", 16, "bold"), bg=c["bg"], fg=c["text"]).pack(pady=15)

        form = tk.Frame(dlg, bg=c["bg"])
        form.pack(fill="both", expand=True, padx=25)

        def add_entry(label, initial=""):
            tk.Label(form, text=label, font=("Segoe UI", 10),
                     bg=c["bg"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", pady=(5, 3))
            e = tk.Entry(form, font=("Segoe UI", 11), bg=c["entry_bg"], fg=c["text"],
                         insertbackground=c["text"], relief="flat",
                         highlightthickness=1, highlightbackground=c["border"],
                         highlightcolor=c["primary"])
            e.pack(fill="x", ipady=6)
            if initial:
                e.insert(0, initial)
            return e

        title_e = add_entry(self.t("task_title"), task["title"] if is_edit else "")

        tk.Label(form, text=self.t("task_desc"), font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", pady=(10, 3))
        desc_t = tk.Text(form, height=4, font=("Segoe UI", 10), bg=c["entry_bg"], fg=c["text"],
                         insertbackground=c["text"], relief="flat", wrap="word",
                         highlightthickness=1, highlightbackground=c["border"],
                         highlightcolor=c["primary"])
        desc_t.pack(fill="x")
        if is_edit and task["description"]:
            desc_t.insert("1.0", task["description"])

        tk.Label(form, text=self.t("priority"), font=("Segoe UI", 10),
                 bg=c["bg"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", pady=(10, 3))
        prio_var = tk.StringVar(value=task["priority"] if is_edit else "medium")
        prio_frame = tk.Frame(form, bg=c["bg"])
        prio_frame.pack(anchor="e" if self.lang == "ar" else "w")
        for val, label in [("low", self.t("low")),
                           ("medium", self.t("medium")),
                           ("high", self.t("high"))]:
            tk.Radiobutton(prio_frame, text=label, variable=prio_var, value=val,
                           font=("Segoe UI", 10), bg=c["bg"], fg=c["text"],
                           selectcolor=c["card"], activebackground=c["bg"],
                           activeforeground=c["text"], cursor="hand2").pack(side="left", padx=5)

        due_e = add_entry(self.t("due_date"),
                          task["due_date"] if is_edit and task["due_date"] else "")

        def save():
            title = title_e.get().strip()
            if not title:
                messagebox.showwarning(self.t("error"), self.t("title_required"))
                return
            desc = desc_t.get("1.0", "end").strip()
            prio = prio_var.get()
            due = due_e.get().strip()

            if is_edit:
                self.db.update_task(task["id"], title, desc, prio, due)
            else:
                self.db.add_task(self.current_user["id"], title, desc, prio, due)
            dlg.destroy()
            self.load_tasks()

        btn_frame = tk.Frame(dlg, bg=c["bg"])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text=self.t("save"), font=("Segoe UI", 11, "bold"),
                  bg=c["primary"], fg="white", relief="flat", cursor="hand2",
                  command=save, bd=0, padx=25, pady=7).pack(side="left", padx=5)
        tk.Button(btn_frame, text=self.t("cancel"), font=("Segoe UI", 11),
                  bg=c["border"], fg=c["text"], relief="flat", cursor="hand2",
                  command=dlg.destroy, bd=0, padx=25, pady=7).pack(side="left", padx=5)

    def do_logout(self):
        self.current_user = None
        self.show_login()

    # ============================================================
    # ============ 4. واجهة الإعدادات ============================
    # ============================================================
    def show_settings(self):
        self.clear_root()
        self.refresh_theme()
        c = self.colors

        # شريط علوي بسيط
        header = tk.Frame(self.root, bg=c["header"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"⚙ {self.t('account_settings')}",
                 font=("Segoe UI", 16, "bold"),
                 bg=c["header"], fg=c["header_text"]).pack(side="left", padx=20)
        tk.Button(header, text=f"← {self.t('back_to_login')}",
                  font=("Segoe UI", 10), bg=c["header"], fg=c["header_text"],
                  relief="flat", cursor="hand2", command=self.show_main, bd=0).pack(side="right", padx=20)

        body = tk.Frame(self.root, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=30, pady=25)

        # بطاقة الملف الشخصي
        profile_card = tk.Frame(body, bg=c["card"], highlightbackground=c["border"], highlightthickness=1)
        profile_card.pack(fill="x", pady=(0, 20))

        tk.Label(profile_card, text="👤", font=("Segoe UI", 36),
                 bg=c["card"], fg=c["primary"]).pack(pady=(20, 5))
        tk.Label(profile_card, text=self.current_user["username"],
                 font=("Segoe UI", 14, "bold"), bg=c["card"], fg=c["text"]).pack()

        tk.Label(profile_card, text=self.t("full_name"), font=("Segoe UI", 10),
                 bg=c["card"], fg=c["text_secondary"]).pack(pady=(15, 3))
        self.fn_entry = tk.Entry(profile_card, font=("Segoe UI", 11), bg=c["entry_bg"],
                                  fg=c["text"], insertbackground=c["text"], relief="flat",
                                  highlightthickness=1, highlightbackground=c["border"],
                                  highlightcolor=c["primary"], width=30, justify="center")
        self.fn_entry.pack(pady=(0, 12), ipady=6)
        self.fn_entry.insert(0, self.current_user.get("full_name") or "")

        def save_profile():
            name = self.fn_entry.get().strip()
            self.db.update_user(self.current_user["id"], full_name=name)
            self.current_user["full_name"] = name
            messagebox.showinfo(self.t("success"), self.t("updated"))

        tk.Button(profile_card, text=self.t("update_profile"),
                  font=("Segoe UI", 10, "bold"),
                  bg=c["primary"], fg="white", relief="flat", cursor="hand2",
                  command=save_profile, bd=0, padx=20, pady=6).pack(pady=(0, 20))

        # بطاقة المظهر واللغة
        prefs_card = tk.Frame(body, bg=c["card"], highlightbackground=c["border"], highlightthickness=1)
        prefs_card.pack(fill="x", pady=(0, 20))

        row1 = tk.Frame(prefs_card, bg=c["card"])
        row1.pack(fill="x", padx=25, pady=15)
        tk.Label(row1, text=self.t("theme"), font=("Segoe UI", 11, "bold"),
                 bg=c["card"], fg=c["text"]).pack(side="right" if self.lang == "ar" else "left")
        theme_frame = tk.Frame(row1, bg=c["card"])
        theme_frame.pack(side="left" if self.lang == "ar" else "right")
        tk.Button(theme_frame, text=f"☀ {self.t('light')}", font=("Segoe UI", 10),
                  bg=c["card"] if self.theme != "light" else c["primary"],
                  fg=c["text"] if self.theme != "light" else "white",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=5,
                  command=lambda: self._set_theme("light")).pack(side="left", padx=3)
        tk.Button(theme_frame, text=f"🌙 {self.t('dark')}", font=("Segoe UI", 10),
                  bg=c["card"] if self.theme != "dark" else c["primary"],
                  fg=c["text"] if self.theme != "dark" else "white",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=5,
                  command=lambda: self._set_theme("dark")).pack(side="left", padx=3)

        row2 = tk.Frame(prefs_card, bg=c["card"])
        row2.pack(fill="x", padx=25, pady=(0, 15))
        tk.Label(row2, text=self.t("language"), font=("Segoe UI", 11, "bold"),
                 bg=c["card"], fg=c["text"]).pack(side="right" if self.lang == "ar" else "left")
        lang_frame = tk.Frame(row2, bg=c["card"])
        lang_frame.pack(side="left" if self.lang == "ar" else "right")
        tk.Button(lang_frame, text=self.t("arabic"), font=("Segoe UI", 10),
                  bg=c["card"] if self.lang != "ar" else c["primary"],
                  fg=c["text"] if self.lang != "ar" else "white",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=5,
                  command=lambda: self._set_lang("ar")).pack(side="left", padx=3)
        tk.Button(lang_frame, text=self.t("english"), font=("Segoe UI", 10),
                  bg=c["card"] if self.lang != "en" else c["primary"],
                  fg=c["text"] if self.lang != "en" else "white",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=5,
                  command=lambda: self._set_lang("en")).pack(side="left", padx=3)

        # بطاقة تغيير كلمة المرور
        pass_card = tk.Frame(body, bg=c["card"], highlightbackground=c["border"], highlightthickness=1)
        pass_card.pack(fill="x")

        tk.Label(pass_card, text=self.t("change_password"),
                 font=("Segoe UI", 12, "bold"), bg=c["card"], fg=c["text"]).pack(pady=(15, 10))

        def pass_field(label):
            tk.Label(pass_card, text=label, font=("Segoe UI", 10),
                     bg=c["card"], fg=c["text"]).pack(anchor="e" if self.lang == "ar" else "w", padx=30)
            e = tk.Entry(pass_card, font=("Segoe UI", 11), show="●", bg=c["entry_bg"],
                         fg=c["text"], insertbackground=c["text"], relief="flat",
                         highlightthickness=1, highlightbackground=c["border"],
                         highlightcolor=c["primary"], width=30)
            e.pack(pady=(3, 10), ipady=5)
            return e

        old_e = pass_field(self.t("old_password"))
        new_e = pass_field(self.t("new_password"))

        def do_change_pass():
            old = old_e.get().strip()
            new = new_e.get().strip()
            if not old or not new:
                messagebox.showwarning(self.t("error"), self.t("fill_fields"))
                return
            if self.db.change_password(self.current_user["id"], old, new):
                messagebox.showinfo(self.t("success"), self.t("updated"))
                old_e.delete(0, "end")
                new_e.delete(0, "end")
            else:
                messagebox.showerror(self.t("error"), self.t("wrong_old_password"))

        tk.Button(pass_card, text=self.t("save"), font=("Segoe UI", 10, "bold"),
                  bg=c["primary"], fg="white", relief="flat", cursor="hand2",
                  command=do_change_pass, bd=0, padx=20, pady=6).pack(pady=(0, 20))

    def _set_theme(self, th):
        self.theme = th
        self.refresh_theme()
        self.db.update_user(self.current_user["id"], theme=th)
        self.current_user["theme"] = th
        self.show_settings()

    def _set_lang(self, lang):
        self.lang = lang
        self.db.update_user(self.current_user["id"], language=lang)
        self.current_user["language"] = lang
        self.show_settings()

    # ============================================================
    # ============ 5. واجهة التقارير =============================
    # ============================================================
    def show_reports(self):
        self.clear_root()
        self.refresh_theme()
        c = self.colors

        header = tk.Frame(self.root, bg=c["header"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"📊 {self.t('reports_title')}",
                 font=("Segoe UI", 16, "bold"),
                 bg=c["header"], fg=c["header_text"]).pack(side="left", padx=20)
        tk.Button(header, text=f"← {self.t('back_to_login')}",
                  font=("Segoe UI", 10), bg=c["header"], fg=c["header_text"],
                  relief="flat", cursor="hand2", command=self.show_main, bd=0).pack(side="right", padx=20)

        stats = self.db.get_stats(self.current_user["id"])

        body = tk.Frame(self.root, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=25, pady=20)

        # بطاقات الإحصاء
        cards_frame = tk.Frame(body, bg=c["bg"])
        cards_frame.pack(fill="x", pady=(0, 20))

        def stat_card(parent, label, value, color):
            card = tk.Frame(parent, bg=c["card"], highlightbackground=c["border"],
                            highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(card, text=label, font=("Segoe UI", 10),
                     bg=c["card"], fg=c["text_secondary"]).pack(pady=(15, 5))
            tk.Label(card, text=str(value), font=("Segoe UI", 26, "bold"),
                     bg=c["card"], fg=color).pack(pady=(0, 15))

        stat_card(cards_frame, self.t("total_tasks"), stats["total"], c["primary"])
        stat_card(cards_frame, self.t("completed_tasks"), stats["completed"], c["success"])
        stat_card(cards_frame, self.t("pending_tasks"), stats["pending"], c["warning"])

        # الرسم البياني (بالأشرطة)
        chart_card = tk.Frame(body, bg=c["card"], highlightbackground=c["border"],
                              highlightthickness=1)
        chart_card.pack(fill="both", expand=True)

        tk.Label(chart_card, text=self.t("priority_distribution"),
                 font=("Segoe UI", 13, "bold"), bg=c["card"], fg=c["text"]).pack(pady=15)

        chart_canvas = tk.Canvas(chart_card, bg=c["card"], height=280,
                                  highlightthickness=0)
        chart_canvas.pack(fill="both", expand=True, padx=30, pady=10)

        # رسم الأشرطة
        prios = [
            ("high", c["danger"]),
            ("medium", c["warning"]),
            ("low", c["success"]),
        ]
        max_val = max(stats["priority"].values()) if stats["priority"] else 1
        if max_val == 0:
            max_val = 1

        chart_canvas.update_idletasks()
        width = 800
        bar_h = 40
        gap = 30
        start_y = 30

        for i, (p, color) in enumerate(prios):
            val = stats["priority"].get(p, 0)
            y = start_y + i * (bar_h + gap)

            # التسمية
            chart_canvas.create_text(20, y + bar_h // 2, text=self.t(p),
                                      anchor="w", font=("Segoe UI", 11, "bold"),
                                      fill=c["text"])
            # الخلفية
            chart_canvas.create_rectangle(120, y, 720, y + bar_h,
                                            fill=c["border"], outline="")
            # الشريط
            bar_w = (val / max_val) * 600 if max_val else 0
            if bar_w > 0:
                chart_canvas.create_rectangle(120, y, 120 + bar_w, y + bar_h,
                                                fill=color, outline="")
            # القيمة
            chart_canvas.create_text(730, y + bar_h // 2, text=str(val),
                                      anchor="w", font=("Segoe UI", 11, "bold"),
                                      fill=c["text"])

        # نسبة الإنجاز
        rate = (stats["completed"] / stats["total"] * 100) if stats["total"] else 0
        rate_frame = tk.Frame(chart_card, bg=c["card"])
        rate_frame.pack(fill="x", padx=30, pady=(0, 20))

        tk.Label(rate_frame, text=f"{self.t('completion_rate')}: {rate:.1f}%",
                 font=("Segoe UI", 12, "bold"), bg=c["card"], fg=c["primary"]).pack(side="right" if self.lang == "ar" else "left")

        # شريط التقدم
        progress_bg = tk.Frame(rate_frame, bg=c["border"], height=14)
        progress_bg.pack(side="left" if self.lang == "ar" else "right", fill="x", expand=True, padx=15)
        progress_bg.pack_propagate(False)
        if rate > 0:
            tk.Frame(progress_bg, bg=c["success"], height=14).place(
                relwidth=rate / 100, relheight=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
