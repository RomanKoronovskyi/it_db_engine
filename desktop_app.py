import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from core import DataType, Table
from storage import Database

class DesktopApp(tk.Tk):
    COLOR_BG = "#F8FAFC"
    COLOR_CARD = "#FFFFFF"
    COLOR_BORDER = "#E2E8F0"
    COLOR_PRIMARY = "#2563EB"
    COLOR_DANGER = "#DC2626"
    COLOR_TEXT = "#0F172A"
    COLOR_MUTED = "#64748B"

    def __init__(self):
        super().__init__()
        self.title("Таблична СУБД")
        self.geometry("1100x680")
        self.minsize(850, 520)
        self.configure(bg=self.COLOR_BG)

        self.db: Database = Database("EnterpriseDB")
        self.current_table_name: str = ""

        self._configure_styles()
        self._init_ui()

    def _configure_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background=self.COLOR_BG, foreground=self.COLOR_TEXT, font=("Segoe UI", 9))
        self.style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")

        self.style.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.COLOR_TEXT,
            font=("Segoe UI", 9),
            rowheight=28,
            borderwidth=1,
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", self.COLOR_PRIMARY)], foreground=[("selected", "#FFFFFF")])

        self.style.configure(
            "Treeview.Heading",
            background="#EDF2F7",
            foreground="#334155",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(6, 6)
        )
        self.style.map("Treeview.Heading", background=[("active", "#E2E8F0")])

        self.style.configure("Vertical.TScrollbar", gripcount=0, background="#CBD5E1", troughcolor=self.COLOR_BG)

    def _init_ui(self):
        top_bar = tk.Frame(self, bg=self.COLOR_CARD, height=52, padx=16, pady=8, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)

        self._btn(top_bar, "Нова БД", self.action_new_db).pack(side=tk.LEFT, padx=3)
        self._btn(top_bar, "Відкрити JSON", self.action_load_db).pack(side=tk.LEFT, padx=3)
        self._btn(top_bar, "Зберегти JSON", self.action_save_db).pack(side=tk.LEFT, padx=3)

        self.lbl_db_name = tk.Label(
            top_bar,
            text=f"Активна БД: {self.db.name}",
            bg=self.COLOR_CARD,
            fg=self.COLOR_PRIMARY,
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_db_name.pack(side=tk.RIGHT, padx=6)

        body_frame = tk.Frame(self, bg=self.COLOR_BG, padx=12, pady=12)
        body_frame.pack(fill=tk.BOTH, expand=True)

        left_card = tk.Frame(body_frame, bg=self.COLOR_CARD, width=230, padx=10, pady=10, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        left_card.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_card.pack_propagate(False)

        tk.Label(left_card, text="ТАБЛИЦІ", bg=self.COLOR_CARD, fg=self.COLOR_MUTED, font=("Segoe UI", 8, "bold")).pack(anchor=tk.W, pady=(0, 6))

        self.tables_listbox = tk.Listbox(
            left_card,
            bg="#F8FAFC",
            fg=self.COLOR_TEXT,
            selectbackground=self.COLOR_PRIMARY,
            selectforeground="#FFFFFF",
            font=("Segoe UI", 9),
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.COLOR_BORDER,
            activestyle="none"
        )
        self.tables_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.tables_listbox.bind("<<ListboxSelect>>", self.action_on_select_table)

        btn_t_box = tk.Frame(left_card, bg=self.COLOR_CARD)
        btn_t_box.pack(fill=tk.X)
        self._btn(btn_t_box, "+ Таблиця", self.action_create_table, bg="#EEF2FF", fg=self.COLOR_PRIMARY).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self._btn(btn_t_box, "Видалити", self.action_drop_table, bg="#FEE2E2", fg=self.COLOR_DANGER).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        right_card = tk.Frame(body_frame, bg=self.COLOR_CARD, padx=12, pady=12, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        schema_bar = tk.Frame(right_card, bg=self.COLOR_CARD, pady=4)
        schema_bar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(schema_bar, text="Схема та операції:", bg=self.COLOR_CARD, fg=self.COLOR_MUTED, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self._btn(schema_bar, "Додати колонку", self.action_add_column).pack(side=tk.LEFT, padx=3)
        self._btn(schema_bar, "Перейменувати", self.action_rename_column).pack(side=tk.LEFT, padx=3)
        self._btn(schema_bar, "Переставити місцями", self.action_swap_columns, bg="#EEF2FF", fg=self.COLOR_PRIMARY).pack(side=tk.LEFT, padx=3)
        self._btn(schema_bar, "Видалити колонку", self.action_delete_column, bg="#FEE2E2", fg=self.COLOR_DANGER).pack(side=tk.LEFT, padx=3)

        grid_container = tk.Frame(right_card, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        grid_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(grid_container, show="headings", selectmode="browse", style="Treeview")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(grid_container, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        rows_bar = tk.Frame(right_card, bg=self.COLOR_CARD, pady=8)
        rows_bar.pack(fill=tk.X)

        self._btn(rows_bar, "Додати рядок", self.action_add_row, bg=self.COLOR_PRIMARY, fg="#FFFFFF").pack(side=tk.LEFT, padx=(0, 4))
        self._btn(rows_bar, "Редагувати", self.action_edit_row).pack(side=tk.LEFT, padx=3)
        self._btn(rows_bar, "Видалити", self.action_delete_row, bg="#FEE2E2", fg=self.COLOR_DANGER).pack(side=tk.LEFT, padx=3)

    def _btn(self, parent, text, cmd, bg="#F1F5F9", fg="#0F172A"):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=bg,
            fg=fg,
            activebackground="#E2E8F0",
            activeforeground=fg,
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )

    def action_new_db(self):
        name = simpledialog.askstring("Нова БД", "Введіть назву бази даних:")
        if name:
            self.db = Database(name)
            self.current_table_name = ""
            self.lbl_db_name.config(text=f"Активна БД: {self.db.name}")
            self._refresh_tables_list()
            self._render_table_view()

    def action_load_db(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            try:
                self.db = Database.load_from_file(path)
                self.current_table_name = next(iter(self.db.tables)) if self.db.tables else ""
                self.lbl_db_name.config(text=f"Активна БД: {self.db.name}")
                self._refresh_tables_list()
                self._render_table_view()
                messagebox.showinfo("Успіх", "Базу даних завантажено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зчитати файл: {e}")

    def action_save_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            try:
                self.db.save_to_file(path)
                messagebox.showinfo("Успіх", "Базу даних збережено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

    def action_create_table(self):
        name = simpledialog.askstring("Створення таблиці", "Введіть назву нової таблиці:")
        if not name:
            return
        try:
            self.db.create_table(name)
            self.current_table_name = name
            self._refresh_tables_list()
            self._render_table_view()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def action_drop_table(self):
        if not self.current_table_name:
            messagebox.showwarning("Увага", "Оберіть таблицю для видалення.")
            return
        if messagebox.askyesno("Підтвердження", f"Видалити таблицю '{self.current_table_name}'?"):
            self.db.drop_table(self.current_table_name)
            self.current_table_name = next(iter(self.db.tables)) if self.db.tables else ""
            self._refresh_tables_list()
            self._render_table_view()

    def _refresh_tables_list(self):
        self.tables_listbox.delete(0, tk.END)
        for idx, t_name in enumerate(self.db.tables.keys()):
            self.tables_listbox.insert(tk.END, t_name)
            if t_name == self.current_table_name:
                self.tables_listbox.select_set(idx)

    def action_on_select_table(self, event):
        selection = self.tables_listbox.curselection()
        if selection:
            self.current_table_name = self.tables_listbox.get(selection[0])
            self._render_table_view()

    def _render_table_view(self):
        self.tree.delete(*self.tree.get_children())
        table = self.db.get_table(self.current_table_name)
        if not table:
            self.tree["columns"] = ()
            return

        col_ids = [str(i) for i in range(len(table.columns))]
        self.tree["columns"] = col_ids

        for idx, col in enumerate(table.columns):
            self.tree.heading(str(idx), text=f"{col.name} ({col.data_type.value})")
            self.tree.column(str(idx), width=130, anchor=tk.CENTER)

        for row in table.rows:
            self.tree.insert("", tk.END, iid=row.id, values=row.values)

    def action_add_column(self):
        table = self.db.get_table(self.current_table_name)
        if not table:
            messagebox.showwarning("Увага", "Спочатку оберіть або створіть таблицю")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Додати колонку")
        dialog.geometry("320x170")
        dialog.configure(bg=self.COLOR_CARD)

        tk.Label(dialog, text="Назва стовпця:", bg=self.COLOR_CARD).pack(pady=(10, 2))
        name_entry = tk.Entry(dialog, relief="solid", bd=1)
        name_entry.pack(fill=tk.X, padx=20)

        tk.Label(dialog, text="Тип даних:", bg=self.COLOR_CARD).pack(pady=(6, 2))
        type_cb = ttk.Combobox(dialog, values=[dt.value for dt in DataType], state="readonly")
        type_cb.current(0)
        type_cb.pack(fill=tk.X, padx=20)

        def submit():
            col_name = name_entry.get().strip()
            if not col_name:
                messagebox.showerror("Помилка", "Назва не може бути порожньою")
                return
            try:
                table.add_column(col_name, DataType(type_cb.get()))
                dialog.destroy()
                self._render_table_view()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        self._btn(dialog, "Зберегти", submit, bg=self.COLOR_PRIMARY, fg="#FFFFFF").pack(pady=12)

    def action_rename_column(self):
        table = self.db.get_table(self.current_table_name)
        if not table or not table.columns:
            messagebox.showwarning("Увага", "У таблиці немає колонок")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Перейменувати колонку")
        dialog.geometry("320x170")
        dialog.configure(bg=self.COLOR_CARD)

        col_names = [f"{idx}: {col.name}" for idx, col in enumerate(table.columns)]
        tk.Label(dialog, text="Оберіть колонку:", bg=self.COLOR_CARD).pack(pady=(10, 2))
        col_cb = ttk.Combobox(dialog, values=col_names, state="readonly")
        col_cb.current(0)
        col_cb.pack(fill=tk.X, padx=20)

        tk.Label(dialog, text="Нова назва:", bg=self.COLOR_CARD).pack(pady=(6, 2))
        name_entry = tk.Entry(dialog, relief="solid", bd=1)
        name_entry.pack(fill=tk.X, padx=20)

        def submit():
            new_name = name_entry.get().strip()
            try:
                table.rename_column(col_cb.current(), new_name)
                dialog.destroy()
                self._render_table_view()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        self._btn(dialog, "Застосувати", submit, bg=self.COLOR_PRIMARY, fg="#FFFFFF").pack(pady=12)

    def action_swap_columns(self):
        table = self.db.get_table(self.current_table_name)
        if not table or len(table.columns) < 2:
            messagebox.showwarning("Увага", "Потрібно щонайменше дві колонки для перестановки")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Перестановка колонок")
        dialog.geometry("320x190")
        dialog.configure(bg=self.COLOR_CARD)

        col_names = [f"{idx}: {col.name}" for idx, col in enumerate(table.columns)]

        tk.Label(dialog, text="Колонка 1:", bg=self.COLOR_CARD).pack(pady=(8, 2))
        cb_a = ttk.Combobox(dialog, values=col_names, state="readonly")
        cb_a.current(0)
        cb_a.pack(fill=tk.X, padx=20)

        tk.Label(dialog, text="Колонка 2:", bg=self.COLOR_CARD).pack(pady=(6, 2))
        cb_b = ttk.Combobox(dialog, values=col_names, state="readonly")
        cb_b.current(1)
        cb_b.pack(fill=tk.X, padx=20)

        def submit():
            try:
                table.swap_columns(cb_a.current(), cb_b.current())
                dialog.destroy()
                self._render_table_view()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        self._btn(dialog, "Поміняти місцями", submit, bg=self.COLOR_PRIMARY, fg="#FFFFFF").pack(pady=12)

    def action_delete_column(self):
        table = self.db.get_table(self.current_table_name)
        if not table or not table.columns:
            messagebox.showwarning("Увага", "У таблиці немає колонок")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Видалити колонку")
        dialog.geometry("320x140")
        dialog.configure(bg=self.COLOR_CARD)

        col_names = [f"{idx}: {col.name}" for idx, col in enumerate(table.columns)]
        tk.Label(dialog, text="Оберіть колонку для видалення:", bg=self.COLOR_CARD).pack(pady=(12, 4))
        col_cb = ttk.Combobox(dialog, values=col_names, state="readonly")
        col_cb.current(0)
        col_cb.pack(fill=tk.X, padx=20)

        def submit():
            try:
                table.delete_column(col_cb.current())
                dialog.destroy()
                self._render_table_view()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        self._btn(dialog, "Видалити", submit, bg=self.COLOR_DANGER, fg="#FFFFFF").pack(pady=14)

    def action_add_row(self):
        table = self.db.get_table(self.current_table_name)
        if not table or not table.columns:
            messagebox.showwarning("Увага", "Спочатку додайте колонки")
            return
        self._show_row_form(table, title="Додати запис")

    def action_edit_row(self):
        table = self.db.get_table(self.current_table_name)
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть рядок для редагування")
            return
        row = next((r for r in table.rows if r.id == selected[0]), None)
        if row:
            self._show_row_form(table, title="Редагувати запис", existing_row=row)

    def action_delete_row(self):
        table = self.db.get_table(self.current_table_name)
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть рядок для видалення")
            return
        table.delete_row(selected[0])
        self._render_table_view()

    def _show_row_form(self, table: Table, title: str, existing_row=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=self.COLOR_CARD)
        entries = []

        for idx, col in enumerate(table.columns):
            row_frame = tk.Frame(dialog, bg=self.COLOR_CARD)
            row_frame.pack(fill=tk.X, padx=14, pady=4)

            hint = " (HH:MM:SS-HH:MM:SS)" if col.data_type == DataType.TIME_INVL else ""
            lbl_text = f"{col.name} [{col.data_type.value}]{hint}:"
            tk.Label(row_frame, text=lbl_text, width=24, anchor=tk.W, bg=self.COLOR_CARD, font=("Segoe UI", 9)).pack(side=tk.LEFT)

            entry = tk.Entry(row_frame, relief="solid", bd=1)
            if existing_row:
                entry.insert(0, str(existing_row.values[idx]))
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entries.append(entry)

        def submit():
            raw_vals = [e.get() for e in entries]
            try:
                if existing_row:
                    table.update_row_values(existing_row.id, raw_vals)
                else:
                    table.add_row(raw_vals)
                dialog.destroy()
                self._render_table_view()
            except Exception as e:
                messagebox.showerror("Помилка валідації", str(e))

        self._btn(dialog, "Підтвердити", submit, bg=self.COLOR_PRIMARY, fg="#FFFFFF").pack(pady=12)