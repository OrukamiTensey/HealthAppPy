import json
import os

# activities_table_sql = """CREATE TABLE IF NOT EXISTS activities (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         user_id INTEGER NOT NULL,
#                         activity_type TEXT NOT NULL,
#                         duration_minutes INTEGER NOT NULL,
#                         calories_burned REAL NOT NULL,
#                         date TEXT NOT NULL,
#                         FOREIGN KEY (user_id) REFERENCES users (id)
#                         );"""

class Activity:
    def __init__(self, user):
        self.user = user
        self.catalog_path = "activity_catalog.json"
        self.activities = self.load_activity_catalog()
        self.today_activity = []

    def load_activity_catalog(self):
        if not os.path.exists(self.catalog_path):
            print(f"Catalog file '{self.catalog_path}' not found.")
            return {}
        with open(self.catalog_path, "r") as file:
            return json.load(file)

    def add_activity(self):
        print("\n--- Add Activity ---")
        print("Available activities:", ", ".join(self.activities.keys()))
        activity_name = input("Enter activity name: ").strip().title()

        if activity_name not in self.activities:
            print("Invalid activity. Please choose from the available list.")
            return

        try:
            time_spent = float(input(f"Enter time spent on {activity_name} (in minutes): "))
        except ValueError:
            print("Invalid input. Time must be a number.")
            return

        calories_burned = self.activities[activity_name] * time_spent

        # Додаємо активність у список
        self.today_activity.append({
            "activity": activity_name,
            "time": time_spent,
            "calories_burned": calories_burned
        })

        print(f"Activity added: {activity_name} for {time_spent} min. Burned: {calories_burned:.2f} kcal.")

        # Віднімаємо спалені калорії з харчової історії користувача
        self.user.nutrition.burn_calories(calories_burned)

    def get_today_activity(self):
        return sum(activity["calories_burned"] for activity in self.today_activity)

    def show_today_activity(self):
        if not self.today_activity:
            print("No activities recorded for today.")
        else:
            print("\n--- Today's Activities ---")
            for activity in self.today_activity:
                print(f"{activity['activity']} - {activity['time']} min - {activity['calories_burned']:.2f} kcal")

            total = self.get_today_activity()
            print(f"\nTotal calories burned today: {total:.2f} kcal")