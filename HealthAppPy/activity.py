import json
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Налаштування теми CustomTkinter
ctk.set_appearance_mode("light")  # Світла тема
ctk.set_default_color_theme("green")  # Зелена колірна схема

class ActivityTrackerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("My Activity")
        self.root.geometry("636x402")
        self.root.configure(bg="#E6E4E4")

        self.selected_button = None
        self.nav_buttons = {}
        self.user = User()  # Assuming you have a User class
        self.activity = Activity(self.user)

        self.create_sidebar()
        self.create_header()
        self.create_main_content()

        self.on_nav_click("Activity")  # Default selected menu item

    def create_header(self):
        header = tk.Frame(self.root, bg="#58C75C", height=47, width=493)
        header.pack_propagate(False)  # Забороняє зміну розміру
        header.pack(side='top', anchor='ne')  # Вирівнюємо праворуч з відступами

        title = tk.Label(
            header,
            text="My activity",
            font=("Helvetica", 20, "bold"),
            bg="#58C75C",
            fg="white"
        )
        title.pack(pady=10)

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.root, fg_color="#C8C8C8", width=143, height=402)
        sidebar.pack(side="left")
        sidebar.pack_propagate(False)


        menu_items = {
            "Profile": "👤",
            "Nutrition": "🍴",
            "Activity": "🏃",
            "CalorieC": "📊",
            "Reg_Win": "📝",
            "Help": "❓"
        }

        for name, icon in menu_items.items():
            btn = tk.Button(
                sidebar,
                text=f"  {icon}  {name}",
                anchor="w",
                justify="left",
                font=("Arial", 10),
                bg="#c4c4c4",
                fg="black",
                bd=0,
                padx=10,
                pady=8,
                activebackground="#8d8989",
                command=lambda n=name: self.on_nav_click(n)
            )
            btn.pack(fill=tk.X)
            self.nav_buttons[name] = btn


    def create_main_content(self):
        self.main_frame = tk.Frame(self.root, bg="#E6E4E4")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Створюємо контейнер для форми та зображення
        top_container = ctk.CTkFrame(self.main_frame, fg_color="#E6E4E4")
        top_container.pack(fill="x", pady=10)

        # Створюємо рамку для форми (ліва частина)
        workout_frame = ctk.CTkFrame(top_container, fg_color="#E6E4E4")
        workout_frame.pack(side="left", fill="both", expand=True, padx=10)

        # Activity selection
        self.activity_var = ctk.StringVar(value="Activity:")
        activities = list(self.activity.activities.keys())
        self.activity_combobox = ctk.CTkComboBox(
            workout_frame,
            variable=self.activity_var,
            values=activities,
            width=120
        )
        self.activity_combobox.grid(row=0, column=0, sticky="ew", padx=5, pady=5, columnspan=2)

        # Додаємо обробник подій для очищення тексту при фокусуванні
        def clear_placeholder(event):
            if self.activity_var.get() == "Activity:":
                self.activity_var.set("")

        def restore_placeholder(event):
            if not self.activity_var.get():
                self.activity_var.set("Activity:")

        self.activity_combobox.bind("<FocusIn>", clear_placeholder)
        self.activity_combobox.bind("<FocusOut>", restore_placeholder)

        # Time entry
        ctk.CTkLabel(workout_frame)
        self.time_entry = ctk.CTkEntry(workout_frame, placeholder_text="Minutes")
        self.time_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Add activity button
        add_btn = ctk.CTkButton(
            workout_frame,
            text="Add Activity",
            command=self.add_activity,
            fg_color="#58C75C",
            hover_color="#4CAF50"
        )
        add_btn.grid(row=2, column=1, columnspan=2, pady=10)

        # Додаємо зображення (права частина)
        try:
            self.photo = tk.PhotoImage(file="running.png")
            # Масштабуємо зображення, якщо потрібно
            self.photo = self.photo.subsample(5, 5)  # Зменшуємо в 2 рази
            image_label = tk.Label(top_container, image=self.photo, bg="white")
            image_label.pack(side=tk.LEFT, padx=20)
        except:
            print("Не вдалося завантажити зображення")

        # Activity history table
        history_frame = ctk.CTkFrame(self.main_frame, fg_color="white", width=303, height=189)
        history_frame.pack(side="left")
        history_frame.pack_propagate(False)  # Вимкнути автоматичну зміну розміру
        history_frame.pack()  # Видалити fill="both", expand=True

        columns = ("ID", "Activity", "Min", "Calories", "Date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=10, anchor="center")

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_activity(self):
        activity_name = self.activity_var.get()
        time_str = self.time_entry.get()

        if not activity_name:
            messagebox.showerror("Error", "Please select an activity")
            return

        try:
            time_spent = float(time_str)
            if time_spent <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for time")
            return

        if activity_name not in self.activity.activities:
            messagebox.showerror("Error", "Invalid activity selected")
            return

        calories_burned = self.activity.activities[activity_name] * time_spent

        self.activity.today_activity.append({
            "activity": activity_name,
            "time": time_spent,
            "calories_burned": calories_burned,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        messagebox.showinfo("Success",
                            f"Activity added: {activity_name} for {time_spent} min\n"
                            f"Calories burned: {calories_burned:.2f} kcal")

        self.update_activity_table()
        self.activity_var.set("")
        self.time_entry.delete(0, tk.END)

        # Update user's burned calories
        self.user.nutrition.burn_calories(calories_burned)

    def update_activity_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, activity in enumerate(self.activity.today_activity, 1):
            self.tree.insert("", "end", values=(
                idx,
                activity["activity"],
                activity["time"],
                f"{activity['calories_burned']:.2f}",
                activity.get("date", "")
            ))

    def on_nav_click(self, name):
        print(f"Menu button clicked: {name}")
        for btn in self.nav_buttons.values():
            btn.configure(bg="#c4c4c4")
        self.nav_buttons[name].configure(bg="#8d8989")
        self.selected_button = name


class Activity:
    def __init__(self, user):
        self.user = user
        self.catalog_path = "activity_catalog.json"
        self.activities = self.load_activity_catalog()
        self.today_activity = []

    def load_activity_catalog(self):
        if not os.path.exists(self.catalog_path):
            default_activities = {
                "Running": 10,
                "Swimming": 8,
                "Cycling": 7,
                "Weight Training": 5,
                "Yoga": 3,
                "Walking": 4
            }
            with open(self.catalog_path, "w") as file:
                json.dump(default_activities, file)
            return default_activities
        with open(self.catalog_path, "r") as file:
            return json.load(file)

    def get_today_activity(self):
        return sum(activity["calories_burned"] for activity in self.today_activity)


class User:
    def __init__(self):
        self.nutrition = self.Nutrition()

    class Nutrition:
        def burn_calories(self, calories):
            print(f"Burned {calories} calories")


if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityTrackerApp(root)
    root.mainloop()