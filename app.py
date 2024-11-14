from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from tabulate import tabulate
import pandas as pd
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed to use sessions

# Suppress SettingWithCopyWarning
pd.options.mode.chained_assignment = None

# Function definitions
def align_left(s, width=30):
    """Align text to the left."""
    return f'{s:<{width}}' if pd.notna(s) else ""

def load_and_preprocess_data(file_path="products.xlsx"):
    """Load and preprocess product data from Excel file."""
    df = pd.read_excel(file_path)
    df = df.rename(columns={
        "Part Name": "Product Name",
        "Quantity": "Quantity",
        "purchase_price": "Purchase Price"
    })
    product_name = df.pop("Product Name")
    df.insert(0, "Product Name", product_name.apply(align_left))
    df["Packaging"] = pd.to_datetime(df["Packaging"], format="%m/%y")
    return df

def filter_expiring_products(df, expiration_date):
    """Filter products that are expiring on or before the specified date."""
    mask = df["Packaging"] <= pd.Timestamp(expiration_date)
    expiring_products = df.loc[mask].copy()
    expiring_products["Packaging"] = expiring_products["Packaging"].dt.strftime('%d-%m-%Y')
    return expiring_products


#spacy. load()

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/u_home')
def u_home():
    return render_template('u_home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/u_about')
def u_about():
    return render_template('u_about.html')

@app.route('/i_about')
def i_about():
    return render_template('i_about.html')

@app.route('/checker', methods=['GET', 'POST'])
def checker():
    if request.method == 'POST':
        expiration_date_str = request.form.get('expiration_date')
        try:
            expiration_date = datetime.datetime.strptime(expiration_date_str, '%d-%m-%Y')
        except ValueError:
            return render_template('checker.html', error="Invalid date format. Please use dd-mm-yyyy.")
        
        df = load_and_preprocess_data()
        expiring_products = filter_expiring_products(df, expiration_date)
        
        if expiring_products.empty:
            return render_template('checker.html', message="No products found expiring on or before the specified date.")
        
        table_html = tabulate(expiring_products, headers="keys", tablefmt="html", showindex=False)
        return render_template('checker.html', table=table_html, products=expiring_products.to_dict(orient='records'))
    
    return render_template('checker.html')

@app.route('/add_to_cart/<product_name>', methods=['POST'])
def add_to_cart(product_name):
    """Add product to the user's cart."""
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product_name)  # Add product to cart
    session.modified = True  # Mark session as modified
    return jsonify(success=True, product_name=product_name)

@app.route('/u_add_to_cart/<product_name>', methods=['POST'])
def u_add_to_cart(product_name):
    if 'u_cart' not in session:
        session['u_cart'] = []
    session['u_cart'].append(product_name)
    session.modified = True
    return jsonify(success=True, product_name=product_name)

@app.route('/u_get_cart', methods=['GET'])
def u_get_cart():
    cart_items = session.get('u_cart', [])
    return jsonify({'u_cart': cart_items}), 200


@app.route('/cart')
def cart():
    """Display items in the cart."""
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)

@app.route('/u_cart')
def u_cart():
    """Display items in the user's cart."""
    cart_items = session.get('u_cart', [])
    return render_template('u_cart.html', cart_items=cart_items)

@app.route('/e_commerce')
def e_commerce():
    return render_template('e_commerce.html')

@app.route('/u_e_commerce')
def u_e_commerce():
    return render_template('u_e_commerce.html')

@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    if request.method == 'POST':
        # Perform any required operations on form data here
        return redirect(url_for('payment'))
    return render_template('shipping.html')

@app.route('/u_shipping', methods=['GET', 'POST'])
def u_shipping():
    if request.method == 'POST':
        # Perform any required operations on form data here
        return redirect(url_for('u_payment'))
    return render_template('u_shipping.html')

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/u_payment')
def u_payment():
    return render_template('u_payment.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/u_contact')
def u_contact():
    return render_template('u_contact.html')

@app.route('/i_contact')
def i_contact():
    return render_template('i_contact.html')

@app.route('/logout')
def logout():
    """Log out the user and redirect to login page."""
    session.clear()  # Clear the session
    return redirect(url_for('signin'))

@app.route('/u_logout')
def u_logout():
    """Log out the user and redirect to signin page."""
    session.clear()  # Clear the user session
    return redirect(url_for('login'))

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

if __name__ == '__main__':
    app.run(debug=True)
