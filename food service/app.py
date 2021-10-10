from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired
import sqlite3

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image_link = StringField('Image link', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])

app = Flask(__name__)

@app.route('/')
def index():
    connection = sqlite3.connect('foodservice.db')

    products = connection.execute('''SELECT * FROM food''').fetchall()

    return render_template('index.html', products=products, logged_in=session.get('logged_in'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in') is True:
        return redirect(url_for('index'))

    connection = sqlite3.connect('foodservice.db')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = connection.execute('SELECT * FROM admins WHERE email = ? AND password = ?', (email, password)).fetchone()
        if admin:
            session['logged_in'] = True
            session['admin_id'] = admin[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', msg='Invalid credentials')
    return render_template('login.html')


@app.route('/orders')
def orders():
    if session.get('logged_in') is not True:
        return redirect(url_for('login'))
        
    connection = sqlite3.connect('foodservice.db')

    orders = connection.execute('SELECT * FROM orders').fetchall()
    return render_template('orders.html', orders=orders, logged_in=session.get('logged_in'))

@app.route('/order/<int:id>', methods=['GET', 'POST'])
def order(id):
    connection = sqlite3.connect('foodservice.db')
    product = connection.execute('''SELECT * FROM food WHERE id = ?''', (id,)).fetchone()

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')

        connection.execute('''
            INSERT INTO orders (food_id, fullname, email, address, payment_method)
            VALUES (?, ?, ?, ?, ?)''', 
            (product[0], fullname, email, address, payment_method))

        connection.commit()
        return redirect(url_for('index'))

    return render_template('order.html', product=product, logged_in=session.get('logged_in'))

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/product/create', methods=['GET', 'POST'])
def create_product():
    if session.get('logged_in') is not True:
        return redirect(url_for('login'))

    if request.method == 'POST':
        connection = sqlite3.connect('foodservice.db')
        form = ProductForm(request.form)

        name = form.name.data
        image_link = form.image_link.data
        description = form.description.data
        price = int(form.price.data)

        connection.execute('''
            INSERT INTO food (name, image_link, description, price) 
            VALUES (?, ?, ?, ?)''',
            (name, image_link, description, price))

        connection.commit()
        return redirect(url_for('index'))

    return render_template('create_product.html', form=ProductForm())


@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if session.get('logged_in') is not True:
        return redirect(url_for('login'))

    connection = sqlite3.connect('foodservice.db')
    if request.method == 'POST':

        form = ProductForm(request.form)

        name = form.name.data
        image_link = form.image_link.data
        description = form.description.data
        price = int(form.price.data)

        connection.execute('''
            UPDATE food SET name = ?, image_link = ?, description = ?, price = ? WHERE id = ?''',
            (name, image_link, description, price, id))


        connection.commit()
        return redirect(url_for('index'))

    product = connection.execute('''
        SELECT * FROM food WHERE id = ?''', (id,)).fetchone()

    form = ProductForm(data={'name': product[1], 'image_link': product[2], 'description': product[3], 'price': product[4]})
    return render_template('create_product.html', form=form, logged_in=session['logged_in'])


@app.route('/user', methods=['GET', 'POST'])
def edit_user():
    if session.get('logged_in') is not True:
        return redirect(url_for('login'))

    connection = sqlite3.connect('foodservice.db')
    if request.method == 'POST':

        form = AdminForm(request.form)

        email = form.email.data
        password = form.password.data

        connection.execute('''
            UPDATE admins SET email = ?, password = ? WHERE id = ?''',
            (email, password, session['admin_id']))

        connection.commit()
        return redirect(url_for('index'))

    admin = connection.execute('''
        SELECT * FROM admins WHERE id = ?''', (session['admin_id'],)).fetchone()

    form = AdminForm(data={'email': admin[1], 'password': admin[2]})

    return render_template('user.html', form=form, logged_in=session['logged_in'])
    

@app.route('/product/delete/<int:id>')
def delete_product(id):
    connection = sqlite3.connect('foodservice.db')
    connection.execute('DELETE FROM food WHERE id = ?', (id,))
    connection.commit()

    return redirect(url_for('index'))


@app.route('/orders/remove/<int:id>')
def delete_order(id):
    connection = sqlite3.connect('foodservice.db')
    connection.execute('DELETE FROM orders WHERE id = ?', (id,))
    connection.commit()

    return redirect(url_for('index'))

@app.route('/orders/<int:id>')
def order_info(id):
    connection = sqlite3.connect('foodservice.db')
    order = connection.execute('SELECT * FROM orders WHERE id = ?', (id,)).fetchone()

    return render_template('order_info.html', order=order, logged_in=session['logged_in'])

@app.route('/product/<int:id>')
def product_info(id):
    connection = sqlite3.connect('foodservice.db')
    product = connection.execute('SELECT * FROM food WHERE id = ?', (id,)).fetchone()
    orders = connection.execute('SELECT * FROM orders WHERE food_id = ?', (id,)).fetchall()

    return render_template('product_info.html', orders=orders, product=product, logged_in=session['logged_in'])


if __name__ == '__main__':
    app.secret_key = 'V+b{Kg!S[p,U?8,r/JtF2NB*)nu,)wvRkE1a4DgJ'
    app.debug = True
    app.run(port=8000)
