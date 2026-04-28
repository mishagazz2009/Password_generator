import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Путь к файлу истории
        self.history_file = "password_history.json"
        
        # Загрузка истории
        self.history = self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="Генератор случайных паролей", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Фрейм для настроек
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=10, pady=10)
        settings_frame.pack(padx=20, pady=10, fill="x")
        
        # Ползунок длины пароля
        length_frame = tk.Frame(settings_frame)
        length_frame.pack(fill="x", pady=5)
        
        tk.Label(length_frame, text="Длина пароля:").pack(side="left")
        
        self.length_var = tk.IntVar(value=12)
        self.length_label = tk.Label(length_frame, text="12", width=3)
        self.length_label.pack(side="right")
        
        self.length_scale = tk.Scale(
            length_frame, 
            from_=4, 
            to=32, 
            orient="horizontal",
            variable=self.length_var,
            command=self.update_length_label
        )
        self.length_scale.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Чекбоксы для выбора символов
        checkboxes_frame = tk.Frame(settings_frame)
        checkboxes_frame.pack(fill="x", pady=10)
        
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Заглавные буквы (A-Z)", 
            variable=self.use_uppercase
        ).pack(anchor="w")
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Строчные буквы (a-z)", 
            variable=self.use_lowercase
        ).pack(anchor="w")
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Цифры (0-9)", 
            variable=self.use_digits
        ).pack(anchor="w")
        
        tk.Checkbutton(
            checkboxes_frame, 
            text="Специальные символы (!@#$%^&*)", 
            variable=self.use_special
        ).pack(anchor="w")
        
        # Фрейм для отображения сгенерированного пароля
        password_frame = tk.Frame(settings_frame)
        password_frame.pack(fill="x", pady=10)
        
        tk.Label(password_frame, text="Сгенерированный пароль:").pack(anchor="w")
        
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            password_frame, 
            textvariable=self.password_var, 
            font=("Courier", 12),
            state="readonly",
            readonlybackground="white"
        )
        password_entry.pack(fill="x", pady=(5, 0))
        
        # Кнопки
        buttons_frame = tk.Frame(settings_frame)
        buttons_frame.pack(fill="x", pady=5)
        
        generate_btn = tk.Button(
            buttons_frame,
            text="Сгенерировать пароль",
            command=self.generate_password,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2
        )
        generate_btn.pack(side="left", padx=(0, 5))
        
        copy_btn = tk.Button(
            buttons_frame,
            text="Копировать",
            command=self.copy_to_clipboard,
            bg="#2196F3",
            fg="white",
            height=2
        )
        copy_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Сохранить в историю",
            command=self.save_to_history,
            bg="#FF9800",
            fg="white",
            height=2
        )
        save_btn.pack(side="left", padx=5)
        
        # Фрейм для таблицы истории
        history_frame = tk.LabelFrame(self.root, text="История паролей", padx=10, pady=10)
        history_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Таблица истории
        columns = ("Дата", "Пароль", "Длина")
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=columns, 
            show="headings",
            height=8
        )
        
        self.history_tree.heading("Дата", text="Дата создания")
        self.history_tree.heading("Пароль", text="Пароль")
        self.history_tree.heading("Длина", text="Длина")
        
        self.history_tree.column("Дата", width=150)
        self.history_tree.column("Пароль", width=300)
        self.history_tree.column("Длина", width=80)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления историей
        history_buttons_frame = tk.Frame(self.root)
        history_buttons_frame.pack(pady=10)
        
        copy_history_btn = tk.Button(
            history_buttons_frame,
            text="Копировать выбранный",
            command=self.copy_selected,
            bg="#9C27B0",
            fg="white"
        )
        copy_history_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(
            history_buttons_frame,
            text="Удалить выбранный",
            command=self.delete_selected,
            bg="#F44336",
            fg="white"
        )
        delete_btn.pack(side="left", padx=5)
        
        clear_history_btn = tk.Button(
            history_buttons_frame,
            text="Очистить историю",
            command=self.clear_history,
            bg="#607D8B",
            fg="white"
        )
        clear_history_btn.pack(side="left", padx=5)
        
        # Обновление таблицы истории
        self.update_history_table()
        
    def update_length_label(self, value):
        """Обновляет метку с текущей длиной пароля"""
        self.length_label.config(text=str(int(float(value))))
        
    def generate_password(self):
        """Генерирует случайный пароль на основе выбранных параметров"""
        # Проверка, что выбран хотя бы один тип символов
        if not any([
            self.use_uppercase.get(), 
            self.use_lowercase.get(),
            self.use_digits.get(), 
            self.use_special.get()
        ]):
            messagebox.showwarning(
                "Предупреждение", 
                "Выберите хотя бы один тип символов для пароля!"
            )
            return
        
        # Сбор доступных символов
        characters = ""
        
        if self.use_uppercase.get():
            characters += string.ascii_uppercase
        if self.use_lowercase.get():
            characters += string.ascii_lowercase
        if self.use_digits.get():
            characters += string.digits
        if self.use_special.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Генерация пароля
        length = self.length_var.get()
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Проверка, что пароль содержит все выбранные типы символов
        if self.use_uppercase.get() and not any(c.isupper() for c in password):
            password = self.ensure_char_type(password, string.ascii_uppercase)
        if self.use_lowercase.get() and not any(c.islower() for c in password):
            password = self.ensure_char_type(password, string.ascii_lowercase)
        if self.use_digits.get() and not any(c.isdigit() for c in password):
            password = self.ensure_char_type(password, string.digits)
        if self.use_special.get() and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            password = self.ensure_char_type(password, "!@#$%^&*()_+-=[]{}|;:,.<>?")
        
        self.password_var.set(password)
        
    def ensure_char_type(self, password, char_set):
        """Гарантирует наличие символов определенного типа в пароле"""
        password_list = list(password)
        random_pos = random.randint(0, len(password) - 1)
        password_list[random_pos] = random.choice(char_set)
        return ''.join(password_list)
        
    def copy_to_clipboard(self):
        """Копирует сгенерированный пароль в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()  # Важно для работы с буфером обмена
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль!")
            
    def save_to_history(self):
        """Сохраняет сгенерированный пароль в историю"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль!")
            return
            
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": len(password)
        }
        
        self.history.append(entry)
        self.save_history_to_file()
        self.update_history_table()
        messagebox.showinfo("Успех", "Пароль сохранен в историю!")
        
    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history if isinstance(history, list) else []
            except (json.JSONDecodeError, IOError):
                return []
        return []
        
    def save_history_to_file(self):
        """Сохраняет историю в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
            
    def update_history_table(self):
        """Обновляет таблицу истории"""
        # Очистка текущей таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Добавление записей из истории (в обратном порядке)
        for entry in reversed(self.history):
            self.history_tree.insert(
                "", 
                "end", 
                values=(entry["date"], entry["password"], entry["length"])
            )
            
    def copy_selected(self):
        """Копирует выбранный пароль из истории в буфер обмена"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль в таблице!")
            return
            
        item = self.history_tree.item(selected[0])
        password = item['values'][1]
        
        # Используем встроенный буфер обмена tkinter
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        
    def delete_selected(self):
        """Удаляет выбранный пароль из истории"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль в таблице!")
            return
            
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Удалить выбранный пароль из истории?"):
            # Получение индекса выбранного элемента
            item = self.history_tree.item(selected[0])
            values = item['values']
            
            # Поиск и удаление записи из списка истории
            for i, entry in enumerate(self.history):
                if (entry["date"] == values[0] and 
                    entry["password"] == values[1]):
                    del self.history[i]
                    break
                    
            self.save_history_to_file()
            self.update_history_table()
            
    def clear_history(self):
        """Очищает всю историю паролей"""
        if not self.history:
            messagebox.showinfo("Информация", "История уже пуста!")
            return
            
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history = []
            self.save_history_to_file()
            self.update_history_table()
            messagebox.showinfo("Успех", "История очищена!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()