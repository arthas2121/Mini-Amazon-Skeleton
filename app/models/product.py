from flask import current_app as app


class Product:
    def __init__(self, id, name, category, description, image):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.image = image

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Products
''')
        return [Product(*row) for row in rows]
    
    @staticmethod
    def add_product(id, name, category, description, image):
        app.db.execute('''
INSERT INTO Products(id, name, category, description, image)
VALUES(:id, :name, :category, :description, :image)
        ''',
                            id=id, name=name, category=category, 
                            description=description, image=image)
    
    @staticmethod
    def delete_product(id):
        app.db.execute('''
            DELETE FROM Products
            WHERE id = :id
            RETURNING id
        ''',
                            id=id)
    
    @staticmethod
    def update_product(id, name, category, description, image):
        app.db.execute('''
        UPDATE Products
        SET name = :name, category = :category, description = :description, image = :image
        WHERE id = :id
        ''',
            id=id, name=name, category=category, description=description, image=image)
    

class ProductSummary:
    def __init__(self, pid, name, category, description, image, seller_num, avg_price, total_quantity):
        self.pid = pid
        self.name = name
        self.category = category
        self.description = description
        self.image = image
        self.seller_num = seller_num
        self.avg_price = avg_price
        self.total_quantity = total_quantity

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM ProductSummary
        WHERE pid = :id
        ''',
            id = id)
        return [ProductSummary(*row) for row in rows]
    
    @staticmethod
    def get_category(category, sorted_by='none', search=None):
        if sorted_by == 'none' and not search:
            rows = app.db.execute('''
            SELECT *
            FROM ProductSummary
            WHERE category = :category
            ''',
                category=category)
        elif sorted_by != 'none' and not search:
            rows = app.db.execute('''
            SELECT *
            FROM ProductSummary
            WHERE category = :category
            ORDER BY
            CASE WHEN :sort_by = 'Asc' THEN avg_price END ASC NULLS LAST,
            CASE WHEN :sort_by = 'Desc' THEN avg_price END DESC NULLS LAST,
            CASE WHEN :sort_by = 'quantity_asc' THEN total_quantity END ASC NULLS LAST,
            CASE WHEN :sort_by = 'quantity_desc' THEN total_quantity END DESC NULLS LAST
            ''',
                category=category, sort_by=sorted_by)
        elif sorted_by == 'none' and search:
            rows = app.db.execute('''
            SELECT *
            FROM ProductSummary
            WHERE LOWER(name) LIKE :search OR LOWER(description) LIKE :search
            ''',
                search='%'+search.lower()+'%')
        else:
            rows = app.db.execute('''
            SELECT * 
            FROM ProductSummary
            WHERE LOWER(name) LIKE :search OR LOWER(description) LIKE :search
            ORDER BY
            case when :sort_by = 'Asc' THEN avg_price END ASC NULLS LAST,
            case when :sort_by = 'Desc' THEN avg_price END DESC NULLS LAST,
            case when :sort_by = 'quantity_asc' THEN total_quantity END ASC NULLS LAST,
            case when :sort_by = 'quantity_desc' THEN total_quantity END DESC NULLS LAST
            ''',
                search='%'+search.lower()+'%', sort_by=sorted_by)
        return [ProductSummary(*row) for row in rows] if rows else None

class SellerForProduct:
    def __init__(self, pid, price, quantity, sid, firstname, lastname):
        self.pid = pid
        self.price = price
        self.quantity = quantity
        self.sid = sid
        self.firstname = firstname
        self.lastname = lastname
    
    def get(id):
        rows = app.db.execute('''
        SELECT s.pid, s.price, s.quantity, s.uid, u.firstname, u.lastname
        FROM Sellers s, Users u
        WHERE s.pid = :id AND s.uid = u.id
        ''',
            id=id)
        return [SellerForProduct(*row) for row in rows]
