from flask import current_app as app

class Category:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @staticmethod
    def get_all():
        rows = app.db.execute("""
        SELECT *
        FROM Category
        """,
        )
        return [Category(*row) for row in rows]
        