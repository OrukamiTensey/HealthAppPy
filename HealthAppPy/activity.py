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
        self.root.geometry("636x402")  # Збільшений розмір вікна
        self.root.configure(bg="#E6E4E4")
        self.root.minsize(636, 402)  # Мінімальний розмір

        self.selected_button = None
        self.nav_buttons = {}
        self.user = User()
        self.activity = Activity(self.user)
        self.current_content = None
        self.content_stack = []  # To track navigation history

        # Основний контейнер з двома колонками
        self.main_container = tk.Frame(root, bg="#E6E4E4")
        self.main_container.pack(fill="both", expand=True)

        # Ліва панель (sidebar)
        self.create_sidebar()

        # Права панель (основний вміст)
        self.right_panel = tk.Frame(self.main_container, bg="#E6E4E4")
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.create_header()
        self.create_main_content()
        self.create_workout_content()  # Create workout content but don't show it yet

        self.on_nav_click("Activity")  # Default selected menu item

    def create_header(self):
        self.header = tk.Frame(self.right_panel, bg="#58C75C", height=47)
        self.header.pack(side='top', fill='x')
        self.header.pack_propagate(False)

        # Back button (initially hidden)
        self.back_button = ctk.CTkButton(
            self.header,
            text="←",
            width=30,
            fg_color="transparent",
            hover_color="#4CAF50",
            command=self.go_back,
            font=("Arial", 16)
        )
        self.back_button.pack(side="left", padx=5)
        self.back_button.pack_forget()

        self.title_label = tk.Label(
            self.header,
            text="My activity",
            font=("Helvetica", 20, "bold"),
            bg="#58C75C",
            fg="white"
        )
        self.title_label.pack(pady=10)

    def go_back(self):
        if self.content_stack:
            previous_content = self.content_stack.pop()
            self.show_content(previous_content, is_back_navigation=True)

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_container, fg_color="#C8C8C8", width=150)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        menu_items = {
            "Profile": "👤",
            "Nutrition": "🍴",
            "Activity": "🏃",
            "CalorieC": "📊",
            "Reg_Win": "📝",
            "Help": "❓",
            "Workout": "💪"  # Added Workout to sidebar
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
        # Main content frame that will be shown by default
        self.main_content_frame = ctk.CTkFrame(self.right_panel, fg_color="#E6E4E4")

        # Основний контент у правій панелі
        content_frame = ctk.CTkFrame(self.main_content_frame, fg_color="#E6E4E4")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Верхня частина - форма та зображення
        top_frame = ctk.CTkFrame(content_frame, fg_color="#E6E4E4")
        top_frame.pack(fill="x", pady=10)

        # Форма для введення даних
        form_frame = ctk.CTkFrame(top_frame, fg_color="#E6E4E4")
        form_frame.pack(side="left", fill="both", expand=True, padx=10)

        # Випадаючий список активностей
        self.activity_var = ctk.StringVar(value="Activity:")
        activities = list(self.activity.activities.keys())
        self.activity_combobox = ctk.CTkComboBox(
            form_frame,
            variable=self.activity_var,
            values=activities,
            width=200
        )
        self.activity_combobox.pack(pady=5, fill="x")

        # Поле для введення часу
        self.time_entry = ctk.CTkEntry(form_frame, placeholder_text="Minutes")
        self.time_entry.pack(pady=5, fill="x")

        # Кнопка додавання активності
        add_btn = ctk.CTkButton(
            form_frame,
            text="Add Activity",
            command=self.add_activity,
            fg_color="#58C75C",
            hover_color="#4CAF50"
        )
        add_btn.pack(pady=10, fill="x")

        # Workout button on main screen
        workout_btn = ctk.CTkButton(
            form_frame,
            text="💪 Start Workout",
            command=lambda: self.show_content("Workout"),
            fg_color="#FF5733",
            hover_color="#E64A19"
        )
        workout_btn.pack(pady=10, fill="x")

        # Обробники подій для плейсхолдера
        def clear_placeholder(event):
            if self.activity_var.get() == "Activity:":
                self.activity_var.set("")

        def restore_placeholder(event):
            if not self.activity_var.get():
                self.activity_var.set("Activity:")

        self.activity_combobox.bind("<FocusIn>", clear_placeholder)
        self.activity_combobox.bind("<FocusOut>", restore_placeholder)

        # Зображення (права частина верхнього блоку)
        image_frame = ctk.CTkFrame(top_frame, fg_color="#E6E4E4")
        image_frame.pack(side="right", padx=20)

        try:
            self.photo = tk.PhotoImage(file="running.png")
            self.photo = self.photo.subsample(4, 4)
            image_label = tk.Label(image_frame, image=self.photo, bg="white")
            image_label.pack()
        except:
            print("Не вдалося завантажити зображення")

        # Таблиця історії активностей
        history_frame = ctk.CTkFrame(content_frame, fg_color="white")
        history_frame.pack(fill="both", expand=True, pady=(0, 20))

        columns = ("ID", "Activity", "Min", "Calories", "Date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_workout_content(self):
        # Workout content frame that will be shown when Workout button is clicked
        self.workout_content_frame = ctk.CTkFrame(self.right_panel, fg_color="#E6E4E4")

        # Create notebook for free and paid courses
        notebook = ttk.Notebook(self.workout_content_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Free courses tab
        free_frame = ctk.CTkFrame(notebook, fg_color="#E6E4E4")
        paid_frame = ctk.CTkFrame(notebook, fg_color="#E6E4E4")

        notebook.add(free_frame, text="Free Courses")
        notebook.add(paid_frame, text="Premium Courses")

        # Add content to free courses tab with scrollbar
        self.setup_scrollable_course_tab(free_frame, is_free=True)
        self.setup_scrollable_course_tab(paid_frame, is_free=False)

        # Back button to return to main content
        back_btn = ctk.CTkButton(
            self.workout_content_frame,
            text="← Back to Activity",
            command=lambda: self.show_content("Activity"),
            fg_color="#58C75C",
            hover_color="#4CAF50"
        )
        back_btn.pack(side="bottom", pady=10)

    def setup_scrollable_course_tab(self, parent_frame, is_free=True):
        # Create main container frame
        container = ctk.CTkFrame(parent_frame, fg_color="#E6E4E4")
        container.pack(fill="both", expand=True)

        # Create canvas with scrollbar
        canvas = tk.Canvas(container, bg="#E6E4E4", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#E6E4E4")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add label at the top
        if is_free:
            tab_label = "Free Workout Courses"
            courses = [
                {"name": "Beginner Full Body Workout",
                 "author": "John Fitness",
                 "description": "Perfect for beginners to start their fitness journey"},
                {"name": "30-Day Yoga Challenge",
                 "author": "Yoga with Anna",
                 "description": "Daily yoga sessions to improve flexibility and strength"},
                {"name": "Home Workout (No Equipment)",
                 "author": "HomeFit Trainer",
                 "description": "Effective workouts using just your body weight"},
                {"name": "Cardio Blast Routine",
                 "author": "Cardio King",
                 "description": "High-intensity cardio workout to burn calories fast"},
                {"name": "Stretching & Flexibility",
                 "author": "Flex Master",
                 "description": "Improve your range of motion and prevent injuries"},
                {"name": "Pilates Fundamentals",
                 "author": "Pilates Pro",
                 "description": "Core strengthening exercises for all levels"},
                {"name": "Morning Energy Boost",
                 "author": "Energy Coach",
                 "description": "Short routines to start your day with energy"},
                {"name": "Posture Correction",
                 "author": "Posture Expert",
                 "description": "Exercises to improve your posture and reduce back pain"}
            ]
        else:
            tab_label = "Premium Workout Programs"
            courses = [
                {"name": "Advanced Bodybuilding Program",
                 "author": "Pro Bodybuilder",
                 "description": "12-week program to build muscle mass",
                 "price": "$49.99"},
                {"name": "Personalized Training Plan",
                 "author": "Elite Trainers",
                 "description": "Custom workout plan based on your goals",
                 "price": "$79.99"},
                {"name": "Marathon Preparation",
                 "author": "Running Pro",
                 "description": "Complete training for marathon runners",
                 "price": "$59.99"},
                {"name": "Olympic Weightlifting Course",
                 "author": "Olympic Coach",
                 "description": "Master the snatch and clean & jerk",
                 "price": "$69.99"},
                {"name": "Nutrition + Workout Bundle",
                 "author": "Health Experts",
                 "description": "Complete package for fitness and nutrition",
                 "price": "$99.99"},
                {"name": "Athlete Performance Program",
                 "author": "Sports Scientist",
                 "description": "Training to maximize athletic performance",
                 "price": "$89.99"},
                {"name": "Senior Fitness Program",
                 "author": "Golden Age Trainer",
                 "description": "Safe exercises for older adults",
                 "price": "$49.99"},
                {"name": "Post-Rehabilitation Routine",
                 "author": "Physical Therapist",
                 "description": "Exercises for recovery after injuries",
                 "price": "$59.99"}
            ]

        label = ctk.CTkLabel(
            scrollable_frame,
            text=tab_label,
            font=("Helvetica", 16, "bold")
        )
        label.pack(pady=10)

        # Add courses to the scrollable frame
        for course in courses:
            course_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
            course_frame.pack(fill="x", padx=10, pady=5)

            # Course info on the left
            info_frame = ctk.CTkFrame(course_frame, fg_color="white")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

            name_label = ctk.CTkLabel(
                info_frame,
                text=course["name"],
                font=("Helvetica", 12, "bold")
            )
            name_label.pack(anchor="w")

            author_label = ctk.CTkLabel(
                info_frame,
                text=f"by {course['author']}",
                font=("Helvetica", 10),
                text_color="gray"
            )
            author_label.pack(anchor="w")

            desc_label = ctk.CTkLabel(
                info_frame,
                text=course["description"],
                font=("Helvetica", 10),
                wraplength=400
            )
            desc_label.pack(anchor="w", pady=(0, 5))

            # Buttons on the right
            btn_frame = ctk.CTkFrame(course_frame, fg_color="white")
            btn_frame.pack(side="right", padx=10, pady=5)

            info_btn = ctk.CTkButton(
                btn_frame,
                text="ℹ️ Info",
                width=60,
                fg_color="#3498DB",
                hover_color="#2980B9",
                command=lambda c=course: self.show_course_info(c)
            )
            info_btn.pack(side="left", padx=5)

            if is_free:
                action_btn = ctk.CTkButton(
                    btn_frame,
                    text="Start",
                    width=60,
                    fg_color="#58C75C",
                    hover_color="#4CAF50"
                )
            else:
                action_btn = ctk.CTkButton(
                    btn_frame,
                    text=course["price"],
                    width=80,
                    fg_color="#FF5733",
                    hover_color="#E64A19"
                )
            action_btn.pack(side="left", padx=5)

    def show_course_info(self, course):
        # Hide current content
        if self.current_content:
            self.current_content.pack_forget()

        # Create info frame
        self.course_info_frame = ctk.CTkFrame(self.right_panel, fg_color="#E6E4E4")
        self.current_content = self.course_info_frame

        # Add to navigation stack
        if self.content_stack and self.content_stack[-1] != "CourseInfo":
            self.content_stack.append("CourseInfo")

        # Show back button
        self.back_button.pack(side="left", padx=5)
        self.title_label.config(text=f"Course: {course['name']}")

        # Course name
        name_label = ctk.CTkLabel(
            self.course_info_frame,
            text=course["name"],
            font=("Helvetica", 18, "bold")
        )
        name_label.pack(pady=(20, 5), padx=20, anchor="w")

        # Author
        author_frame = ctk.CTkFrame(self.course_info_frame, fg_color="#E6E4E4")
        author_frame.pack(fill="x", pady=5, padx=20)

        author_title = ctk.CTkLabel(
            author_frame,
            text="Author:",
            font=("Helvetica", 14, "bold")
        )
        author_title.pack(side="left", padx=(0, 5))

        author_label = ctk.CTkLabel(
            author_frame,
            text=course["author"],
            font=("Helvetica", 14)
        )
        author_label.pack(side="left")

        # Description
        desc_frame = ctk.CTkFrame(self.course_info_frame, fg_color="white")
        desc_frame.pack(fill="both", expand=True, padx=20, pady=10)

        desc_label = ctk.CTkLabel(
            desc_frame,
            text=course["description"],
            font=("Helvetica", 12),
            wraplength=550,
            justify="left"
        )
        desc_label.pack(pady=10, padx=10, anchor="nw")

        # Price if it's a paid course
        if "price" in course:
            price_frame = ctk.CTkFrame(self.course_info_frame, fg_color="#E6E4E4")
            price_frame.pack(fill="x", pady=10, padx=20)

            price_title = ctk.CTkLabel(
                price_frame,
                text="Price:",
                font=("Helvetica", 14, "bold")
            )
            price_title.pack(side="left", padx=(0, 5))

            price_label = ctk.CTkLabel(
                price_frame,
                text=course["price"],
                font=("Helvetica", 14),
                text_color="#FF5733"
            )
            price_label.pack(side="left")

        # Action button
        if "price" in course:
            action_btn = ctk.CTkButton(
                self.course_info_frame,
                text=f"Purchase for {course['price']}",
                fg_color="#FF5733",
                hover_color="#E64A19",
                font=("Helvetica", 14)
            )
        else:
            action_btn = ctk.CTkButton(
                self.course_info_frame,
                text="Start Course",
                fg_color="#58C75C",
                hover_color="#4CAF50",
                font=("Helvetica", 14)
            )
        action_btn.pack(pady=20)

        self.course_info_frame.pack(fill="both", expand=True)

    def show_content(self, content_name, is_back_navigation=False):
        # Hide current content
        if self.current_content:
            self.current_content.pack_forget()

        # Update navigation stack
        if not is_back_navigation and content_name != "CourseInfo":
            if self.current_content:
                self.content_stack.append(self.current_content)
            else:
                self.content_stack.append(content_name)

        # Show the requested content
        if content_name == "Activity":
            self.current_content = self.main_content_frame
            self.title_label.config(text="My Activity")
            self.back_button.pack_forget()
        elif content_name == "Workout":
            self.current_content = self.workout_content_frame
            self.title_label.config(text="Workout Courses")
            self.back_button.pack_forget()
        elif content_name == "CourseInfo":
            # Handled in show_course_info method
            return

        self.current_content.pack(fill="both", expand=True)

    def add_activity(self):
        activity_name = self.activity_var.get()
        time_str = self.time_entry.get()

        if not activity_name or activity_name == "Activity:":
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

        # Show appropriate content based on selection
        if name == "Workout":
            self.show_content("Workout")
        else:
            self.show_content("Activity")


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