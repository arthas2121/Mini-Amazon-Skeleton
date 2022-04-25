from unicodedata import category
from flask import render_template
from flask_login import current_user
import datetime

from .models.user import User
from .models.product import Product
from .models.order import Order
#new
from .models.category import Category

from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all()
    products = products[:10]
    # find the products current user has bought:
    if current_user.is_authenticated:
        orders = Order.get_all_by_buyer_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        purchased_products = [Product.get(i.pid) for i in orders]
        sellers = [User.get(i.seller) for i in orders]
        zipped_orders = zip(orders[:5], purchased_products[:5], sellers[:5])
    else:
        zipped_orders = None
    # render the page by adding information to the index.html file

    categories = Category.get_all()
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=zipped_orders,
                           categories=categories)
