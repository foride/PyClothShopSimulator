import mysql.connector


class DB_Communication:
    def __init__(self):
        self.conn = None
        self.cursor = None
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
