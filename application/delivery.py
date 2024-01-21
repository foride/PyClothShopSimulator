import mysql.connector
from validation_utility import ValidationUtility


class Delivery:
    _delivery_details = []

    def __init__(self):
        self.delivery_id = None
        self.city = None
        self.street = None
        self.number = None
        self.postal_code = None
        self.country = None
        Delivery._delivery_details.append(self)

    @classmethod
    def fetch_deliveries_by_user(cls, db_connection, user_id):
        cls._delivery_details.clear()
        query = """
                SELECT DISTINCT Delivery.delivery_id, Delivery.city, Delivery.street, Delivery.number, 
                Delivery.postal_code, Delivery.country FROM Delivery JOIN Orders ON 
                Delivery.delivery_id = Orders.delivery_id WHERE Orders.user_id = %s
            """

        db_connection.cursor.execute(query, (user_id,))
        rows = db_connection.cursor.fetchall()
        for row in rows:
            delivery = cls()
            (delivery.delivery_id, delivery.city, delivery.street, delivery.number,
             delivery.postal_code, delivery.country) = row

    @classmethod
    def print_delivery_details(cls):
        for delivery in cls._delivery_details:
            print(f"Delivery ID: {delivery.delivery_id}, City: {delivery.city}, Street: {delivery.street}, "
                  f"Number: {delivery.number}, Postal Code: {delivery.postal_code}, Country: {delivery.country}")

    def insert_new_delivery(self, db_connection):

        print("New order will be created with this delivery details")
        self.city = ValidationUtility.get_validated_input_varchar("Enter city: ", 100)
        self.street = ValidationUtility.get_validated_input_varchar("Enter street: ", 100)
        self.number = ValidationUtility.get_validated_input_integer("Enter number: ", 10)
        self.postal_code = ValidationUtility.get_validated_input_integer("Enter postal code: ", 15)
        self.country = ValidationUtility.get_validated_input_varchar("Enter country: ", 100)

        try:
            db_connection.cursor.execute(
                "INSERT INTO Delivery (city, street, number, postal_code, country) VALUES (%s, %s, %s, %s, %s)",
                (self.city, self.street, self.number, self.postal_code, self.country))
            db_connection.conn.commit()
            self.delivery_id = db_connection.cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Error in database operation: {e}")
        finally:
            print("The delivery details has been added to the database and will be visible to the user "
                  "after finalizing the basket.")
            return self.delivery_id

    @classmethod
    def select_delivery(cls):
        cls.print_delivery_details()
        try:
            selected_id = int(input("Enter the ID of the delivery you want to select: "))
        except ValueError:
            print("Invalid input. Please enter a numeric ID.")
            return None

        for delivery in cls._delivery_details:
            if delivery.delivery_id == selected_id:
                return selected_id
        print("No delivery found with the provided ID.")
        return None

    def menu(self, db_connection, user_id):
        while True:
            print("\nDelivery Management Menu:")
            print("1. Print Delivery Details")
            print("2. Select Saved Delivery Details")
            print("3. Insert New Delivery")
            print("4. Exit")
            self.fetch_deliveries_by_user(db_connection, user_id)
            choice = input("Enter your choice: ")

            if choice == "1":
                self.print_delivery_details()
            elif choice == "2":
                selected_delivery = self.select_delivery()
                if selected_delivery:
                    print("Selected delivery details:")
                    print(selected_delivery)
                    return selected_delivery
            elif choice == "3":
                self.insert_new_delivery(db_connection)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
