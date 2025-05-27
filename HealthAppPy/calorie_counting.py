# consumed_table_sql = """CREATE TABLE IF NOT EXISTS CONSUMED (
#                         USER TEXT NOT NULL,
#                         DATE DATE NOT NULL,
#                         TOTAL_MASS REAL NOT NULL,
#                         TOTAL_PROTEINS REAL NOT NULL,
#                         TOTAL_FATS REAL NOT NULL,
#                         TOTAL_CARBOHYDRATES REAL NOT NULL,
#                         TOTAL_KCAL INTEGER NOT NULL,
#                         NORM_PROTEINS REAL NOT NULL,
#                         NORM_FATS REAL NOT NULL,
#                         NORM_CARBOHYDRATES REAL NOT NULL,
#                         NORM_KCAL INTEGER NOT NULL
#                         );"""

from datetime import date
from DB_control import DBControl


class CalorieCounting:
    def __init__(self, user):
        self.user = user
        self.activity_factor = float(user.activity_factor)  # фактор фізичної активності
        self.nutrition = user.nutrition  # Споживання користувача через клас Nutrition
        self.goal = user.goal  # Ціль користувача (схуднення, підтримка, набір ваги)
        self.bjv_mode = user.bjv_mode

    def calculate_bmr(self):
        # Основний рівень метаболізму за формулою Harris-Benedict
        if self.user.sex == 'M':
            bmr = 10 * self.user.weight + 6.25 * self.user.height - 5 * self.user.get_age() + 5
        else:
            bmr = 10 * self.user.weight + 6.25 * self.user.height - 5 * self.user.get_age() - 161
        return bmr

    def calculate_total_calories(self):
        # Загальна кількість калорій із урахуванням фізичної активності
        bmr = self.calculate_bmr()
        total_calories = bmr * self.activity_factor

        # Якщо мета - зменшити вагу
        if self.goal == 'L':
            total_calories -= 500  # Скидаємо 500 калорій для схуднення
        elif self.goal == 'G':
            total_calories += 500  # Додаємо 500 калорій для набору ваги

        return total_calories

    def calculate_bjv(self, bjv_mode = "default"):
        """
        Розрахунок білків, жирів та вуглеводів (БЖВ) залежно від мети:
        - bjv_mode = "default"       збалансоване харчування
        - bjv_mode = "fat_loss"      для втрати жиру
        - bjv_mode = "muscle_gain"   для набору м'язової маси
        """

        total_calories = self.calculate_total_calories()

        if bjv_mode == "fat_loss":
            # Більше білка для збереження м'язів, менше вуглеводів
            protein_ratio = 0.40
            fat_ratio = 0.30
            carb_ratio = 0.30

        elif bjv_mode == "muscle_gain":
            # Більше вуглеводів для енергії і м'язового росту
            protein_ratio = 0.30
            fat_ratio = 0.20
            carb_ratio = 0.50

        else:  # bjv_mode == "default"
            # Збалансоване харчування
            protein_ratio = 0.30
            fat_ratio = 0.30
            carb_ratio = 0.40

        protein = total_calories * protein_ratio / 4  # 1 г білка = 4 ккал
        fat = total_calories * fat_ratio / 9  # 1 г жиру = 9 ккал
        carb = total_calories * carb_ratio / 4  # 1 г вуглеводів = 4 ккал

        return {
            "goal": bjv_mode,
            "protein (g)": round(protein, 1),
            "fat (g)": round(fat, 1),
            "carb (g)": round(carb, 1)
        }

    def change_bjv_mode(self, bjv_mode):
        self.user.bjv_mode = bjv_mode

    # Зберігання норми в бд
    def store_norm_to_db(self, db_name):
        current_date = date.today().isoformat()
        norm_calories = int(self.calculate_total_calories())
        bjv = self.calculate_bjv()
        norm_protein = bjv['protein']
        norm_fat = bjv['fat']
        norm_carb = bjv['carb']

        columns = [
            "USER", "DATE",
            "TOTAL_MASS", "TOTAL_PROTEINS", "TOTAL_FATS", "TOTAL_CARBOHYDRATES", "TOTAL_KCAL",
            "NORM_PROTEINS", "NORM_FATS", "NORM_CARBOHYDRATES", "NORM_KCAL"
        ]

        values = [
            f"'{self.user.name}'", f"'{current_date}'",
            0, 0, 0, 0, 0,
            norm_protein, norm_fat, norm_carb, norm_calories
        ]

        insert_sql = f"""
                        INSERT INTO CONSUMED ({', '.join(columns)})
                        VALUES ({', '.join(map(str, values))});
                    """
        DBControl.insert_data(db_name, insert_sql)

    # Витягування результатів за день
    def get_daily_totals(self, db_name, target_date=None):
        if target_date is None:
            target_date = date.today().isoformat()

        condition = f"USER = '{self.user.name}' AND DATE = '{target_date}'"

        columns_name = "SUM(TOTAL_PROTEINS), SUM(TOTAL_FATS), SUM(TOTAL_CARBOHYDRATES), SUM(TOTAL_KCAL)"

        results = DBControl.receive_data(db_name, "CONSUMED", columns_name, condition)

        if results and results[0] and any(results[0]):
            proteins = results[0][0] or 0
            fats = results[0][1] or 0
            carbs = results[0][2] or 0
            kcal = results[0][3] or 0
            return (proteins, fats, carbs, kcal)
        else:
            return (0, 0, 0, 0)

    def show_progress(self):
        # Показує прогрес (калорії і БЖВ) порівняно з нормою
        norm = self.calculate_bjv()
        consumed = self.nutrition.get_daily_summary()

        if not consumed:
            print("No nutrition data for today.")
            return

        total_calories = self.calculate_total_calories()
        print(f"\n--- Your Progress Today ---")
        print(
            f"Calories: {consumed['calories']}/{total_calories} kcal ({(consumed['calories'] / total_calories) * 100:.2f}%)")
        print(
            f"Protein: {consumed['protein']}/{norm['protein']}g ({(consumed['protein'] / norm['protein']) * 100:.2f}%)")
        print(f"Fat: {consumed['fat']}/{norm['fat']}g ({(consumed['fat'] / norm['fat']) * 100:.2f}%)")
        print(f"Carbs: {consumed['carbs']}/{norm['carb']}g ({(consumed['carbs'] / norm['carb']) * 100:.2f}%)")

        # Прогрес у вигляді заповненої смуги (порівняння калорій)
        progress = (consumed['calories'] / total_calories) * 100
        print(f"Progress bar: [{'#' * int(progress // 2)}{'-' * (50 - int(progress // 2))}] {int(progress)}%")