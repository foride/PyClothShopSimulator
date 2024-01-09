from decimal import Decimal


class Basket:

    def __init__(self, db_connection, user_id, order_id=None):

        self.db_connection = db_connection
        db_connection.cursor.callproc("addDefaultOrder", [user_id, 0])
        self.db_connection.conn.commit()
        db_connection.cursor.execute("SELECT MAX(order_id) FROM Orders")
        self.order_id = db_connection.cursor.fetchone()[0]
        self.calculated_price = None

    def assign_order_id(self):

        query = "SELECT MAX(order_id) FROM Orders"
        self.db_connection.cursor.execute(query)
        result = self.db_connection.cursor.fetchone()
        latest_order_id = result[0] if result[0] is not None else 0
        return latest_order_id + 1

    def add_clothes(self, clothes_id: int):
        print(f"order_id {self.order_id}")
        query = "INSERT INTO Basket (order_id, clothes_id) VALUES (%s, %s)"
        self.db_connection.cursor.execute(query, (self.order_id, clothes_id))
        self.db_connection.conn.commit()

    def calculate_price(self):

        query = """
            SELECT SUM(Clothes.price) 
            FROM Clothes 
            JOIN Basket ON Clothes.clothes_id = Basket.clothes_id 
            WHERE Basket.order_id = %s
        """
        self.db_connection.cursor.execute(query, (self.order_id,))
        self.calculated_price = self.db_connection.cursor.fetchone()[0]

    def display_clothes(self):

        query = """
            SELECT Clothes.material, Clothes.size, Clothes.sex, Clothes.price
            FROM Basket
            JOIN Clothes ON Basket.clothes_id = Clothes.clothes_id
            WHERE Basket.order_id = %s
        """
        self.db_connection.cursor.execute(query, (self.order_id,))
        for row in self.db_connection.cursor:
            print(f"Material: {row[0]}, Size: {row[1]}, Sex: {row[2]}, Price: {Decimal(row[3])}")

    def remove_clothes(self, clothes_id: int):
        # Remove the specified clothes from the basket
        query = "DELETE FROM Basket WHERE order_id = %s AND clothes_id = %s"
        self.db_connection.cursor.execute(query, (self.order_id, clothes_id))
        self.db_connection.conn.commit()

    def view_edit_basket(self):
        while True:
            print("\nCurrent basket:")
            self.display_clothes()
            self.calculate_price()
            print(f"Price of the basket: {self.calculated_price}")

            print("\n1: Add Clothes")
            print("2: Remove Clothes")
            print("3: Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                clothes_id = int(input("Enter Clothes ID to add: "))
                self.add_clothes(clothes_id)
            elif choice == '2':
                clothes_id = int(input("Enter Clothes ID to remove: "))
                self.remove_clothes(clothes_id)
            elif choice == '3':
                return self.order_id, self.calculated_price
            else:
                print("Invalid choice. Please try again.")
