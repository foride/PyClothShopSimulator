class Collection:
    _all_collections = []

    def __init__(self):
        self.collection_id = None
        self.name = None
        self.start_date = None
        self.end_date = None
        Collection._all_collections.append(self)

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
