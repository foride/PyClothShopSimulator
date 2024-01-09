import mysql.connector


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
            print()
            print(f"Order ID: {order_id}, Amount: {order_details['amount']}")
            payment = order_details['payment_details']
            print(
                f"Payment Status: {payment['status']}, Payment Form: {payment['payment_form']}, "
                f"Payment Date: {payment['date']}")
            delivery = order_details['delivery_details']
            print(
                f"Delivery Address: {delivery['city']}, {delivery['street']} {delivery['number']}, "
                f"{delivery['postal_code']}, {delivery['country']}")
            clothes_index = 0
            collections_index = 0

            while clothes_index < len(order_details['clothes']) and collections_index < len(
                    order_details['collections']):
                clothes = order_details['clothes'][clothes_index]
                collection = order_details['collections'][collections_index]

                print(
                    f"Material: {clothes['material']}, Size: {clothes['size']}, Sex: {clothes['sex']}, "
                    f"Price: {clothes['price']}")

                print(
                    f"{collection['name']}, Collection Start Date: {collection['start_date']}, "
                    f"Collection End Date: {collection['end_date']}")

                clothes_index += 1
                collections_index += 1

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

    @staticmethod
    def add_new_order(db_connection, amount, user_id, payment_id, delivery_id):
        try:
            db_connection.cursor.callproc("addOrder", [amount, user_id, payment_id, delivery_id])
            db_connection.conn.commit()
            print("New order added successfully.")
        except mysql.connector.Error as e:
            print(f"Error during order addition: {e}")

    @staticmethod
    def update_order_attributes(db_connection, order_id, new_amount, new_payment_id, new_delivery_id):
        try:
            db_connection.cursor.callproc("updateOrder",
                                          [order_id, new_amount, new_payment_id, new_delivery_id])
            db_connection.conn.commit()
            print("Order attributes updated successfully.")
        except mysql.connector.Error as e:
            print(f"Error during order attribute update: {e}")
