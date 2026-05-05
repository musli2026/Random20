import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# Предопределённые задачи
DEFAULT_TASKS = [
    {"text": "Прочитать статью по истории", "category": "учёба"},
    {"text": "Сделать зарядку 10 минут", "category": "спорт"},
    {"text": "Выполнить задачу по работе", "category": "работа"},
    {"text": "Изучить тему по математике", "category": "учёба"},
    {"text": "Отжаться 20 раз", "category": "спорт"},
    {"text": "Написать отчёт", "category": "работа"},
    {"text": "Посмотреть видеоурок", "category": "учёба"},
    {"text": "Пробежка", "category": "спорт"},
    {"text": "Планирование задач на день", "category": "работа"}
]

class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Данные
        self.history = []          # Каждый элемент: {"task": "...", "category": "...", "time": "..."}
        self.categories = ["все", "учёба", "спорт", "работа"]

        # Загрузка истории из JSON
        self.load_history()

        # Интерфейс
        self.create_widgets()

        # Обновление отображения истории
        self.refresh_history_display()

    def create_widgets(self):
        # Рамка для генерации
        frame_gen = tk.LabelFrame(self.root, text="Генератор задач", padx=10, pady=10)
        frame_gen.pack(fill="x", padx=10, pady=5)

        self.btn_generate = tk.Button(frame_gen, text="🎲 Сгенерировать задачу", command=self.generate_task, 
                                      font=("Arial", 12), bg="#4CAF50", fg="white")
        self.btn_generate.pack(pady=5)

        self.lbl_task = tk.Label(frame_gen, text="Нажмите кнопку, чтобы получить задачу", 
                                 font=("Arial", 11), wraplength=550)
        self.lbl_task.pack(pady=5)

        # Рамка для добавления новой задачи
        frame_add = tk.LabelFrame(self.root, text="Добавить новую задачу", padx=10, pady=10)
        frame_add.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_add, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_task = tk.Entry(frame_add, width=40)
        self.entry_task.grid(row=0, column=1, padx=5)

        tk.Label(frame_add, text="Категория:").grid(row=1, column=0, sticky="w")
        self.combo_category = ttk.Combobox(frame_add, values=["учёба", "спорт", "работа"], state="readonly")
        self.combo_category.grid(row=1, column=1, padx=5, pady=5)
        self.combo_category.current(0)

        self.btn_add = tk.Button(frame_add, text="➕ Добавить задачу", command=self.add_task, bg="#2196F3", fg="white")
        self.btn_add.grid(row=2, column=1, pady=5, sticky="e")

        # Рамка для фильтрации
        frame_filter = tk.LabelFrame(self.root, text="Фильтрация истории", padx=10, pady=10)
        frame_filter.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_filter, text="Фильтр по категории:").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="все")
        self.filter_menu = ttk.Combobox(frame_filter, textvariable=self.filter_var, values=self.categories, state="readonly")
        self.filter_menu.pack(side="left", padx=5)
        self.filter_menu.bind("«ComboboxSelected»", lambda e: self.refresh_history_display())

        # История
        frame_history = tk.LabelFrame(self.root, text="История задач", padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(frame_history)
        scrollbar.pack(side="right", fill="y")

        self.listbox_history = tk.Listbox(frame_history, yscrollcommand=scrollbar.set, font=("Courier", 9))
        self.listbox_history.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_history.yview)

        # Кнопка очистки истории
        self.btn_clear = tk.Button(self.root, text="🗑️ Очистить историю", command=self.clear_history, bg="#f44336", fg="white")
        self.btn_clear.pack(pady=5)

    def generate_task(self):
        """Выбирает случайную задачу из предопределённого списка и сохраняет в историю."""
        if not DEFAULT_TASKS:
            messagebox.showwarning("Нет задач", "Список задач пуст. Добавьте хотя бы одну задачу.")
            return

        task = random.choice(DEFAULT_TASKS)
        task_text = task["text"]
        category = task["category"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.history.append({
            "task": task_text,
            "category": category,
            "time": timestamp
        })
        self.save_history()
        self.refresh_history_display()
        self.lbl_task.config(text=f"✅ Текущая задача: {task_text} (категория: {category})")

    def add_task(self):
        """Добавляет новую задачу в предопределённый список с проверкой ввода."""
        task_text = self.entry_task.get().strip()
        category = self.combo_category.get()

        if not task_text:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return

        DEFAULT_TASKS.append({"text": task_text, "category": category})
        self.entry_task.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача «{task_text}» добавлена в список!")

    def refresh_history_display(self):
        """Обновляет список истории с учётом фильтра."""
        self.listbox_history.delete(0, tk.END)
        
        selected_filter = self.filter_var.get()
        
        for item in self.history:
            if selected_filter == "все" or item["category"] == selected_filter:
                display_text = f"[{item['time']}] {item['task']} ({item['category']})"
                self.listbox_history.insert(tk.END, display_text)

    def save_history(self):
        """Сохраняет историю в JSON-файл."""
        try:
            with open("tasks_data.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_history(self):
        """Загружает историю из JSON-файла."""
        if os.path.exists("tasks_data.json"):
            try:
                with open("tasks_data.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def clear_history(self):
        """Очищает всю историю после подтверждения."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_display()
            self.lbl_task.config(text="История очищена")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()