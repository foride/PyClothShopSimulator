import mysql.connector
from datetime import date
from decimal import Decimal


class DB_Communication:
    def __init__(self):
        self.conn = None
        self.cursor = None
        # Initialize with your database credentials
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='jkhfasddjk123',
                port='3306',
                database='sklep'
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")


class User:
    def __init__(self, user_id: int, login: str, password: str, email: str, phone: str, name: str, surname: str,
                 role: str, database: DB_Communication):
        self.db = database
        self.user_id = user_id
        self.login = login
        self.password = password  # Note: Storing passwords in plain text is not secure
        self.email = email
        self.phone = phone
        self.name = name
        self.surname = surname
        self.role = role

    def user_menu(self):
        while True:
            print("\n--- User Menu ---")
            print("1: Display Attributes")
            print("2: Update Attributes")
            print("3: Delete Account")
            print("4: Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.display_attributes()
            elif choice == '2':
                self.update_attributes()
            elif choice == '3':
                self.delete_account()
            elif choice == '4':
                return 4
            else:
                print("Invalid choice. Please try again.")

    def display_attributes(self):
        print(f"Login: {self.login}")
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")
        print(f"Name: {self.name}")
        print(f"Surname: {self.surname}")
        print(f"Role: {self.role}")

    def update_attributes(self):
        new_email = input("Enter new email (or press Enter to skip): ")
        new_phone = input("Enter new phone (or press Enter to skip): ")
        new_name = input("Enter new name (or press Enter to skip): ")
        new_surname = input("Enter new surname (or press Enter to skip): ")

        self.db.cursor.callproc('UpdateUserDetails',
                                [self.user_id, new_email or self.email, new_phone or self.phone,
                                 new_name or self.name, new_surname or self.surname])
        self.db.conn.commit()

        self.email = new_email if new_email else self.email
        self.phone = new_phone if new_phone else self.phone
        self.name = new_name if new_name else self.name
        self.surname = new_surname if new_surname else self.surname
        print("User details updated successfully.")

    def delete_account(self):
        confirmation = input("Are you sure you want to delete your account? (yes/no): ")
        if confirmation.lower() == 'yes':
            try:

                self.db.cursor.callproc('DeleteUserAccount', [self.user_id])
                self.db.conn.commit()
                print("Account deleted successfully.")
                return 3

            except mysql.connector.Error as e:
                print(f"Error during account deletion: {e}")
        else:
            print("Account deletion cancelled.")


class Order:
    def __init__(self, order_id: int, order_date: date, amount: Decimal, user_id: int, payment_id: int,
                 delivery_id: int, clothes_id: int):
        self.order_id = order_id
        self.order_date = date
        self.amount = amount
        self.user_id = user_id
        self.payment_id = payment_id
        self.delivery_id = delivery_id
        self.clothes_id = clothes_id


class Payment:
    def __init__(self, payment_id: int, status: str, payment_form: str, payment_date: date):
        self.payment_id = payment_id
        self.status = status
        self.payment_form = payment_form
        self.payment_date = date


class Delivery:
    def __init__(self, delivery_id: int, city: str, street: str, number: int, postal_code: str, country: str):
        self.delivery_id = delivery_id
        self.city = city
        self.street = street
        self.number = number
        self.postal_code = postal_code
        self.country = country


class Basket:
    def __init__(self, order_id: int, clothes_id: int):
        self.order_id = order_id
        self.clothes_id = clothes_id

    def display_clothes(self, db_connection):
        cursor = db_connection.cursor()
        query = """
            SELECT Clothes.material, Clothes.size, Clothes.sex, Clothes.price
            FROM Basket
            JOIN Clothes ON Basket.clothes_id = Clothes.clothes_id
            WHERE Basket.order_id = %s AND Basket.clothes_id = %s
        """
        cursor.execute(query, (self.order_id, self.clothes_id))
        for row in cursor:
            print(f"Material: {row[0]}, Size: {row[1]}, Sex: {row[2]}, Price: {Decimal(row[3])}")
        cursor.close()


class Clothes:
    _all_clothes = []  # Private class variable to hold all clothes

    def __init__(self):
        self.clothes_id = None
        self.material = None
        self.size = None
        self.sex = None
        self.price = None
        self.collection_id = None
        Clothes._all_clothes.append(self)  # Add each new instance to the class variable

    @classmethod
    def print_all_clothes(cls):
        for clothes in cls._all_clothes:
            print(
                f"ID: {clothes.clothes_id}, Material: {clothes.material}, Size: {clothes.size}, "
                f"Sex: {clothes.sex}, Price: {clothes.price}, Collection ID: {clothes.collection_id}")

    @classmethod
    def get_clothes_by_id(cls, clothes_id):
        for clothes in cls._all_clothes:
            if clothes.clothes_id == clothes_id:
                return clothes
        return None

    @classmethod
    def fetch_clothes_from_db(cls, db_connection):
        cls._all_clothes.clear()
        db_connection.cursor.execute("SELECT clothes_id, material, size, sex, price, collection_id FROM Clothes")
        rows = db_connection.cursor.fetchall()
        for row in rows:
            cls.create_clothes(row[0], row[1], row[2], row[3], row[4], row[5])  # Use cls.create_clothes here

    @classmethod
    def refresh_clothes(cls, db_connection):
        cls.fetch_clothes_from_db(db_connection)

    @classmethod
    def create_clothes(cls, clothes_id, material, size, sex, price, collection_id):
        clothes = cls()
        clothes.clothes_id = clothes_id
        clothes.material = material
        clothes.size = size
        clothes.sex = sex
        clothes.price = price
        clothes.collection_id = collection_id
        return clothes


class Collection:
    _all_collections = []  # Private class variable to hold all collections

    def __init__(self):
        self.collection_id = None
        self.name = None
        self.start_date = None
        self.end_date = None
        Collection._all_collections.append(self)  # Add each new instance to the class

    @classmethod
    def print_all_collections(cls):
        for collection in cls._all_collections:
            print(
                f"ID: {collection.collection_id}, Name: {collection.name}, Start Date: {collection.start_date}, "
                f"End Date: {collection.end_date}")

    @classmethod
    def get_collection_by_id(cls, collection_id):
        for collection in cls._all_collections:
            if collection.collection_id == collection_id:
                return collection
        return None

    @classmethod
    def fetch_collections_from_db(cls, db_connection):
        cls._all_collections.clear()

        db_connection.cursor.execute("SELECT collection_id, name, start_date, end_date FROM Collections")
        rows = db_connection.cursor.fetchall()
        for row in rows:
            cls.create_collection(row[0], row[1], row[2], row[3])

    @classmethod
    def refresh_collections(cls, db_connection):
        cls.fetch_collections_from_db(db_connection)

    @classmethod
    def create_collection(cls, collection_id, name, start_date, end_date):
        collection = cls()
        collection.collection_id = collection_id
        collection.name = name
        collection.start_date = start_date
        collection.end_date = end_date
        return collection


class UI_App:
    def __init__(self):
        self.db = DB_Communication()
        self.user = None

    def login(self):
        user_login = input("Enter login: ")
        user_password = input("Enter password: ")

        try:
            self.db.cursor.execute("SELECT * FROM Users WHERE login = %s AND password = %s", (user_login,
                                                                                              user_password))
            user_data = self.db.cursor.fetchone()
            if user_data:
                current_user = User(*user_data, self.db)
                self.user = current_user
                print(f"Welcome, {current_user.name}")
                return True
            else:
                print("Login failed. Incorrect username or password.")
                return False
        except mysql.connector.Error as e:
            print(f"Error during login: {e}")
            return False

    def create_account(self):
        while True:
            user_login = input("Enter login: ")
            self.db.cursor.execute("SELECT login FROM Users WHERE login = %s", (user_login,))
            if self.db.cursor.fetchone():
                print("Login already exists. Please choose a different login.")
            else:
                break
        user_password = input("Enter password: ")
        user_email = input("Enter email: ")
        user_phone = input("Enter phone: ")
        user_name = input("Enter name: ")
        user_surname = input("Enter surname: ")
        user_role = input("Enter role (admin, employee, customer): ")

        # Ensure role is one of the accepted values
        if user_role not in ['admin', 'employee', 'customer']:
            print("Invalid role. Please enter 'admin', 'employee', or 'customer'.")
            return

        # Call the database procedure
        try:
            self.db.cursor.callproc('CreateUserAccount',
                                    [user_login, user_password, user_email, user_phone, user_name, user_surname,
                                     user_role])
            self.db.conn.commit()
            print("Account created successfully.")
            return True
        except mysql.connector.Error as e:
            print(f"Error in account creation: {e}")
            return False

    def main_menu(self):
        is_success = False
        while True:
            print("\n--- Main Menu ---")
            print("1: Create an Account")
            print("2: Login to an Account")
            print("3: Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                self.create_account()
            elif choice == '2':
                is_success = self.login()
                if is_success:
                    return True
            elif choice == '3':
                return False
            else:
                print("Invalid choice. Please try again.")
                collection = Collection()
                collection.fetch_collections_from_db(self.db)
                collection.print_all_collections()
                clothes = Clothes()
                clothes.fetch_clothes_from_db(self.db)
                clothes.print_all_clothes()

    def get_db_communication(self):
        return self.db

    def get_user(self):
        return self.user


def main():
    app = UI_App()
    is_logged = app.main_menu()
    if is_logged:
        user = app.get_user()
        user.user_menu()


if __name__ == "__main__":
    main()
