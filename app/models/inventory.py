from flask import current_app as app
from unicodedata import category
from flask import render_template
from flask_login import current_user

class Inventory:
    def __init__(self, uid, pid, quantity, price):
        self.uid = uid
        self.pid = pid
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def get_all_by_user(uid):
        rows = app.db.execute(
            '''
            SELECT Sellers.uid, Sellers.pid, Products.name, Sellers.quantity, Sellers.price
            FROM Sellers INNER JOIN Products on Sellers.pid=Products.id
            WHERE Sellers.uid =:uid
            ORDER BY uid, pid;
            ''', uid=uid)
        return rows
    

    @staticmethod
    def check_is_seller(uid):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Sellers
            WHERE uid = :uid
            ''', uid=uid
        )
        return len(rows) > 0


    @staticmethod
    def update_quantity(uid, pid, new_quantity):
        app.db.execute(
            '''
            UPDATE Sellers
            SET quantity =:new_quantity
            WHERE uid =:uid AND pid =:pid
            ''', uid=uid, pid=pid, new_quantity=new_quantity)
        return True

    @staticmethod
    def remove_product(uid, pid):
        app.db.execute(
            '''
            DELETE FROM Sellers
            WHERE uid =:uid AND pid =:pid
            ''', uid=uid, pid=pid)
        return True

    @staticmethod
    def add_product(uid, pid, price, quantity):
        app.db.execute(
            """ INSERT INTO Sellers(uid, pid, price, quantity)
            VALUES(:uid, :pid, :price, :quantity)
            RETURNING *
            """, uid = uid, pid = pid, price = price, quantity = quantity)
        return True

    @staticmethod
    def check_existence(uid, pid):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Sellers
            WHERE uid = :uid AND pid =:pid
            ''', uid=uid, pid=pid)
        if not rows:  # data not found
            return False
        else:
            return True
    
    @staticmethod
    def get_all_by_product(pid):
        rows = app.db.execute('''
        SELECT * 
        FROM Sellers
        WHERE pid = :pid
        ''',
            pid=pid)
        return [Inventory(*row) for row in rows]
    
    @staticmethod
    def get(uid, pid):
        rows = app.db.execute('''
        SELECT *
        FROM Sellers
        WHERE uid = :uid AND pid = :pid
        ''',
            uid=uid, pid=pid)
        return Inventory(*rows[0]) if rows else None

    @staticmethod
    def update_product(uid, pid, quantity, price):
        app.db.execute('''
        UPDATE Sellers
        SET quantity = :quantity, price = :price
        WHERE uid = :uid AND pid = :pid
        ''',
            uid=uid, pid=pid, quantity=quantity, price=price)
    
    @staticmethod
    def update_quantity(uid, pid, quantity):
        app.db.execute('''
        UPDATE Sellers
        SET quantity = :quantity
        WHERE uid = :uid AND pid = :pid
        ''',
            uid=uid, pid=pid, quantity=quantity)
        
    @staticmethod
    def reduce_quantity(uid, pid, removal_quantity):
        rows = app.db.execute(
            '''
            SELECT *
            FROM Sellers
            WHERE uid = :uid AND pid =:pid
            ''', uid=uid, pid=pid)
        
        if (not rows) or (removal_quantity > rows[0].quantity):  # data not found
            return False
        else:
            new_quantity = rows[0].quantity - removal_quantity
            app.db.execute(
                '''
                UPDATE Sellers
                SET quantity =:new_quantity
                WHERE uid =:uid AND pid =:pid
                ''', uid=uid, pid=pid, new_quantity=new_quantity)
            return True

    @staticmethod
    def get_inventory_analytics(uid):
        rows = app.db.execute(
            '''
            SELECT Sellers.uid, Sellers.pid, Products.name AS name, Sellers.quantity, Sellers.price
            FROM Sellers INNER JOIN Products on Sellers.pid=Products.id
            WHERE Sellers.uid =:uid AND Sellers.quantity < 10
            ORDER BY Sellers.quantity ASC
            ''', uid=uid)
        return rows

class InventoryAndProduct:
    def __init__(self, uid, pid, quantity, price, pname):
        self.uid = uid
        self.pid = pid
        self.quantity = quantity
        self.price = price
        self.pname = pname
    
    def get(uid):
        rows = app.db.execute('''
        SELECT s.uid, s.pid, s.quantity, s.price, p.name
        FROM Sellers s, Products p
        WHERE s.uid = :uid AND p.id = s.pid
        ''',
            uid=uid)
        return [InventoryAndProduct(*row) for row in rows]

    @staticmethod
    def get_by_product_name(uid, name):
        rows = app.db.execute(
            '''
            SELECT s.uid, s.pid, s.quantity, s.price, p.name
            FROM Sellers s, Products p
            WHERE s.uid = :uid AND p.id = s.pid AND p.name =:name
            ORDER BY uid, pid;
            ''', uid=uid, name=name)
        return [InventoryAndProduct(*row) for row in rows]
