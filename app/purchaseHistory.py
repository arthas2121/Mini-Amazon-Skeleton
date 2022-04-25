from time import time
from unicodedata import category
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from .models.product import Product
from .models.order import Order
from .models.user import User

from flask import Blueprint
bp = Blueprint('purchase_history', __name__)


class SearchByItemForm(FlaskForm):
    search_field = StringField(('Search by item '))
    submit1 = SubmitField('Search')


class SearchBySellerForm(FlaskForm):
    search_field = StringField(('Search by seller\'s first name '))
    submit2 = SubmitField('Search')


@bp.route('/purchase_history', methods=['GET', 'POST'])
def show_all_history():
    form1 = SearchByItemForm()
    form2 = SearchBySellerForm()
    if current_user.is_authenticated:
        if form1.validate_on_submit() and form1.submit1.data:
            search_field = form1.search_field.data.strip()
            if search_field == '':
                return redirect(url_for('purchase_history.show_all_history'))
            return redirect(url_for('purchase_history.search_by_item', search_field=search_field))
        if form2.validate_on_submit() and form2.submit2.data:
            search_field = form2.search_field.data.strip()
            if search_field == '':
                return redirect(url_for('purchase_history.show_all_history'))
            return redirect(url_for('purchase_history.search_by_seller', search_field=search_field))
        orders = Order.get_all_by_buyer_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        purchased_products = [Product.get(i.pid) for i in orders]
        sellers = [User.get(i.seller) for i in orders]
        zipped_orders = zip(orders, purchased_products, sellers)
    else:
        return redirect(url_for('users.login'))

    return render_template('purchaseHistory.html',
                           purchase_history=zipped_orders, form1=form1, form2=form2)


@bp.route('/purchase_history/item/<search_field>', methods=['GET', 'POST'])
def search_by_item(search_field):
    form1 = SearchByItemForm()
    if form1.validate_on_submit() and form1.submit1.data:
        search_field = form1.search_field.data.strip()
        if search_field == '':
            return redirect(url_for('purchase_history.show_all_history'))
        return redirect(url_for('purchase_history.search_by_item', search_field=search_field))
    form2 = SearchBySellerForm()
    if form2.validate_on_submit() and form2.submit2.data:
        search_field = form2.search_field.data.strip()
        if search_field == '':
            return redirect(url_for('purchase_history.show_all_history'))
        return redirect(url_for('purchase_history.search_by_seller', search_field=search_field))
    orders = Order.search_by_item(search_field, current_user.id)
    purchased_products = [Product.get(i.pid) for i in orders]
    sellers = [User.get(i.seller) for i in orders]
    zipped_orders = zip(orders, purchased_products, sellers)
    return render_template('purchaseHistory.html', purchase_history=zipped_orders, form1=form1, form2=form2)


@bp.route('/purchase_history/seller/<search_field>', methods=['GET', 'POST'])
def search_by_seller(search_field):
    form1 = SearchByItemForm()
    if form1.validate_on_submit() and form1.submit1.data:
        search_field = form1.search_field.data.strip()
        if search_field == '':
            return redirect(url_for('purchase_history.show_all_history'))
        return redirect(url_for('purchase_history.search_by_item', search_field=search_field))
    form2 = SearchBySellerForm()
    if form2.validate_on_submit() and form2.submit2.data:
        search_field = form2.search_field.data.strip()
        if search_field == '':
            return redirect(url_for('purchase_history.show_all_history'))
        return redirect(url_for('purchase_history.search_by_seller', search_field=search_field))
    print(search_field)
    orders = Order.search_by_seller(search_field, current_user.id)
    purchased_products = [Product.get(i.pid) for i in orders]
    sellers = [User.get(i.seller) for i in orders]
    zipped_orders = zip(orders, purchased_products, sellers)
    return render_template('purchaseHistory.html', purchase_history=zipped_orders, form1=form1, form2=form2)


@bp.route('/purchase_history/time/<time_interval>')
def show_history_by_date(time_interval):
    since = datetime.datetime(1980, 9, 14, 0, 0, 0)
    if time_interval == "week":
        since = datetime.datetime.now() - datetime.timedelta(weeks=1)
    elif time_interval == "month":
        since = datetime.datetime.now() - datetime.timedelta(days=30)
    elif time_interval == "halfyear":
        since = datetime.datetime.now() - datetime.timedelta(days=182)
    elif time_interval == "year":
        since = datetime.datetime.now() - datetime.timedelta(days=365)
    orders = Order.get_all_by_buyer_uid_since(
        current_user.id, since)
    purchased_products = [Product.get(i.pid) for i in orders]
    sellers = [User.get(i.seller) for i in orders]
    zipped_orders = zip(orders, purchased_products, sellers)
    return render_template('timedPurchaseHistory.html', purchase_history=zipped_orders)


class DetailedOrderForm(FlaskForm):
    name = StringField('Seller Name', render_kw={'readonly': True})
    product = StringField('Product Name', render_kw={'readonly': True})
    unit_price = StringField('Unit Price', render_kw={'readonly': True})
    quantity = StringField('Quantity', render_kw={'readonly': True})
    fulfillment = StringField('fulfillment', render_kw={'readonly': True})
    time = StringField('Order Time', render_kw={'readonly': True})
    

@bp.route('/order_detail/<id>', methods=['GET', 'POST'])
def order_detail(id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    order = Order.get(id)
    product = Product.get(order.pid)
    seller = User.get(order.seller)
    form = DetailedOrderForm()
    form.name.data = seller.firstname + " " + seller.lastname
    form.product.data = product.name
    form.unit_price.data = order.price
    form.quantity.data = order.quantity
    form.fulfillment.data = order.fulfilled
    form.time.data = order.time_purchased
    return render_template('detailedOrder.html', form=form)
