class Payment:
    def __init__(self):
        self.payment_id = None
        self.status = None
        self.payment_form = None
        self.payment_date = None
        self.payment_details = []

    def fetch_payments_by_user(self, db_connection, user_id):
        self.payment_details.clear()
        query = """
            SELECT DISTINCT Payments.payment_id, Payments.status, Payments.payment_form, Payments.date 
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
        self.status = "unpaid"

        while True:
            payment_form = input("Enter payment form (card, blik, transfer): ").lower()
            if payment_form in ["card", "blik", "transfer"]:
                self.payment_form = payment_form
                break
            else:
                print("Invalid input. Please enter card, blik, or transfer.")

        db_connection.cursor.execute(
            "INSERT INTO Payments (status, payment_form, date) VALUES (%s, %s, %s)",
            (self.status, self.payment_form, self.payment_date))
        db_connection.conn.commit()
        self.payment_id = db_connection.cursor.lastrowid
        print("The payment form has been added to the database and will be visible to the user after finalizing the "
              "basket.")
        return self.payment_id

    def select_saved_payment_details(self, payment_id):
        found_payment = None

        for payment_detail in self.payment_details:
            if payment_detail['payment_id'] == payment_id:
                found_payment = payment_detail
                break

        if found_payment:
            self.status = found_payment['status']
            self.payment_form = found_payment['payment_form']
            self.payment_date = found_payment['payment_date']
            return payment_id
        else:
            print("Payment details not found.")
            return None

    def menu(self, db_connection, user_id):
        while True:
            print("\n--- Payment options menu ----")
            print("1: Print Payment Details")
            print("2: Insert New Payment")
            print("3: Select Saved Payment Details")
            print("4: Exit")
            self.fetch_payments_by_user(db_connection, user_id)
            choice = input("Enter your choice: ")

            if choice == '1':
                self.print_payment_details()
            elif choice == '2':
                payment_id = self.insert_new_payment(db_connection)
                return payment_id
            elif choice == '3':
                payment_id = input("Enter payment ID: ")
                selected_payment = self.select_saved_payment_details(payment_id)
                if selected_payment:
                    print("Selected payment details:")
                    print(selected_payment)
                    return selected_payment
            elif choice == '4':
                print("Exiting the payment menu.")
                break
            else:
                print("Invalid choice. Please select a valid option (1-4).")
