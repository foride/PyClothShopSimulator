class Clothes:
    _all_clothes = []

    def __init__(self):
        self.clothes_id = None
        self.material = None
        self.size = None
        self.sex = None
        self.price = None
        self.collection_id = None
        self.collection_name = None
        self.collection_start_date = None
        self.collection_end_date = None
        Clothes._all_clothes.append(self)

    @classmethod
    def print_all_clothes(cls):
        for clothes in cls._all_clothes:
            print(
                f"ID: {clothes.clothes_id}, Material: {clothes.material}, Size: {clothes.size}, "
                f"Sex: {clothes.sex}, Price: {clothes.price}, Collection: {clothes.collection_name}, "
                f"Start Date: {clothes.collection_start_date}, End Date: {clothes.collection_end_date}")

    @classmethod
    def get_clothes_by_id(cls, clothes_id):
        for clothes in cls._all_clothes:
            if clothes.clothes_id == clothes_id:
                return clothes
        return None

    @classmethod
    def fetch_clothes_from_db(cls, db_connection):
        cls._all_clothes.clear()
        query = """
            SELECT c.clothes_id, c.material, c.size, c.sex, c.price, col.name, col.start_date, col.end_date 
            FROM Clothes c
            JOIN Collections col ON c.collection_id = col.collection_id
            """
        db_connection.cursor.execute(query)
        rows = db_connection.cursor.fetchall()
        for row in rows:
            cls.create_clothes_with_collection(row)  # Modified to handle collection details

    @classmethod
    def create_clothes_with_collection(cls, row):
        clothes = cls()
        clothes.clothes_id, clothes.material, clothes.size, clothes.sex, clothes.price, \
            clothes.collection_name, clothes.collection_start_date, clothes.collection_end_date = row

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
    def print_sorted_by_price(cls, ascending=True):
        sorted_clothes = sorted(cls._all_clothes, key=lambda x: x.price, reverse=not ascending)
        for clothes in sorted_clothes:
            print(
                f"ID: {clothes.clothes_id}, Material: {clothes.material}, Size: {clothes.size}, "
                f"Sex: {clothes.sex}, Price: {clothes.price}, Collection: {clothes.collection_name}, "
                f"Start Date: {clothes.collection_start_date}, End Date: {clothes.collection_end_date}")

    @classmethod
    def print_sorted_by_collection_date(cls, newest_first=True):
        # Sort based on collection's start_date
        sorted_clothes = sorted(cls._all_clothes, key=lambda x: x.collection_start_date, reverse=newest_first)

        for clothes in sorted_clothes:
            print(
                f"ID: {clothes.clothes_id}, Material: {clothes.material}, Size: {clothes.size}, "
                f"Sex: {clothes.sex}, Price: {clothes.price}, Collection: {clothes.collection_name}, "
                f"Start Date: {clothes.collection_start_date}, End Date: {clothes.collection_end_date}")

    @classmethod
    def print_filtered_clothes(cls):
        material = input("Enter material (or leave blank): ").strip().lower()
        size = input("Enter size (or leave blank): ").strip().lower()
        min_price = input("Enter minimum price (or leave blank): ").strip()
        max_price = input("Enter maximum price (or leave blank): ").strip()
        sex = input("Enter sex (male/female/unisex or leave blank): ").strip().lower()

        # Convert min_price and max_price to float, handle empty inputs
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None

        for clothes in cls._all_clothes:
            if (not material or clothes.material.lower() == material) and \
                    (not size or clothes.size.lower() == size) and \
                    (not sex or clothes.sex.lower() == sex) and \
                    (min_price is None or clothes.price >= min_price) and \
                    (max_price is None or clothes.price <= max_price):
                print(
                    f"ID: {clothes.clothes_id}, Material: {clothes.material}, Size: {clothes.size}, "
                    f"Sex: {clothes.sex}, Price: {clothes.price}, Collection: {clothes.collection_name}, "
                    f"Start Date: {clothes.collection_start_date}, End Date: {clothes.collection_end_date}")
