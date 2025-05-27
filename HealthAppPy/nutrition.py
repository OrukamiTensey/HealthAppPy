import json
import os
from datetime import date
from DB_control import DBControl

# products_table_sql = """CREATE TABLE IF NOT EXISTS PRODUCTS (
#                         PRODUCT TEXT PRIMARY KEY,
#                         PROTEINS REAL NOT NULL,
#                         FATS REAL NOT NULL,
#                         CARBOHYDRATES REAL NOT NULL,
#                         KCAL INTEGER NOT NULL
#                         );"""
    
# nutrition_table_sql = """CREATE TABLE IF NOT EXISTS NUTRITION (
#                         USER TEXT NOT NULL,
#                         DATE DATE NOT NULL,
#                         PRODUCT TEXT NOT NULL,
#                         CONSUMED_MASS REAL NOT NULL,
#                         CONSUMED_PROTEINS REAL NOT NULL,
#                         CONSUMED_FATS REAL NOT NULL,
#                         CONSUMED_CARBOHYDRATES REAL NOT NULL,
#                         CONSUMED_KCAL INTEGER NOT NULL
#                         );"""

class Nutrition:
    def __init__(self, user_email, catalog_path="product_catalog.json", history_path="nutrition_history.json"):
        self.user_email = user_email
        self.catalog_path = catalog_path
        self.history_path = history_path
        self.today = date.today().isoformat()
        self.catalog = self.load_catalog()
        self.history = self.load_history()

        self.db = DBControl()
        self.db_name = "Health_database.db"

        nutrition_table_sql = """CREATE TABLE IF NOT EXISTS NUTRITION (
                                 USER TEXT PRIMARY KEY,
                                 DATE DATE NOT NULL,
                                 PRODUCT TEXT NOT NULL,
                                 CONSUMED_MASS REAL NOT NULL,
                                 CONSUMED_PROTEINS REAL NOT NULL,
                                 CONSUMED_FATS REAL NOT NULL,
                                 CONSUMED_CARBOHYDRATES REAL NOT NULL,
                                 CONSUMED_KCAL INTEGER NOT NULL
                                 );"""

        consumed_table_sql = """CREATE TABLE IF NOT EXISTS CONSUMED (
                                 USER TEXT NOT NULL,
                                 DATE DATE NOT NULL,
                                 TOTAL_MASS REAL NOT NULL,
                                 TOTAL_PROTEINS REAL NOT NULL,
                                 TOTAL_FATS REAL NOT NULL,
                                 TOTAL_CARBOHYDRATES REAL NOT NULL,
                                 TOTAL_KCAL INTEGER NOT NULL,
                                 NORM_PROTEINS REAL NOT NULL,
                                 NORM_FATS REAL NOT NULL,
                                 NORM_CARBOHYDRATES REAL NOT NULL,
                                 NORM_KCAL INTEGER NOT NULL
                                 );"""

        self.db.create_table(self.db_name, nutrition_table_sql)
        self.db.create_table(self.db_name, consumed_table_sql)



    def load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, 'r') as file:
                data = json.load(file)
                # Перетворимо список у словник для швидкого пошуку за назвою (в нижньому регістрі)
                return {item["name"].lower(): item for item in data}
        else:
            print(f"Catalog file '{self.catalog_path}' not found.")
            return {}

    def load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r') as file:
                return json.load(file)
        return {}

    def save_history(self):
        with open(self.history_path, 'w') as file:
            json.dump(self.history, file, indent=4)

            self.db.

    def add_consumed_product(self):
        product_name = input("Enter product name: ").strip().lower()
        if product_name not in self.catalog:
            print(f"Product '{product_name}' not found in catalog.")
            return

        try:
            grams = float(input("Enter amount in grams: "))
            if grams <= 0:
                print("Amount must be positive.")
                return
        except ValueError:
            print("Invalid number entered.")
            return

        product_info = self.catalog[product_name]
        factor = grams / 100
        consumed = {
            "name": product_name,
            "grams": grams,
            "calories": round(product_info["calories"] * factor, 1),
            "protein": round(product_info["protein"] * factor, 1),
            "fat": round(product_info["fat"] * factor, 1),
            "carbs": round(product_info["carbs"] * factor, 1)
        }

        user_key = f"{self.user_email}_{self.today}"

        if user_key not in self.history:
            self.history[user_key] = []

        self.history[user_key].append(consumed)
        self.save_history()
        print(f"Added {grams}g of {product_name} to your nutrition history for {self.today}.")


    def burn_calories(self, calories_burned):
        """
        Віднімає спалені калорії з денного споживання як окремий запис.
        """
        user_key = f"{self.user_email}_{self.today}"
    
        if user_key not in self.history:
            self.history[user_key] = []

        # Створюємо віртуальний продукт з негативними калоріями
        burned_product = {
            "name": "Burned Calories (Activity)",
            "grams": 0,
            "calories": -calories_burned,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }

        self.history[user_key].append(burned_product)
        self.save_history()

        print(f"Calories burned ({calories_burned:.2f} kcal) subtracted from today's total.")
        
    def show_today_consumption(self):
        user_key = f"{self.user_email}_{self.today}"
        if user_key not in self.history or not self.history[user_key]:
            print("No consumption history for today.")
            return
    
        print(f"\n--- Consumption History for {self.today} ---")
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0

        for item in self.history[user_key]:
            print(f"{item['grams']}g {item['name'].capitalize()}: "
                  f"{item['calories']} kcal, "
                  f"{item['protein']}g protein, "
                  f"{item['fat']}g fat, "
                  f"{item['carbs']}g carbs")
            total_calories += item['calories']
            total_protein += item['protein']
            total_fat += item['fat']
            total_carbs += item['carbs']

        print("\nTotal today:")
        print(f"Calories: {total_calories} kcal")
        print(f"Protein: {total_protein} g")
        print(f"Fat: {total_fat} g")
        print(f"Carbs: {total_carbs} g")
    
    def get_daily_summary(self):
        user_key = f"{self.user_email}_{self.today}"
        if user_key not in self.history:
            print("No entries for today.")
            return None

        total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for entry in self.history[user_key]:
            total["calories"] += entry["calories"]
            total["protein"] += entry["protein"]
            total["fat"] += entry["fat"]
            total["carbs"] += entry["carbs"]

        return total
