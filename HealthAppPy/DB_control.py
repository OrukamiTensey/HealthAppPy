import sqlite3

# приклад коду для використання кожної функції для керування базою даних
#
# ініціалізуємо змінну для взаємодії з функціями керування БД
#       db = DBControl()
#
#       db_name = "example.db"
#       table_name = "NUTRITION"
#
# функція для створення файлу бази даних, для цього необхідно ввести назву
#       db.create_db(db_name)
#
#       sql_columns = """CREATE TABLE IF NOT EXISTS NUTRITION (
#                        PRODUCT TEXT PRIMARY KEY,
#                        PROTEINS REAL NOT NULL,
#                        FATS REAL NOT NULL,
#                        CARBOHYDRATES REAL NOT NULL,
#                        KCAL INTEGER NOT NULL
#                        );"""
#
# функція для створення таблиці значень в файлі бази даних, для цього зазначаємо
# назву існуючої БД та SQL-запит з необхідною інформацією для формування таблиці
#       db.create_table(db_name, sql_columns)
#
# тут використовується конструкція для читання з текстового файлу рядків, які
# містять сформовані SQL-запити, значення яких вносяться за допомогою функції
# в базу даних
#       with open("testfordb.txt", "r") as file:
#           for line in file:
#               db.insert_data(db_name, line.strip())
#
# приклад SQL-запитів, які вставляються: INSERT INTO NUTRITION (PRODUCT, PROTEINS, FATS, CARBOHYDRATES, KCAL) VALUES('Quince', 0.6, 0, 8.7, 37);
#
# функція для видалення якогось конкретного рядка за певною умовою
#       db.delete_specific_data(db_name, table_name, "PRODUCT = 'Apricot'")
#
# якщо потрібно просто очистити всі дані таблиці - використовуйте цю функцію
#       db.delete_data(db_name, table_name)
#
# функція для друку значень з БД, за потреби можна ввести умову фільтрування значень
#       db.print_data(db_name, "*", table_name)
#       db.print_data(db_name, "*", table_name, "FATS < 9")
#
# функція для перевірки на наявність потрібних даних в таблиці (за умовою)
#       db.data_exists(db_name, "*", table_name, "PRODUCT = 'Lamb'")
#
# функція для отримання всіх, відповідаючих виставленій умові, даних, у результаті
# отримуємо масив кортежів із даними (рядки даних)
#       result = db.receive_data(db_name, "*", table_name, "KCAL > 43")
#
#       for record in result:
#           product, proteins, fats, carbohydrates, kcal = record
#           print(product)

class DBControl:
    @staticmethod
    def create_db(file_name):
        # Створити базу даних
        conn = sqlite3.connect(file_name)
        conn.close()

    @staticmethod
    def create_table(file_name, sql_columns):
        # Створити таблицю в базі даних
        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute(sql_columns)
            conn.commit()
            print("Table created Successfully")
        except sqlite3.Error as e:
            print(f"Error in createTable function: {e}")
        finally:
            conn.close()

    @staticmethod
    def delete_specific_data(file_name, table_name, condition):
        # Видалити конкретні дані з таблиці на основі умови
        sql = f"DELETE FROM {table_name} WHERE {condition};"

        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';")
            result = cursor.fetchone()

            cursor.execute(sql)
            print("Records deleted Successfully!")

            if result:
                sql_reset = f"DELETE FROM sqlite_sequence WHERE name = '{table_name}';"
                cursor.execute(sql_reset)
                print("Auto-increment reset Successfully!")
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error in deleteData function: {e}")
        finally:
            conn.close()
            
    @staticmethod
    def delete_data(file_name, table_name):
        # Видалити всі дані з таблиці
        sql = f"DELETE FROM {table_name};"
    
        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
        
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';")
            result = cursor.fetchone()
        
            cursor.execute(sql)
            print("Records deleted Successfully!")
        
            if result:
                sql_reset = f"DELETE FROM sqlite_sequence WHERE name = '{table_name}';"
                cursor.execute(sql_reset)
                print("Auto-increment reset Successfully!")
        
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error in deleteData function: {e}")
        finally:
            conn.close()


    @staticmethod
    def insert_data(file_name, sql_value):
        # Вставити дані (один рядок) в таблицю
        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute(sql_value)
            conn.commit()
            #print("Records inserted Successfully!")
        except sqlite3.Error as e:
            print(f"Error in insertData function: {e}")
        finally:
            conn.close()

    @staticmethod
    def print_data(file_name, columns_name, table_name, object_condition=""):
        # Вивести всі дані з таблиці за вказаними параметрами
        sql = f"SELECT {columns_name} FROM {table_name}"
        if object_condition:
            sql += f" WHERE {object_condition}"

        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            #print("Records printed Successfully!")
        except sqlite3.Error as e:
            print(f"Error in printData function: {e}")
        finally:
            conn.close()

    @staticmethod
    def data_exists(file_name, columns_name, table_name, object_condition):
        # Перевірити, чи існують дані в таблиці
        sql = f"SELECT {columns_name} FROM {table_name} WHERE {object_condition} LIMIT 1;"
        exists = False

        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            exists = cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Failed to prepare statement: {e}")
        finally:
            conn.close()

        return exists

    @staticmethod
    def receive_data(file_name, columns_name, table_name, object_condition=""):
        # Отримати всі дані з таблиці за вказаними параметрами
        sql = f"SELECT {columns_name} FROM {table_name}"
        if object_condition:
            sql += f" WHERE {object_condition}"

        received_tuple = []
            
        try:
            conn = sqlite3.connect(file_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                received_tuple.append(row)
            #print("Records printed Successfully!")
        except sqlite3.Error as e:
            print(f"Error in printData function: {e}")
        finally:
            conn.close()

        return received_tuple