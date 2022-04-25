from ctypes import addressof
from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from .inventory import Inventory

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
    
    @staticmethod
    def update_by_id(id, firstname, lastname, email, address):
        rows = app.db.execute("""
        UPDATE Users
        SET firstname = :firstname, lastname = :lastname, email = :email, address = :address
        WHERE id = :id
        """,
        id=id, firstname=firstname, lastname=lastname, email=email, address=address)

    @staticmethod
    def get_balance_by_id(id):
        rows = app.db.execute("""
        SELECT balance
        FROM Users
        WHERE id = :id
        """,
        id=id)
        return rows[0][0]
    
    @staticmethod
    def change_balance_by_id(id, balance):
        rows = app.db.execute("""
        UPDATE Users
        SET balance = :balance
        WHERE id = :id
        """,
        id=id, balance=balance)

    @staticmethod
    def get_products():
        return Inventory.get_all_by_user(self.id)


    @staticmethod
    def check_old_password_by_id(id, old_password):
        rows = app.db.execute("""
        SELECT password
        FROM Users
        WHERE id = :id
        """,
        id=id)
        if check_password_hash(rows[0][0], old_password):
            return True
        else:
            return False
    

    @staticmethod
    def update_password_by_id(id, new_password):
        app.db.execute("""
        UPDATE Users
        SET password = :password
        WHERE id = :id
        """,
        id=id, password=generate_password_hash(new_password))
