from xml.sax.handler import all_properties
from flask import current_app as app

class Cart:
    def __init__(self, uid, sid, pid, quantity, price):
        self.uid = uid
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def get_all(uid):
        rows = app.db.execute('''
            SELECT *
            FROM Cart
            WHERE uid = :uid AND quantity > 0
            ORDER BY sid 
            ''',
                              uid = uid)
        return [Cart(*row) for row in rows]
    
    @staticmethod
    def get_total_price(uid):
        count = 0
        user_cart = Cart.get_all(uid)
        for item in user_cart:
            count += item.price * item.quantity
        return count
    
    @staticmethod
    def delete_item(uid, sid, pid):
        app.db.execute('''
            DELETE FROM Cart
            WHERE uid = :uid AND sid = :sid AND pid = :pid
            RETURNING uid
        ''',
                            uid=uid, sid=sid, pid=pid)
    
    @staticmethod
    def update_quantity(uid, sid, pid, quantity):
        app.db.execute('''
            UPDATE Cart
            SET quantity = :quantity
            WHERE uid = :uid AND sid = :sid AND pid = :pid
            RETURNING uid
        ''',
                            uid=uid, sid=sid, pid=pid, quantity=quantity)
    
    @staticmethod
    def check_status(uid):
        all_products = Cart.get_all(uid)
        total_price = Cart.get_total_price(uid)
        balance = app.db.execute('''
            SELECT balance
            FROM Users
            WHERE id = :id
        ''',
                            id=uid)
        if balance[0][0] < total_price:
            return -1
        else:
            for p in all_products:
                if_available = app.db.execute('''
                    SELECT quantity
                    FROM Sellers
                    WHERE uid = :uid AND pid = :pid
                ''',
                            uid=p.sid, pid=p.pid)
            if not if_available or if_available[0][0] < p.quantity:
                return -2
        return 0
    
    @staticmethod
    def clear_cart(uid):
        all_products = Cart.get_all(uid)
        for p in all_products:
            if p.quantity > 0:
                Cart.delete_item(uid, p.sid, p.pid)

    @staticmethod
    def get_price_by_id(sid, pid):
        rows = app.db.execute('''
        SELECT price
        FROM Sellers
        WHERE uid = :uid AND pid = :pid
        ''',
            uid=sid, pid=pid)
        return rows[0][0]

    @staticmethod
    def add_to_cart(uid, pid, sid, quantity):
        rows = app.db.execute('''
        SELECT *
        FROM Cart
        WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''',
            uid=uid, pid=pid, sid=sid)
        if rows:
            return -1
        price = Cart.get_price_by_id(sid, pid)
        app.db.execute('''
        INSERT INTO Cart(uid, sid, pid, quantity, price)
        VALUES (:uid, :sid, :pid, :quantity, :price)
        RETURNING uid
        ''',
            uid=uid, sid=sid, pid=pid, quantity=quantity, price=price)
        return 0
    
    @staticmethod
    def get_product_price_in_seller(pid, sid):
        rows = app.db.execute('''
        SELECT price
        FROM Sellers 
        WHERE uid = :uid AND pid = :pid
        ''',
            uid=sid, pid=pid)
        return rows[0][0]

    @staticmethod
    def get_product_price_in_cart(uid, pid, sid):
        rows = app.db.execute('''
        SELECT price
        FROM Cart
        WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''',
            uid=uid, pid=pid, sid=sid)
        return rows[0][0]

    @staticmethod
    def check_if_code_used(uid, code, status):
        rows = app.db.execute('''
        SELECT code
        FROM Code
        WHERE uid = :uid AND status = :status
        ''',
            uid=uid, status=status)
        for row in rows:
            if code == row[0]:
                return True
        return False

    @staticmethod
    def check_if_already_use_one_code(uid):
        rows = app.db.execute('''
        SELECT status
        FROM Code
        WHERE uid = :uid
        ''',
            uid=uid)
        for row in rows:
            if row[0] == 0:
                return True
        return False

    @staticmethod
    def apply_promotional_code(code, uid):
        if Cart.check_if_code_used(uid, code, 0) or Cart.check_if_code_used(uid, code, 1): # Applied for current cart or used in previous cart
            return -2
        if code == 'DUKE' or code == 'BLUEDEVIL' or code == 'YI' or code == 'YIFEI' or code == 'CHANG' or code == 'ZHEKUN':
            if Cart.check_if_already_use_one_code(uid):
                return -3
            all_products = Cart.get_all(uid)
            for product in all_products:
                seller_price = Cart.get_product_price_in_seller(product.pid, product.sid)
                app.db.execute('''
                UPDATE Cart
                SET price = 0.9 * price
                WHERE uid = :uid AND sid = :sid AND pid = :pid AND price = :price
                RETURNING uid
                ''',
                    uid=uid, sid=product.sid, pid=product.pid, price=seller_price)
            app.db.execute('''
            INSERT INTO Code(uid, code, status)
            VALUES (:uid, :code, :status)
            RETURNING uid
            ''',
                uid=uid, code=code, status=0)
            return 0
        else:
            return -1
    
    @staticmethod
    def cancel_code(uid, code):
        if not Cart.check_if_code_used(uid, code, 0):
            return -1
        all_products = Cart.get_all(uid)
        for product in all_products:
            price = Cart.get_product_price_in_seller(product.pid, product.sid)
            app.db.execute('''
                UPDATE Cart
                SET price = :price
                WHERE uid = :uid AND sid = :sid AND pid = :pid
                RETURNING uid
            ''',
                uid=uid, sid=product.sid, pid=product.pid, price=price)
        app.db.execute('''
        DELETE FROM Code
        WHERE uid = :uid AND code = :code AND status = :status
        RETURNING uid
        ''',
            uid=uid, code=code, status=0)
        return 0
    
    @staticmethod
    def update_code_status(uid):
        status = 0 # Applied
        rows = app.db.execute('''
        SELECT code
        FROM Code
        WHERE uid = :uid AND status = :status
        ''',
            uid=uid, status=status)
        if rows is not None:
            for row in rows:
                status = 1
                app.db.execute('''
                UPDATE Code
                SET status = :status
                WHERE uid = :uid AND code = :code
                RETURNING uid
                ''',
                    uid=uid, code=row[0], status=status)
    