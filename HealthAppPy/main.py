import os
import json
from user import User
from registration import RegistrationWindow
from nutrition import Nutrition
from calorie_counting import CalorieCounting
from activity import Activity

# Ініціалізація
reg_window = RegistrationWindow()
reg_window.load_users()

current_user_path = "current_user.json"
user = None

# Спроба автоматичного входу
if os.path.exists(current_user_path):
    with open(current_user_path, "r") as file:
        user_data = json.load(file)
        user = User.from_dict(user_data)
        print(f"Welcome back, {user.name}!")
else:
    while True:
        print("\n--- Welcome ---")
        print("1. Register")
        print("2. Log in")
        print("0. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            user = reg_window.register_new_user()
            reg_window.save_users()
        elif choice == "2":
            user = reg_window.login_user()
        elif choice == "0":
            print("Exiting the app. Goodbye!")
            exit()
        else:
            print("Invalid option. Try again.")
            continue

        if user:
            # Збереження поточного користувача
            with open(current_user_path, "w") as file:
                json.dump(user.to_dict(), file)
            break

# Основне меню
nutrition = user.nutrition
activity = Activity(user)
calorie_counter = CalorieCounting(user)

while True:
    print("\n--- Main Menu ---")
    print("1. View Profile")
    print("2. Update Profile")
    print("3. Add Product (Nutrition)")
    print("4. Show Consumed History")
    print("5. Show Progress (Calories & Nutrients)")
    print("6. Add Activity")
    print("7. Show Today's Activities")
    print("0. Logout")

    user_choice = input("Choose an option: ")

    if user_choice == "1":
        user.display_profile()
    elif user_choice == "2":
        user.update_profile()
        reg_window.save_users()
        # оновити калькулятор після зміни даних
        calorie_counter = CalorieCounting(user)
        with open(current_user_path, "w") as file:
            json.dump(user.to_dict(), file)
    elif user_choice == "3":
        nutrition.add_consumed_product()
    elif user_choice == "4":  
        nutrition.show_today_consumption()
    elif user_choice == "5":
        calorie_counter.show_progress()
    elif user_choice == "6":
        activity.add_activity()
    elif user_choice == "7":
        activity.show_today_activity()
    elif user_choice == "0":
        print("Logging out...")
        if os.path.exists(current_user_path):
            os.remove(current_user_path)
        break
    else:
        print("Invalid option. Try again.")