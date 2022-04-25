from crypt import methods
from flask import redirect, render_template, url_for, flash
from flask import request
from flask_login import current_user
from wtforms.fields import SelectField
from flask_wtf import FlaskForm
from wtforms import SubmitField

from app.models.sellerReview import sellerReview

from .models.productReview import productReview
from .models.product import Product, ProductSummary, SellerForProduct
from .models.category import Category
from .models.productReview import productReview
from .models.inventory import Inventory
from .models.user import User
from flask import Blueprint
bp = Blueprint('products', __name__)


class sortBy(FlaskForm):
    myChoices = [("Most Recent","Most Recent"), ("Rating High to Low", "Rating High to Low"), ("Rating Low to High", "Rating Low to High")]
    myField = SelectField(u'Field name', choices = myChoices)
    submit = SubmitField('change sort')


@bp.route('/ProductPage/<id>', methods=['GET', 'POST'])
def product(id):
    form = sortBy()
    if form.validate_on_submit():
        sort_cat = form.myField.data
        if sort_cat == "Most Recent":
            all_reviews = productReview.get_product_review_new_date(pid=id)
        elif sort_cat == "Rating High to Low":
            all_reviews = productReview.get_product_review_from_high(pid=id)
        elif sort_cat == "Rating Low to High":
            all_reviews = productReview.get_product_review_from_low(pid=id)
    else:
        all_reviews = productReview.get_product_review_new_date(pid=id)
    product = Product.get(id)
    avg_rating = productReview.get_product_avg_review(pid = id)
    review_cnt = productReview.get_num_product_review(pid = id)
    pos_reviews = productReview.get_top_3_reviews(pid=id)
    image_reviews = productReview.get_product_image_path(pid=id)

    productsummary = ProductSummary.get(id)[0]
    if productsummary.avg_price:
        productsummary.avg_price = '$' + str(round(productsummary.avg_price, 2))
    
    sellers = SellerForProduct.get(id)
    
    sellers_avg = []

    for seller in sellers:
        sellers_avg.append(sellerReview.get_seller_avg_review(seller.sid))

    sellers_total = zip(sellers, sellers_avg)

    return render_template('ProductPage.html', form = form, product=product, avg_rating = avg_rating, review_cnt = review_cnt, pos_reviews = pos_reviews, all_reviews=all_reviews, productsummary=productsummary, sellers=sellers, image_reviews=image_reviews, sellers_total = sellers_total)

@bp.route('/ProductSummary/<category>/<search>/<sort_by>', methods=['GET', 'POST'])
def productSummary(category, search='...', sort_by='none'):
    categories = Category.get_all()
    if request.form:
        if request.form.get('search'):  
            search = request.form.get('search')
    if search == '...':
        search_term = None
    else:
        search_term = search

    products = ProductSummary.get_category(category=category, search=search_term, sorted_by=sort_by)
    if products:
        for product in products:
            if product.avg_price:
                product.avg_price = '$' + str(round(product.avg_price, 2))
    return render_template('ProductSummary.html', products=products, category=category, categories=categories, search=search)

@bp.route('/CreateProduct', methods=['GET', 'POST'])
def createProduct():
    categories = Category.get_all()
    return render_template('CreateProduct.html', categories=categories)

@bp.route('/AddProduct', methods=['GET', 'POST'])
def addToDataset():
    products = Product.get_all()
    ids = [p.id for p in products]
    new_id = max(ids) + 1
    category = request.form['category']
    name = request.form['productName']
    description = request.form['productDescription']
    image = request.form['image']
    price = request.form['price']
    quantity = request.form['quantity']
    Product.add_product(new_id, name, category, description, image)
    Inventory.add_product(current_user.id, new_id, price, quantity)
    flash('Congratulations, you have successfully added the information of product {pid} !'.format(pid=new_id))
    return redirect(url_for('users.view_inventory'))

@bp.route('/ProductPage/<pid>/like/<uid>')
def like_product(uid, pid):
    productReview.like_product_review(uid, pid)
    return redirect(url_for('products.product', id=pid))

@bp.route('/ProductPage/<pid>/dislike/<uid>')
def dislike_product(uid, pid):
    productReview.dislike_product_review(uid, pid)
    return redirect(url_for('products.product', id=pid))

@bp.route('/ProductPage/<pid>/<uid>/show-image')
def show_image(uid, pid):
    filename = productReview.get_user_product_image_path(pid, uid)
    return render_template('view_image.html', pid=pid, uid=uid, filename=filename)