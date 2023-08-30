from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def connect_to_mongodb():
    client = MongoClient('mongodb+srv://2409:2409@cluster0.b6wokfx.mongodb.net/?retryWrites=true&w=majority')
    db = client['auction']
    return db

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        db = connect_to_mongodb()
        collection = db['products']
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        product_data = {
            'name': name,
            'description': description,
            'price': price
        }
        collection.insert_one(product_data)
        return 'Product added to the database!'
    else:
        db = connect_to_mongodb()
        collection = db['products']
        products = collection.find()
        return render_template('product.html', products=products)

@app.route('/client')
def client():
    return render_template('client.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = connect_to_mongodb()
        collection = db['users']
        email = request.form.get('email')
        password = request.form.get('password')
        user = collection.find_one({'email': email, 'password': password})
        if user:
            return redirect(url_for('place_bid'))
        else:
            return render_template('client.html', message='Invalid email or password')
    else:
        return render_template('client.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = connect_to_mongodb()
        collection = db['users']
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        collection.insert_one(user_data)
        return redirect(url_for('login', message='Registration successful!'))
    else:
        return render_template('register.html')

@app.route('/place_bid', methods=['GET', 'POST'])
def place_bid():
    if request.method == 'POST':
        db = connect_to_mongodb()
        collection = db['bids']
        username = request.form.get('username')
        password = request.form.get('password')
        bid_amount = float(request.form.get('bid-amount'))
        product = request.form.get('product')
        user_collection = db['users']
        user = user_collection.find_one({'username': username, 'password': password})
        if user:
            products_collection = db['products']
            product_data = products_collection.find_one({'name': product})
            if product_data:
                current_price = product_data['price']
                if bid_amount > float(current_price):
                    bid_data = {
                        'product': product,
                        'username': username,
                        'bid_amount': bid_amount
                    }
                    collection.insert_one(bid_data)
                    return redirect(url_for('result'))
                else:
                    return render_template('place_bid.html', message='Bid amount must be higher than the current price')
            else:
                return render_template('place_bid.html', message='Product not found')
        else:
            return render_template('place_bid.html', message='Invalid username or password')
    else:
        db = connect_to_mongodb()
        collection = db['products']
        products = collection.find()
        return render_template('place_bid.html', products=products)


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/result')
def result():
    db = connect_to_mongodb()
    bids_collection = db['bids']
    products_collection = db['products']
    bids = bids_collection.find()
    results = []
    max_bids = []

    for index, bid in enumerate(bids):
        product = products_collection.find_one({'name': bid['product']})
        result_data = {
            'serial_no': index + 1,
            'product': bid['product'],
            'username': bid['username'],
            'bid_amount': bid['bid_amount'],
            'price': product['price']
        }
        results.append(result_data)

    product_names = products_collection.distinct('name')
    for product_name in product_names:
        max_bid = bids_collection.find_one({'product': product_name}, sort=[('bid_amount', -1)])
        if max_bid:
            max_bids.append(max_bid)

    return render_template('result.html', results=results, max_bids=max_bids)



@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

if __name__ == '__main__':
    app.run(debug=True, port=1234)
