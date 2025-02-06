from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/receipt')
def receipt():
    return render_template('receipt.html')

@app.route('/order_status')
def order_status():
    return render_template('order_status.html')

if __name__ == '__main__':
    app.run(debug=True)
