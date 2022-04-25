from crypt import methods
from email.mime import image
from textwrap import indent
from unicodedata import category
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.fields import SelectField, DecimalField
from flask import current_app as app
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
from flask import current_app as app

from .models.productReview import productReview
from .models.sellerReview import sellerReview
from .models.user import User
from .models.inventory import Inventory, InventoryAndProduct
from .models.order import Order
from .models.product import Product
from .models.category import Category

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            try:
                msg = Message(
                    'Mini-Amazon Register Confirmation',
                    sender ='CS516miniamazon@gmail.com',
                    recipients = [form.email.data]
                )
                msg.body = 'Thank you for joining Mini-Amazon! Enjoy your shopping!'
                app.mail.send(msg)
            except:
                pass
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


class UpdateProfileForm(FlaskForm):
    id = StringField('Id', render_kw={'readonly': True})
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Save')


@bp.route('/profile', methods=['GET', 'POST'])
def update_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = UpdateProfileForm()
    if request.method == 'GET':
        form.id.data = current_user.id
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.address.data = current_user.address
    if form.validate_on_submit():
        User.update_by_id(current_user.id, form.firstname.data, form.lastname.data, form.email.data, form.address.data)
        flash('Congratulations, you have successfully update your profile!')
        return redirect(url_for('index.index'))
    return render_template('updateProfile.html', title='Update Profile', form=form)


@bp.route('/wallet')
def manage_balance():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    current = User.get_balance_by_id(current_user.id)
    return render_template('manageBalance.html', title='Manage Balance', current=current)


class DepositForm(FlaskForm):
    amount = DecimalField('Deposit Amount', validators=[DataRequired()])
    submit = SubmitField('Confirm')


@bp.route('/wallet/deposit', methods=['GET', 'POST'])
def deposit():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = DepositForm()
    current = User.get_balance_by_id(current_user.id)
    if form.validate_on_submit():
        if form.amount.data < 0:
            flash('Negative amount NOT allowed!')
            return redirect(url_for('users.deposit'))
        User.change_balance_by_id(current_user.id, current + form.amount.data)
        flash('Successfully deposited!')
        return redirect(url_for('users.manage_balance'))
    return render_template('deposit.html', title='Deposit', form=form, current=current)


class WithdrawForm(FlaskForm):
    amount = DecimalField('Withdraw Amount', validators=[DataRequired()])
    submit = SubmitField('Confirm')


@bp.route('/wallet/withdraw', methods=['GET', 'POST'])
def withdraw():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = WithdrawForm()
    current = User.get_balance_by_id(current_user.id)
    if form.validate_on_submit():
        if form.amount.data < 0:
            flash('Negative amount NOT allowed!')
            return redirect(url_for('users.withdraw'))
        if current < form.amount.data:
            flash('You can only withdraw up to your balance!')
            return redirect(url_for('users.withdraw'))
        User.change_balance_by_id(current_user.id, current - form.amount.data)
        flash('Successfully withdrawn!')
        return redirect(url_for('users.manage_balance'))
    return render_template('withdraw.html', title='Withdraw', form=form, current=current)



class ProductReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')

@bp.route('/product_review/<pid>', methods=['GET', 'POST'])
def product_review(pid):   
    form = ProductReviewForm()

    if form.validate_on_submit():
        if productReview.add_product_review(current_user.id, pid, form.rating.data, form.description.data):
            return redirect(url_for('users.all_product_review', uid = current_user.id))
        elif productReview.add_product_review(current_user.id, pid, form.rating.data, form.description.data) == 1:
            flash("You have already made a review for this item!")
            return redirect(url_for('users.all_product_reviews', uid = current_user.id))
        elif productReview.add_product_review(current_user.id, pid, form.rating.data, form.description.data) == 0:
            flash("You can only review the item after you make a purchase!")
            return redirect(url_for('index.index'))
    return render_template('product_review.html', pid = pid, form = form)


@bp.route('/all_product_review/<uid>', methods=['GET', 'POST'])
def all_product_review(uid):
    reviews = productReview.get_user_all_product_reviews(uid)
    return render_template('all_product_review.html', reviews = reviews, uid=uid)

class UpdateProductReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')


@bp.route('/all_product_review/<uid>/update_review/<pid>', methods=['GET','POST'])
def update_product_review(uid, pid):

    form = UpdateProductReviewForm()

    if form.validate_on_submit():
        productReview.update_product_review(uid, pid, form.rating.data, form.description.data)
        flash("Review updated successfully!")
        return redirect(url_for('users.all_product_review', uid = uid))
    
    return render_template('update_product_review.html', uid = uid, pid = pid, form=form)


def allowed_image(filename):

    if not '.' in filename:
        flash("This is not an acceptable file.")
        return False
    
    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        flash("This is not the acceptable file extension.")
        return False


