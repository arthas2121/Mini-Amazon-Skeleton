from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
from flask_mail import Mail, Message
import os


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    app.mail = Mail(app)
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'CS516miniamazon@gmail.com'
    app.config['MAIL_PASSWORD'] = 'miniamazon@CS516'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.mail = Mail(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .products import bp as product_bp
    app.register_blueprint(product_bp)

    from .purchaseHistory import bp as purchase_history_bp
    app.register_blueprint(purchase_history_bp)
    
    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)
    
    path = os.getcwd()
    app.config['IMAGE_UPLOADS'] = path + "/app/static/img/uploads"
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['PNG', 'JPG', 'JPEG', 'GIF']

    return app
