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
    orders = {}

    @classmethod
    def fetch_orders_by_user(cls, db_connection, user_id):
        query = """
                SELECT Orders.order_id, Orders.amount, 
                       Payments.status, Payments.payment_form, Payments.date,
                       Delivery.city, Delivery.street, Delivery.number, Delivery.postal_code, Delivery.country,
                       Clothes.material, Clothes.size, Clothes.sex, Clothes.price,
                       Collections.name, Collections.start_date, Collections.end_date
                FROM Orders
                JOIN Payments ON Orders.payment_id = Payments.payment_id
                JOIN Delivery ON Orders.delivery_id = Delivery.delivery_id
                JOIN Basket ON Orders.order_id = Basket.order_id
                JOIN Clothes ON Basket.clothes_id = Clothes.clothes_id
                JOIN Collections ON Clothes.collection_id = Collections.collection_id
                WHERE Orders.user_id = %s
                """

        db_connection.cursor.execute(query, (user_id,))
        raw_orders = db_connection.cursor.fetchall()

        if not cls.orders:
            for row in raw_orders:
                order_id = row[0]
                if order_id not in cls.orders:
                    cls.orders[order_id] = {
                        'order_id': order_id,
                        'amount': row[1],
                        'payment_details': {'status': row[2], 'payment_form': row[3], 'date': row[4]},
                        'delivery_details': {'city': row[5], 'street': row[6], 'number': row[7], 'postal_code': row[8],
                                             'country': row[9]},
                        'clothes': [],
                        'collections': []
                    }
                clothes_details = {'material': row[10], 'size': row[11], 'sex': row[12], 'price': row[13]}
                collection_details = {'name': row[14], 'start_date': row[15], 'end_date': row[16]}
                cls.orders[order_id]['clothes'].append(clothes_details)
                cls.orders[order_id]['collections'].append(collection_details)
        else:
            updated_orders = {}

            for row in raw_orders:
                order_id = row[0]
                if order_id not in updated_orders:
                    updated_orders[order_id] = {
                        'order_id': order_id,
                        'amount': row[1],
                        'payment_details': {'status': row[2], 'payment_form': row[3], 'date': row[4]},
                        'delivery_details': {'city': row[5], 'street': row[6], 'number': row[7], 'postal_code': row[8],
                                             'country': row[9]},
                        'clothes': [],
                        'collections': []
                    }
                clothes_details = {'material': row[10], 'size': row[11], 'sex': row[12], 'price': row[13]}
                collection_details = {'name': row[14], 'start_date': row[15], 'end_date': row[16]}
                updated_orders[order_id]['clothes'].append(clothes_details)
                updated_orders[order_id]['collections'].append(collection_details)

            cls.orders = updated_orders

    @classmethod
    def print_all_orders_by_user(cls):
        for order_id, order_details in cls.orders.items():
            print(f"Order ID: {order_id}, Amount: {order_details['amount']}")
            payment = order_details['payment_details']
            print(
                f"Payment Status: {payment['status']}, Payment Form: {payment['payment_form']}, "
                f"Payment Date: {payment['date']}")
            delivery = order_details['delivery_details']
            print(
                f"Delivery Address: {delivery['city']}, {delivery['street']} {delivery['number']}, "
                f"{delivery['postal_code']}, {delivery['country']}")
            counter = 0
            for clothes in order_details['clothes']:
                counter += 1
                print(
                    f"{counter}: Material: {clothes['material']}, Size: {clothes['size']}, Sex: {clothes['sex']}, "
                    f"Price: {clothes['price']}")
            counter = 0
            for collection in order_details['collections']:
                counter += 1
                print(
                    f"{counter}: {collection['name']}, Collection Start Date: {collection['start_date']}, "
                    f"Collection End Date: {collection['end_date']}")

    @classmethod
    def cancel_order(cls, db_connection, order_id):

        try:

            db_connection.cursor.callproc("CancelOrder", [order_id])
            db_connection.conn.commit()
            print("Order canceled successfully.")

        except mysql.connector.Error as e:
            print(f"Error during order cancellation: {e}")

    @classmethod
    def print_order_details(cls, order_id):
        int_order_id = int(order_id)
        order_details = cls.orders.get(int_order_id)
        counter = 0
        if order_details:
            print(f"Order ID: {order_id}, Amount: {order_details['amount']}")
            payment = order_details['payment_details']
            print(f"Payment Status: {payment['status']}, Payment Form: {payment['payment_form']}, Payment Date: "
                  f"{payment['date']}")
            delivery = order_details['delivery_details']
            print(f"Delivery Address: {delivery['city']}, {delivery['street']} {delivery['number']}, "
                  f"{delivery['postal_code']}, {delivery['country']}")
            for clothes in order_details['clothes']:
                counter += 1
                print(f"{counter}: Material: {clothes['material']}, Size: {clothes['size']}, Sex: {clothes['sex']}, "
                      f"Price: {clothes['price']}")
            counter = 0
            for collection in order_details['collections']:
                counter += 1
                print(f"{counter}: {collection['name']}, Collection Start Date: {collection['start_date']}, "
                      f"Collection End Date: {collection['end_date']}")
        else:
            print(f"No details found for Order ID: {order_id}")


