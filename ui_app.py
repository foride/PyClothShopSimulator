from validation_utility import ValidationUtility
from security_utility import SecurityUtility
from db_communication import DB_Communication
from user import User
from payment import Payment
from delivery import Delivery
from basket import Basket
from order import Order
from clothes import Clothes
import mysql.connector


class UI_App:
    def __init__(self):
        self.db = DB_Communication()
        self.user = None

    def login(self):
        user_login = ValidationUtility.get_validated_input_varchar("Enter login: ", 20)
        user_password = ValidationUtility.get_validated_input_varchar("Enter password: ", 20)
        hashed_password = SecurityUtility.hash_password(user_password)

        try:
            self.db.cursor.execute("SELECT * FROM Users WHERE login = %s AND password = %s", (user_login,
                                                                                              user_password))
            user_data = self.db.cursor.fetchone()
            if user_data:
                current_user = User(*user_data)
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
            user_login = ValidationUtility.get_validated_input_varchar("Enter login: ", 20)
            self.db.cursor.execute("SELECT login FROM Users WHERE login = %s", (user_login,))
            if self.db.cursor.fetchone():
                print("Login already exists. Please choose a different login.")
            else:
                break
        user_password = ValidationUtility.get_validated_input_varchar("Enter password: ", 20)
        hashed_password = SecurityUtility.hash_password(user_password)
        user_email = ValidationUtility.get_validated_input_varchar("Enter email: ", 255)
        user_phone = ValidationUtility.get_validated_input_varchar("Enter phone: ", 15)
        user_name = ValidationUtility.get_validated_input_varchar("Enter name: ", 45)
        user_surname = ValidationUtility.get_validated_input_varchar("Enter surname: ", 45)
        user_role = "customer"
        # user_role = ValidationUtility.get_validated_input_varchar("Enter role (admin, employee, customer): ", 20)

        if user_role not in ['admin', 'employee', 'customer']:
            print("Invalid role. Please enter 'admin', 'employee', or 'customer'.")
            return

        try:
            self.db.cursor.callproc('CreateUserAccount',
                                    [user_login, hashed_password, user_email, user_phone, user_name, user_surname,
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
                self.user.user_menu(self.db)
            elif choice == "2":
                print("Order menu selected")
                self.order_menu()
            elif choice == "3":
                self.basket_menu()
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

        basket = Basket(self.db, self.user.user_id)
        delivery = Delivery()
        payment = Payment()
        selected_payment = {}
        selected_delivery = {}
        order_id = 0
        total_cost = 0

        while True:

            print("\n--- Basket Menu ----")
            print("1: Edit the basket")
            print("2: Edit the shipping options")
            print("3: Edit the payment options")
            print("4: Finalize the order")
            print("5: Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                order_id, total_cost = basket.view_edit_basket()

            elif choice == '2':
                selected_delivery = delivery.menu(self.db, self.user.user_id)

            elif choice == '3':
                selected_payment = payment.menu(self.db, self.user.user_id)

            elif choice == '4':
                Order.update_order_attributes(self.db, order_id, total_cost, selected_payment, selected_delivery)

            elif choice == '5':
                print("Exiting the menu.")
                break
            else:
                print("Invalid choice. Please select a valid option (1-5).")

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
                order = input("Enter 'asc' for ascending or 'desc' for descending order of price: ").strip().lower()
                ascending = True if order == 'asc' else False
                clothes.print_sorted_by_price(ascending)
            elif choice == '3':
                order = input("Enter 'newest' for newest first or "
                              "'oldest' for oldest first in collection date: ").strip().lower()
                newest_first = True if order == 'newest' else False
                clothes.print_sorted_by_collection_date(newest_first)
            elif choice == '4':
                clothes.print_filtered_clothes()
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
