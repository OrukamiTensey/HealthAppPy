class CalorieCounting:
    def __init__(self, user):
        self.user = user
        self.activity_factor = float(user.activity_factor)  # фактор фізичної активності 
        self.nutrition = user.nutrition  # Споживання користувача через клас Nutrition
        self.goal = user.goal  # Ціль користувача (схуднення, підтримка, набір ваги)
    
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

    def calculate_bjv(self):
        # Розрахунок білків, жирів та вуглеводів за нормою
        total_calories = self.calculate_total_calories()
        protein = total_calories * 0.3 / 4  # 1 грам білка = 4 калорії
        fat = total_calories * 0.3 / 9      # 1 грам жиру = 9 калорій
        carb = total_calories * 0.4 / 4     # 1 грам вуглеводів = 4 калорії
        
        return {"protein": protein, "fat": fat, "carb": carb}


    def show_progress(self):
        # Показує прогрес (калорії і БЖВ) порівняно з нормою
        norm = self.calculate_bjv()
        consumed = self.nutrition.get_daily_summary() 
        
        if not consumed:
            print("No nutrition data for today.")
            return

        total_calories = self.calculate_total_calories()
        print(f"\n--- Your Progress Today ---")
        print(f"Calories: {consumed['calories']}/{total_calories} kcal ({(consumed['calories'] / total_calories) * 100:.2f}%)")
        print(f"Protein: {consumed['protein']}/{norm['protein']}g ({(consumed['protein'] / norm['protein']) * 100:.2f}%)")
        print(f"Fat: {consumed['fat']}/{norm['fat']}g ({(consumed['fat'] / norm['fat']) * 100:.2f}%)")
        print(f"Carbs: {consumed['carbs']}/{norm['carb']}g ({(consumed['carbs'] / norm['carb']) * 100:.2f}%)")

         # Прогрес у вигляді заповненої смуги (порівняння калорій)
        progress = (consumed['calories'] / total_calories) * 100
        print(f"Progress bar: [{'#' * int(progress // 2)}{'-' * (50 - int(progress // 2))}] {int(progress)}%")