@bp.route('/upload-image/<uid>/<pid>', methods = ['GET', 'POST'])
def upload_form(uid, pid):

    if request.files:

        image = request.files["image"]

        if image.filename == "":
            flash("Image mush have a filename")
            return redirect(request.url)

        if not allowed_image(image.filename):
            flash("Image extension is not allowed")
            return redirect(request.url)

        else:
            filename = secure_filename(image.filename)
                
        image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
        flash("Image successfully uploaded")
        productReview.update_image_path(pid, uid, filename)
        return render_template('upload_file.html', uid = uid, pid = pid, filename = filename)
    else:
        filename = productReview.get_user_product_image_path(pid, uid)
        if filename is None:
            return render_template('upload_file.html', uid = uid, pid = pid)
        else:
            return render_template('upload_file.html', uid = uid, pid = pid, filename = filename)


@bp.route('/display-image/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename = 'img/uploads/' + filename), code = 301)


@bp.route('/all_product_review/<uid>/remove/<pid>')
def remove_product_review(uid, pid):
    productReview.remove_product_review(uid, pid)
    return redirect(url_for('users.all_product_review', uid = uid))



class SellerReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')

@bp.route('/seller_review/<sid>', methods=['GET', 'POST'])
def seller_review(sid):   
    form = SellerReviewForm()

    if form.validate_on_submit():
        if sellerReview.add_seller_review(current_user.id, sid, form.rating.data, form.description.data):
            return redirect(url_for('users.all_seller_review', uid = current_user.id))
        elif sellerReview.add_seller_review(current_user.id, sid, form.rating.data, form.description.data) == 1:
            flash("You have already made a review for this seller!")
            return redirect(url_for('users.all_seller_reviews', uid = current_user.id))
        elif sellerReview.add_seller_review(current_user.id, sid, form.rating.data, form.description.data) == 0:
            flash("You can only review the seller after you make a purchase from them!")
            return redirect(url_for('index.index'))
    return render_template('seller_review.html', sid = sid, form = form)


@bp.route('/all_seller_review/<uid>', methods=['GET', 'POST'])
def all_seller_review(uid):
    reviews = sellerReview.get_user_all_seller_reviews(uid)
    return render_template('all_seller_review.html', reviews = reviews, uid=uid)

class UpdateSellerReviewForm(FlaskForm):
    rating = StringField(('Rating (0-5):'), validators=[DataRequired()])
    description = StringField(('Write Your Review:'))
    submit = SubmitField('Submit')

@bp.route('/all_seller_review/<uid>/update_review/<sid>', methods=['GET','POST'])
def update_seller_review(uid, sid):

    form = UpdateSellerReviewForm()

    if form.validate_on_submit():
        sellerReview.update_seller_review(uid, sid, form.rating.data, form.description.data)
        flash("Review updated successfully!")
        return redirect(url_for('users.all_seller_review', uid = uid))

    return render_template('update_seller_review.html', uid = uid, sid = sid, form=form)


@bp.route('/all_seller_review/<uid>/remove/<sid>')
def remove_seller_review(uid, sid):
    sellerReview.remove_seller_review(uid, sid)
    return redirect(url_for('users.all_seller_review', uid = uid))

@bp.route('/inventory', methods=['GET', 'POST'])
def view_inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    #products = Inventory.get_all_by_user(current_user.id)
    products = InventoryAndProduct.get(current_user.id)
    return render_template('inventory.html', title='Inventory', name=current_user.firstname, products=products)

@bp.route('/inventory/update_inventory_quantity_by_new/<pid>', methods=['GET','POST'])
def change_quantity_by_new(pid):
    quantity = request.form['quantity']
    Inventory.update_quantity(current_user.id, pid, quantity)
    flash('Inventory Being Successfully Updated!')
    return redirect(url_for('users.view_inventory'))

@bp.route('/inventory/inventory_product_removal_by_pid/<pid>', methods=['GET','POST'])
def inventory_product_removal_by_pid(pid):
    Inventory.remove_product(current_user.id, pid)
    flash('Products Being Successfully Removed!')
    return redirect(url_for('users.view_inventory'))

@bp.route('/EditProduct/<uid>/<pid>', methods=['GET', 'POST'])
def edit_product(uid, pid):
    productInfo = Product.get(pid)
    sellerInfo = Inventory.get(uid, pid)
    categories = Category.get_all()
    return render_template('EditProduct.html', productInfo=productInfo, sellerInfo=sellerInfo, categories=categories) 

@bp.route('/EditDatabase/<uid>/<pid>', methods=['GET', 'POST'])
def edit_database(uid, pid):
    category = request.form['category']
    name = request.form['productName']
    description = request.form['productDescription']
    image = request.form['image']
    price = request.form['price']
    quantity = request.form['quantity']
    Product.update_product(pid, name, category, description, image)
    Inventory.update_product(uid, pid, quantity, price)
    flash('Congratulations, you have successfully updated the information of product {pid} !'.format(pid=pid))
    return redirect(url_for('users.view_inventory'))

@bp.route('/history_of_orders')
def view_history_of_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    orders = Order.get_all_by_seller(current_user.id)
    return render_template('history_of_orders.html', title='History of Order', name=current_user.firstname, orders=orders)

@bp.route('/history_of_orders/update_order/<order>', methods=['GET', 'POST'])
def update_order_fulfillment(order):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    Order.update_fulfill(order, True)
    return redirect(url_for('users.view_history_of_orders'))

class SellerViewBuyerForm(FlaskForm):
    id = StringField('Id', render_kw={'readonly': True})
    firstname = StringField('First Name', render_kw={'readonly': True})
    lastname = StringField('Last Name', render_kw={'readonly': True})
    email = StringField('Email', render_kw={'readonly': True})
    address = StringField('Address', render_kw={'readonly': True})


@bp.route('/history_of_orders/<uid>', methods=['GET', 'POST'])
def seller_view_buyer(uid):
    form = SellerViewBuyerForm()
    buyer = User.get(uid)
    form.id.data = buyer.id
    form.firstname.data = buyer.firstname
    form.lastname.data = buyer.lastname
    form.email.data = buyer.email
    form.address.data = buyer.address
    return render_template('sellerViewBuyer.html', title='Buyer\'s Profile', form=form)


class PublicBuyerForm(FlaskForm):
    id = StringField('Id', render_kw={'readonly': True})
    firstname = StringField('First Name', render_kw={'readonly': True})
    lastname = StringField('Last Name', render_kw={'readonly': True})


class PublicSellerForm(FlaskForm):
    id = StringField('Id', render_kw={'readonly': True})
    firstname = StringField('First Name', render_kw={'readonly': True})
    lastname = StringField('Last Name', render_kw={'readonly': True})
    email = StringField('Email', render_kw={'readonly': True})
    address = StringField('Address', render_kw={'readonly': True})


@bp.route('/public/<uid>', methods=['GET', 'POST'])
def public_view(uid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if not Inventory.check_is_seller(uid):
        form = PublicBuyerForm()
        buyer = User.get(uid)
        form.id.data = buyer.id
        form.firstname.data = buyer.firstname
        form.lastname.data = buyer.lastname
        return render_template('publicBuyerView.html', form=form)
    else:
        form = PublicSellerForm()
        seller = User.get(uid)
        form.id.data = seller.id
        form.firstname.data = seller.firstname
        form.lastname.data = seller.lastname
        form.email.data = seller.email
        form.address.data = seller.address
        reviews = sellerReview.get_seller_review_new_date(uid)
        return render_template('publicSellerView.html', form=form, reviews=reviews)


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password_again = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')


@bp.route('/profile/reset_password', methods=['GET', 'POST'])
def reset_password():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.check_old_password_by_id(current_user.id, form.old_password.data):
            User.update_password_by_id(current_user.id, form.new_password.data)
            flash("Your password has been successfully reset!")
            return redirect(url_for('users.update_profile'))
        else:
            flash("Your old password is incorrect. Please try again!")
            return redirect(url_for('users.reset_password'))
    return render_template('resetPassword.html', form=form)
    

class sortBy(FlaskForm):
    myChoices = [("Most Recent","Most Recent"), ("Rating High to Low", "Rating High to Low"), ("Rating Low to High", "Rating Low to High")]
    myField = SelectField(u'Field name', choices = myChoices)
    submit = SubmitField('change sort')

@bp.route('/reviewforme', methods=['GET', 'POST'])
def review_for_me():

    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    form = sortBy()
    if form.validate_on_submit():
        sort_cat = form.myField.data
        if sort_cat == "Most Recent":
            all_reviews = sellerReview.get_seller_review_new_date(current_user.id)
        elif sort_cat == "Rating High to Low":
            all_reviews = sellerReview.get_seller_review_from_high(current_user.id)
        elif sort_cat == "Rating Low to High":
            all_reviews = sellerReview.get_seller_review_from_low(current_user.id)
    else:
        all_reviews = sellerReview.get_seller_review_new_date(current_user.id)
    
    return render_template('review_for_me.html', all_reviews = all_reviews, form=form)

@bp.route('/order_analytics')
def view_order_analytics():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    products = Order.get_order_analytics(current_user.id)
    return render_template('OrderAnalytics.html', title='Order Analytics', name=current_user.firstname, products=products)

@bp.route('/inventory_analytics')
def view_inventory_analytics():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    products = Inventory.get_inventory_analytics(current_user.id)
    return render_template('InventoryAnalytics.html', title='Inventory Analytics', name=current_user.firstname, products=products)

@bp.route('/inventory_search', methods=['GET', 'POST'])
def inventory_search():

    search = '...'
    if request.form:
        if request.form.get('search'):  
            search = request.form.get('search')

    if search == '...':
        return redirect(url_for('users.view_inventory'))
    else:
        products = InventoryAndProduct.get_by_product_name(current_user.id, search)
        return render_template('inventory.html', title='Inventory', name=current_user.firstname, products=products)