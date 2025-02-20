from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def verify_password(self, password):
        return self.password == password

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prix = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref_commande = db.Column(db.String(5), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    nom_produit = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prix = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())

class Recu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref_commande = db.Column(db.String(5), nullable=False)
    prix_total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
#

# Main Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.verify_password(password):
            session['user_id'] = user.id
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')


@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')




@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['prix'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

# Vider le panier
@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))



# Product Management Routes
@app.route('/create_product', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = float(request.form['prix'])
        type = request.form['type']
        
        new_product = Product(nom=nom, description=description, prix=prix, type=type)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('view_products'))
    return render_template('create_product.html')

@app.route('/view_products')
def view_products():
    products = Product.query.all()
    return render_template('db/view_products.html', products=products)



# Database Management Routes
@app.route('/database_overview')
def database_overview():
    return render_template('db/database_overview.html')

@app.route('/view_users')
def view_users():
    users = User.query.all()
    return render_template('db/view_users.html', users=users)

# Menu Category Routes

@app.route('/menu/poulet')
def menu_poulet():
    poulets = Product.query.filter_by(type='poulet').all()
    return render_template('menu/poulet.html', poulets=poulets)

@app.route('/menu/salade')
def menu_salade():
    salade = Product.query.filter_by(type='salade').all()
    return render_template('menu/salade.html', salade=salade)

@app.route('/menu/boisson')
def menu_boisson():
    boissons = Product.query.filter_by(type='boisson').all()
    return render_template('menu/boisson.html', boissons=boissons)

@app.route('/menu/dessert')
def menu_dessert():
    dessert = Product.query.filter_by(type='dessert').all()
    return render_template('menu/dessert.html', dessert=dessert)


# Ajouter un produits au panier 
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return redirect(url_for('menu'))
    
    # Initialiser le panier s'il n'existe pas
    if 'cart' not in session:
        session['cart'] = []

    # Vérifier si le produit est déjà dans le panier
    cart_items = session['cart']
    existing_product = next((item for item in cart_items if item['id'] == product.id), None)
    
    if existing_product:
        # Optionnel : Augmenter la quantité au lieu de réajouter
        existing_product['quantity'] += 1
    else:
        # Ajouter le produit avec une clé ID
        cart_items.append({
            'id': product.id,
            'nom': product.nom,
            'prix': product.prix,
            'quantity': 1
        })
    
    session['cart'] = cart_items  # Sauvegarde la session
    session.modified = True  # Marquer la session comme modifiée
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != product_id]
    session.modified = True
    return redirect(url_for('cart'))




# Initialize database and insert sample products
def insert_sample_products():
    sample_products = [
        {'id': '1','nom': 'Poulet Frit', 'description': 'Poulet croustillant frit à la perfection', 'prix': 9.99, 'type': 'poulet'},
        {'id': '2','nom': 'Poulet BBQ', 'description': 'Poulet grillé avec sauce barbecue', 'prix': 10.50, 'type': 'poulet'},
        {'id': '3','nom': 'Poulet Curry', 'description': 'Poulet au curry avec riz basmati', 'prix': 11.00, 'type': 'poulet'},
        {'id': '4','nom': 'Poulet Tandoori', 'description': 'Poulet mariné au yaourt et épices', 'prix': 10.75, 'type': 'poulet'},
        
        {'id': '5','nom': 'Salade César', 'description': 'Salade fraîche avec croûtons et parmesan', 'prix': 7.50, 'type': 'salade'},
        {'id': '6','nom': 'Salade Grecque', 'description': 'Salade avec feta, olives et tomates', 'prix': 8.00, 'type': 'salade'},
        {'id': '7','nom': 'Salade Niçoise', 'description': 'Salade avec thon, œufs et haricots verts', 'prix': 8.50, 'type': 'salade'},
        {'id': '8','nom': 'Salade de Chèvre Chaud', 'description': 'Salade avec toast de chèvre chaud', 'prix': 9.00, 'type': 'salade'},
        
        {'id': '9','nom': 'Coca-Cola', 'description': 'Boisson gazeuse rafraîchissante', 'prix': 2.50, 'type': 'boisson'},
        {'id': '10','nom': 'Jus d\'Orange', 'description': 'Jus d\'orange pressé frais', 'prix': 3.50, 'type': 'boisson'},
        {'id': '11','nom': 'Eau Minérale', 'description': 'Eau minérale naturelle', 'prix': 2.00, 'type': 'boisson'},
        {'id': '12','nom': 'Thé Glacé', 'description': 'Thé glacé maison', 'prix': 3.00, 'type': 'boisson'},
        
        {'id': '13','nom': 'Tiramisu', 'description': 'Dessert italien au café et mascarpone', 'prix': 5.00, 'type': 'dessert'},
        {'id': '14','nom': 'Mousse au Chocolat', 'description': 'Mousse légère au chocolat noir', 'prix': 5.50, 'type': 'dessert'},
        {'id': '15','nom': 'Crème Brûlée', 'description': 'Crème vanille avec caramel croquant', 'prix': 6.00, 'type': 'dessert'},
        {'id': '16','nom': 'Cheesecake', 'description': 'Cheesecake classique avec coulis de fruits rouges', 'prix': 6.50, 'type': 'dessert'}
    ]
    
    for product_data in sample_products:
        product = Product(**product_data)
        db.session.add(product)
    db.session.commit()

@app.route('/validate_cart')
def validate_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirection si l'utilisateur n'est pas connecté

    user_id = session['user_id']
    cart_items = session.get('cart', [])

    if not cart_items:
        return redirect(url_for('cart'))  # Redirection si le panier est vide

    ref_commande = secrets.token_hex(3).upper()  # Générer un code à 6 caractères hexadécimaux
    prix_total = sum(item['prix'] for item in cart_items)

    # Création du Reçu
    new_recu = Recu(ref_commande=ref_commande, prix_total=prix_total, id=user_id)
    db.session.add(new_recu)
    
    # Ajouter chaque produit dans la table Commande
    for item in cart_items:
        new_commande = Commande(
            ref_commande=ref_commande,
            product_id=item['id'],
            nom_produit=item['nom'],
            description=item.get('description', ' '),
            prix=item['prix']
        )
        db.session.add(new_commande)

    db.session.commit()

    # Vider le panier après validation
    session.pop('cart', None)

    return redirect(url_for('confirmation', ref_commande=ref_commande))


@app.route('/confirmation/<ref_commande>')
def confirmation(ref_commande):
    return render_template('confirmation.html', ref_commande=ref_commande)

@app.route('/receipt')
def user_receipts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    receipts = Recu.query.filter_by(id=user_id).all()
    
    return render_template('receipt.html', receipts=receipts)


@app.route('/receipt_details/<ref_commande>')
def receipt_details(ref_commande):
    recu = Recu.query.filter_by(ref_commande=ref_commande).first()
    commandes = Commande.query.filter_by(ref_commande=ref_commande).all()

    return render_template('receipt_details.html', recu=recu, commandes=commandes)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        try:
            Product.query.delete()
            db.session.commit()
            insert_sample_products()
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing products: {str(e)}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)