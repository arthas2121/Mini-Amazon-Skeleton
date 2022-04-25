import time
from ast import Or
from calendar import c
from crypt import methods
#from curses import flash
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user

from .models.cart import Cart
from .models.order import Order
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('userCart', __name__)

@bp.route('/cart',  methods=['GET', 'POST'])
def cartPage():
    user_cart = Cart.get_all(current_user.id)
    total_price = Cart.get_total_price(current_user.id)
    return render_template('Cart.html', user_cart=user_cart, total_price=total_price)

@bp.route('/Delete/<uid>/<sid>/<pid>',  methods=['GET', 'POST'])
def delete_item(uid, sid, pid):
    Cart.delete_item(uid, sid, pid)
    return redirect(url_for('userCart.cartPage'))

@bp.route('/UpdateQuantity/<uid>/<sid>/<pid>', methods=['GET', 'POST'])
def update_quantity(uid, sid, pid):
    quantity = request.form['quantity']
    Cart.update_quantity(uid, sid, pid, quantity)
    return redirect(url_for('userCart.cartPage'))

@bp.route('/SubmitOrder/<id>', methods=['GET', 'POST'])
def submit_order(id):
    order_status = Cart.check_status(id)
    #print("Order Status", order_status)
    if order_status < 0:
        return render_template('orderResult.html', status=order_status)
    else:
        all_products = Cart.get_all(id)
        total_price = Cart.get_total_price(id)
        for product in all_products:
            cur_time = time.strftime('%Y-%m-%d %H:%M:%S')
            Order.add_order(product.uid, product.sid, product.pid, product.quantity, product.price, cur_time)
        Cart.update_code_status(id)
        Cart.clear_cart(id)       
        return render_template('orderResult.html', status=order_status)

@bp.route('/AddCart/<uid>/<pid>/<sid>/', methods=['GET', 'POST'])
def add_to_cart(uid, pid, sid):
    quantity = request.form['quantity']
    res = Cart.add_to_cart(uid, pid, sid, quantity)
    if res < 0:
        flash('You have added this product!')
        return redirect(url_for('products.product', id=pid))
    else:
        return redirect(url_for('userCart.cartPage'))

@bp.route('/ApplyPromotionalCode/<uid>', methods=['GET', 'POST'])
def apply_promotional_code(uid):
    code = request.form['code']
    res = Cart.apply_promotional_code(code, uid)
    if res == 0:
        flash('You have applied promotional code {code} successfully!'.format(code=code))
    elif res == -1:
        flash('Invalid code!')
    elif res == -2:
        flash('You have used this code!')
    else:
        flash('Only one code allowed!')
    return redirect(url_for('userCart.cartPage'))

@bp.route('/CancelCode/<uid>', methods=['GET', 'POST'])
def cancel_code(uid):
    code = request.form['remove_code']
    res = Cart.cancel_code(uid, code)
    if res == -1:
        flash('You did not use this code!')
    else:
        flash('You have removed code {code} successfully!'.format(code=code))
    return redirect(url_for('userCart.cartPage'))


