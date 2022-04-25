from flask import current_app as app
from .inventory import Inventory
from .user import User
from flask import flash


class Order:
    def __init__(self, id, buyer_uid, seller_uid, pid, quantity, price, time_purchased, fulfilled):
        self.id = id
        self.buyer = buyer_uid
        self.seller = seller_uid
        self.pid = pid
        self.quantity = quantity
        self.price = price
        self.time_purchased = time_purchased
        self.fulfilled = fulfilled


    @staticmethod
    def get(id):
        rows = app.db.execute(
            '''
            SELECT id, buyer_uid, seller_uid, pid, quantity, price, time_purchased, fulfilled
            FROM Orders
            WHERE id = :id
            ''', id=id)
        return Order(*(rows[0])) if rows else None
    

    @staticmethod
    def get_all_by_buyer_uid_since(buyer_uid, since):
        rows = app.db.execute(
            '''
            SELECT id, buyer_uid, seller_uid, pid, quantity, price, time_purchased, fulfilled
            FROM Orders
            WHERE buyer_uid = :buyer_uid
            AND time_purchased >= :since
            ORDER BY time_purchased DESC
            ''', buyer_uid=buyer_uid, since=since)
        return [Order(*row) for row in rows]

    
    @staticmethod
    def search_by_item(search, bid):
        rows = app.db.execute(
            '''
            SELECT Orders.id, buyer_uid, seller_uid, Orders.pid, quantity, price, time_purchased, fulfilled
            FROM Orders, Products
            WHERE Orders.buyer_uid = :bid AND Orders.pid = Products.id AND LOWER(Products.name) LIKE :search
            ''', search='%'+search.lower()+'%', bid=bid)
        return [Order(*row) for row in rows]
    

    @staticmethod
    def search_by_seller(search, bid):
        rows = app.db.execute(
            '''
            SELECT Orders.id, buyer_uid, seller_uid, pid, quantity, price, time_purchased, fulfilled
            FROM Orders, Users
            WHERE Orders.buyer_uid = :bid AND Orders.seller_uid = Users.id AND LOWER(firstname) LIKE :search
            ''', search='%'+search.lower()+'%', bid=bid)
        return [Order(*row) for row in rows]

    @staticmethod
    def get_all_by_seller(sid):
        rows = app.db.execute(
            '''
            SELECT Orders.*, Products.name AS product_name
            FROM Orders INNER JOIN Products on Orders.pid=Products.id
            WHERE Orders.seller_uid =:seller_uid
            ORDER BY Orders.time_purchased DESC;
            ''', seller_uid=sid)
        return rows

    @staticmethod
    def update_fulfill(id, fulfilled):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Orders
            WHERE id = :id
            ''', id=id)

        for row in rows:
            if row.fulfilled:
                flash('Invalid Operation, Order Already Fulfilled')
                continue

            buyer_balance = User.get_balance_by_id(row.buyer_uid) - row.quantity * row.price
            if buyer_balance < 0:
                flash('Invalid Orders, Buyer Having Insufficient Funds')
            else:
                res = Inventory.reduce_quantity(row.seller_uid, row.pid, row.quantity)
                if not res:
                    flash('Invalid Orders, Products Out Of Stock')
                else:
                    app.db.execute(
                        '''
                        UPDATE Orders
                        SET fulfilled =:fulfilled
                        WHERE id =:id
                        ''', id=id, fulfilled=fulfilled)

                    for row in rows:
                        seller_balance = User.get_balance_by_id(row.seller_uid) + row.quantity * row.price
                        User.change_balance_by_id(row.seller_uid, seller_balance)
                        buyer_balance = User.get_balance_by_id(row.buyer_uid) - row.quantity * row.price
                        User.change_balance_by_id(row.buyer_uid, buyer_balance)
                flash('Orders Fulfilled Successfully')
        return rows

    @staticmethod
    def get_order_analytics(sid):
        rows = app.db.execute(
            '''
            SELECT Orders.pid, Products.name AS product_name, Orders.quantity, Orders.price
            FROM Orders INNER JOIN Products on Orders.pid=Products.id
            WHERE Orders.seller_uid =:seller_uid
            ORDER BY Orders.quantity DESC
            LIMIT 10
            ''', seller_uid=sid)

        return rows
    
    @staticmethod
    def add_order(bid, sid, pid, quantity, price, time):
        row = app.db.execute('''SELECT MAX(Orders.id) as MAX_ID FROM Orders''')
        id = row[0][0] + 1

        app.db.execute(
            """ INSERT INTO Orders(id, buyer_uid, seller_uid, pid, quantity, price, time_purchased, fulfilled)
            VALUES(:id, :buyer_uid, :seller_uid, :pid, :quantity, :price, :time_purchased, :fulfilled)
            RETURNING *
            """, id=id, buyer_uid = bid, seller_uid = sid, pid = pid, quantity = quantity, price = price, time_purchased = time, fulfilled = False)
        
        return True
    
