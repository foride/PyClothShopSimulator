from validation_utility import ValidationUtility
import sys
import mysql.connector


class User:
    def __init__(self, user_id: int, login: str, password: str, email: str, phone: str, name: str, surname: str,
                 role: str):
        self.user_id = user_id
        self.login = login
        self.password = password  # Note: Storing passwords in plain text is not secure
        self.email = email
        self.phone = phone
        self.name = name
        self.surname = surname
        self.role = role

    def user_menu(self, db):
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
                self.update_attributes(db)
            elif choice == '3':
                self.delete_account(db)
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

    def update_attributes(self, db):

        new_email = ValidationUtility.get_validated_input_varchar("Enter new email (or press Enter to skip): ", 255)
        new_phone = ValidationUtility.get_validated_input_varchar("Enter new phone (or press Enter to skip): ", 15)
        new_name = ValidationUtility.get_validated_input_varchar("Enter new name (or press Enter to skip): ", 45)
        new_surname = ValidationUtility.get_validated_input_varchar("Enter new surname (or press Enter to skip): ", 45)

        db.cursor.callproc('UpdateUserDetails', [self.user_id, new_email or self.email, new_phone or
                                                 self.phone, new_name or self.name, new_surname or self.surname])
        db.conn.commit()

        self.email = new_email if new_email else self.email
        self.phone = new_phone if new_phone else self.phone
        self.name = new_name if new_name else self.name
        self.surname = new_surname if new_surname else self.surname
        print("User details updated successfully.")

    def delete_account(self, db):
        confirmation = input("Are you sure you want to delete your account? (yes/no): ")
        if confirmation.lower() == 'yes':
            try:

                db.cursor.callproc('DeleteUserAccount', [self.user_id])
                db.conn.commit()
                print("Account deleted successfully.")
                return 3

            except mysql.connector.Error as e:
                print(f"Error during account deletion: {e}")
                sys.exit()
        else:
            print("Account deletion cancelled.")