class Payment:
    def __init__(self):
        self.payment_id = None
        self.status = None
        self.payment_form = None
        self.payment_date = None
        self.payment_details = []

    def fetch_payments_by_user(self, db_connection, user_id):
        query = """
            SELECT Payments.payment_id, Payments.status, Payments.payment_form, Payments.date 
            FROM Payments 
            JOIN Orders ON Payments.payment_id = Orders.payment_id 
            WHERE Orders.user_id = %s
        """
        db_connection.cursor.execute(query, (user_id,))
        payments = db_connection.cursor.fetchall()

        for payment in payments:
            payment_detail = {
                'payment_id': payment[0],
                'status': payment[1],
                'payment_form': payment[2],
                'payment_date': payment[3]
            }
            self.payment_details.append(payment_detail)

    def print_payment_details(self):
        for detail in self.payment_details:
            print(detail)

    def insert_new_payment(self, db_connection):
        self.status = input("Enter status (paid, unpaid, cancelled): ")
        self.payment_form = input("Enter payment form (card, blik, transfer): ")

        db_connection.cursor.execute(
            "INSERT INTO Payments (status, payment_form, date) VALUES (%s, %s, %s)",
            (self.status, self.payment_form, self.payment_date))
        db_connection.conn.commit()
        self.payment_id = db_connection.cursor.lastrowid  # Assuming auto-increment ID

    def menu(self, db_connection, user_id):
        while True:
            print("\n--- Payment options menu ----")
            print("1: Fetch Payments by User")
            print("2: Print Payment Details")
            print("3: Insert New Payment")
            print("4: Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.fetch_payments_by_user(db_connection, user_id)
                print("Payments fetched for the user.")
            elif choice == '2':
                self.print_payment_details()
            elif choice == '3':
                self.insert_new_payment(db_connection)
                print("New payment inserted.")
            elif choice == '4':
                print("Exiting the payment menu. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1-4).")


class Delivery:
    def __init__(self):
        self.delivery_id = None
        self.city = None
        self.street = None
        self.number = None
        self.postal_code = None
        self.country = None
        self.delivery_details = []

    @staticmethod
    def fetch_deliveries_by_user(self, db_connection, user_id):

        query = """
                SELECT Delivery.delivery_id, Delivery.city, Delivery.street, Delivery.number, Delivery.postal_code,
                 Delivery.country FROM Delivery JOIN Orders ON Delivery.delivery_id = Orders.delivery_id
                WHERE Orders.user_id = %s
            """
        db_connection.cursor.execute(query, (user_id,))
        deliveries = db_connection.cursor.fetchall()

        for delivery in deliveries:
            delivery_detail = {
                'delivery_id': delivery[0],
                'city': delivery[1],
                'street': delivery[2],
                'number': delivery[3],
                'postal_code': delivery[4],
                'country': delivery[5]
            }
            self.delivery_details.append(delivery_detail)

    def print_delivery_details(self):
        for deliver in self.delivery_details:
            print(deliver)

    def insert_new_delivery(self, db_connection):
        self.city = input("Enter city: ")
        self.street = input("Enter street: ")
        try:
            self.number = int(input("Enter number: "))  # Convert to integer
            self.postal_code = int(input("Enter postal code: "))  # Convert to integer
        except ValueError:
            print("Number and postal code must be integers.")
            return
        self.country = input("Enter country: ")

        try:
            db_connection.cursor.execute(
                "INSERT INTO Delivery (city, street, number, postal_code, country) VALUES (%s, %s, %s, %s, %s)",
                (self.city, self.street, self.number, self.postal_code, self.country))
            db_connection.conn.commit()
            self.delivery_id = db_connection.cursor.lastrowid  # Assuming auto-increment ID
        except mysql.connector.Error as e:
            print(f"Error in database operation: {e}")
        finally:
            print("The record has been added to the database.")

    def menu(self, db_connection, user_id):
        while True:
            print("\nDelivery Management Menu:")
            print("1. Fetch Deliveries by User")
            print("2. Print Delivery Details")
            print("3. Insert New Delivery")
            print("4. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.fetch_deliveries_by_user(db_connection, user_id)
            elif choice == "2":
                self.print_delivery_details()
            elif choice == "3":
                self.insert_new_delivery(db_connection)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")


class Basket:

    def __init__(self, db_connection, order_id=None):
        # Assign order_id if provided, else assign a new one

        self.order_id = order_id if order_id is not None else self.assign_order_id(db_connection)
        self.calculated_price = None

    def assign_order_id(self, db_connection):

        query = "SELECT MAX(order_id) FROM Orders"
        db_connection.cursor.execute(query)
        result = db_connection.cursor.fetchone()
        latest_order_id = result[0] if result[0] is not None else 0
        return latest_order_id + 1

    def add_clothes(self, db_connection, clothes_id: int):
        # Insert query into basket table with selected clothes_id
        query = "INSERT INTO Basket (order_id, clothes_id) VALUES (%s, %s)"
        db_connection.cursor.execute(query, (self.order_id, clothes_id))
        db_connection.conn.commit()

    def calculate_price(self, db_connection):
        # Calculate the total price of clothes in the basket

        query = """
            SELECT SUM(Clothes.price) 
            FROM Clothes 
            JOIN Basket ON Clothes.clothes_id = Basket.clothes_id 
            WHERE Basket.order_id = %s
        """
        db_connection.cursor.execute(query, (self.order_id,))
        self.calculated_price = db_connection.cursor.fetchone()[0]

    def finalize_basket(self, db_connection):
        # Confirm payment and finalize the order
        print(f"Total price: {self.calculated_price}")
        confirmation = input("Do you confirm to pay? (yes/no): ")
        if confirmation.lower() == 'yes':
            # Finalize the order logic here
            # Implement order finalization query
            print("Order finalized successfully.")
        else:
            print("Order not finalized.")


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

    def display_clothes(self, db_connection):

        query = """
            SELECT Clothes.material, Clothes.size, Clothes.sex, Clothes.price
            FROM Basket
            JOIN Clothes ON Basket.clothes_id = Clothes.clothes_id
            WHERE Basket.order_id = %s AND Basket.clothes_id = %s
        """
        db_connection.cursor.execute(query, (self.order_id, self.clothes_id))
        for row in db_connection.cursor:
            print(f"Material: {row[0]}, Size: {row[1]}, Sex: {row[2]}, Price: {Decimal(row[3])}")

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

    @classmethod
    def display_clothes_by_price(cls, db_connection):

        sort_order = input("Enter sort order (asc/desc): ")

        # Call the stored procedure
        db_connection.cursor.callproc('DisplayProductsByPrice', [sort_order])

        # Print the results
        for result in db_connection.cursor.stored_results():
            for row in result.fetchall():
                print(row)

    @classmethod
    def display_clothes_by_collection(cls, db_connection):
        sort_order = input("Enter sort order (newest/oldest): ").lower()

        try:

            if sort_order in ['newest', 'oldest']:
                db_connection.cursor.callproc('DisplayProductsByCollection', [sort_order])

                for result in db_connection.cursor.stored_results():
                    for row in result.fetchall():
                        print(row)
            else:
                print("Invalid sort order. Please use 'newest' or 'oldest'.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            print("display_clothes_by_collection success")

    @classmethod
    def search_products(cls, db_connection):
        material = input("Enter material (or leave blank): ")
        size = input("Enter size (or leave blank): ")
        min_price = input("Enter minimum price (or leave blank): ")
        max_price = input("Enter maximum price (or leave blank): ")
        sex = input("Enter sex (male/female/unisex or leave blank): ")

        # Convert empty strings to None
        material = None if material == "" else material
        size = None if size == "" else size
        min_price = None if min_price == "" else float(min_price)
        max_price = None if max_price == "" else float(max_price)
        sex = None if sex == "" else sex

        try:

            db_connection.cursor.callproc('SearchProducts', [material, size, min_price, max_price, sex])

            for result in db_connection.cursor.stored_results():
                for row in result.fetchall():
                    print(row)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            print("search_products success")


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

    def login_menu(self):
        while True:
            print("\n--- Login Menu ---")
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

                """ order tests
                order = Order(3)
                order.fetch_orders_by_user(self.db, 3)
                order.print_order_details(4)
                """

                """ payment tests
                payment = Payment()
                payment.fetch_payment_details(self.db, 2)
                payment.print_payment_details()
                payment.insert_new_payment(self.db)
                payment.fetch_payment_details(self.db, 6)
                payment.print_payment_details()
                """

                """ delivery tests
                dv = Delivery()
                dv.fetch_delivery_attributes(self.db, 3)
                dv.print_delivery_details()
                dv.insert_new_delivery(self.db)
                """

                """ collection tests
                collection = Collection()
                collection.fetch_collections_from_db(self.db)
                collection.print_all_collections()
                clothes = Clothes()
                clothes.fetch_clothes_from_db(self.db)
                clothes.print_all_clothes()
                """

    def main_menu(self):

        while True:
            print("\n--- Main Menu ---")
            print("1) Account")
            print("2) Orders")
            print("3) Basket")
            print("4) Clothes")
            print("5) Log out")

            choice = input("Select an option: ")

            if choice == "1":
                print("Account menu selected")
                self.user.user_menu()
            elif choice == "2":
                print("Order menu selected")
                self.order_menu()
            elif choice == "3":
                print("Basket menu selected")
            elif choice == "4":
                print("Clothes menu selected")
                self.clothes_menu()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def order_menu(self):
        orders = Order()
        while True:
            print("\n--- Order Menu ---")
            print("1: View all Orders")
            print("2: Cancel Selected Order")
            print("3: Display Selected Order Details")
            print("4: Exit")
            orders.fetch_orders_by_user(self.db, self.user.user_id)
            choice = input("Enter your choice: ")

            if choice == '1':
                orders.print_all_orders_by_user()
            elif choice == '2':
                order_id = input("Enter the Order ID to cancel: ")
                orders.cancel_order(self.db, order_id)
            elif choice == '3':
                order_id = input("Enter the Order ID to view details: ")
                orders.print_order_details(order_id)
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def basket_menu(self):

        # baskets = Basket(self.db, )
        # uzytkonwikowi wyswietlaja sie dostepne ordery do zaplacenia i baskety
        # moze stworzyc nowy basket
        # zamysl jest aby returnowac wybrane delivery, payment, order_id i tutaj oplacac go - czyli 4 do wyjebania XD
        # a potem input walidacja i elo
        delivery = Delivery()
        payment = Payment()

        while True:

            print("\n--- Basket Menu ----")
            print("1: Edit the basket")
            print("2: Edit the shipping options")
            print("3: Edit the payment options")
            print("4: Create an order")
            print("5: Finalize the order")
            print("6: Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                print("xd")

            elif choice == '2':
                delivery.menu(self.db, self.user.user_id)

            elif choice == '3':
                payment.menu(self.db, self.user.user_id)

            elif choice == '4':


            elif choice == '5':
                print("to do")

            elif choice == '6':
                print("Exiting the menu. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1-6).")

    def clothes_menu(self):
        clothes = Clothes()
        clothes.fetch_clothes_from_db(self.db)
        while True:
            print("\n--- Clothes Menu ----")
            print("1: View all Clothes")
            print("2. Display Clothes by Price")
            print("3. Display Clothes by Collection")
            print("4. Search clothes with filters")
            print("5. Exit")
            clothes.refresh_clothes(self.db)
            choice = input("Enter your choice: ")

            if choice == '1':
                clothes.print_all_clothes()
            elif choice == '2':
                clothes.display_clothes_by_price(self.db)
            elif choice == '3':
                clothes.display_clothes_by_collection(self.db)
            elif choice == '4':
                clothes.search_products(self.db)
            elif choice == '5':
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1-6).")


def main():
    is_logged = True
    app = UI_App()
    while is_logged:
        is_logged = app.login_menu()
        if is_logged:
            app.main_menu()


if __name__ == "__main__":
    main()
