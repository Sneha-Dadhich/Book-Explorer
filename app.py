from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import math
import requests
from bs4 import BeautifulSoup
import time
import re
import uuid

# Create an app instance
app = Flask(__name__)

# Configuring the MySQL database
app.secret_key = '9f2c1f3d9b6f4c1d8c7e2a9a0e3b5f78' # If it's missing or weak, users can tamper with session data.
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vasu__8088'  # Your MySql password
app.config['MYSQL_DB'] = 'book_explorer_db'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# -------------------- REGISTER --------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Validations
        if not username or not password or not email:
            msg = 'Please fill out all fields.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'^[A-Za-z0-9_]+$', username):
            msg = 'Username must contain only letters, numbers, and underscores.'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE name = %s', (username,))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists!'
            else:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    'INSERT INTO users (id, name, password, email) VALUES (%s, %s, %s, %s)',
                    (str(uuid.uuid4()), username, hashed_password, email)
                )
                mysql.connection.commit()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    return render_template('register.html', msg=msg)

# -------------------- LOGIN --------------------
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            msg = 'Please fill out all fields.'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account and check_password_hash(account['password'], password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('dashboard'))
            else:
                msg = 'Incorrect username or password.'
    return render_template('login.html', msg=msg)

# -------------------- DASHBOARD --------------------
@app.route('/dashboard')
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('books.html', username=session['username'])
    return redirect(url_for('login'))


# Helper function to scrape books
def scrape_books():
    base_url = 'http://books.toscrape.com/'
    url = base_url
    books_data = []
    
    # Simple check for database population to avoid re-scraping
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM books')
    count = cursor.fetchone()[0]
    if count > 0:
        print("Database already has books. Skipping scrape.")
        return books_data
        
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all('article', class_='product_pod')

            for book in books:
                title = book.h3.a['title']
                price_text = book.find('p', class_='price_color').text
                price = float(price_text.strip('£'))
                stock_availability = book.find('p', class_='instock availability').text.strip()
                rating_class = book.find('p', class_='star-rating')['class'][-1].lower()
                rating_map = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                rating = rating_map.get(rating_class)
                thumbnail_url = base_url + book.find('div', class_='image_container').a.img['src'].replace('../', '')

                books_data.append({
                    'id': str(uuid.uuid4()),
                    'title': title,
                    'price': price,
                    'stock_availability': stock_availability,
                    'rating': rating,
                    'thumbnail_image_url': thumbnail_url
                })
            
            next_button = soup.find('li', class_='next')
            if next_button:
                url = base_url + next_button.a['href']
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            break
            
    # Insert data into database
    if books_data:
        try:
            cursor.executemany(
                "INSERT INTO books (id, title, price, stock_availability, rating, thumbnail_image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                [(book['id'], book['title'], book['price'], book['stock_availability'], book['rating'], book['thumbnail_image_url']) for book in books_data]
            )
            mysql.connection.commit()
            print(f"Successfully scraped and stored {len(books_data)} books.")
        except Exception as e:
            print(f"Failed to insert books into database: {e}")
    cursor.close()
    return books_data

# Function to create a table on startup
def setup_database():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock_availability VARCHAR(50),
                rating INT,
                thumbnail_image_url VARCHAR(255)
            )
        """)
        mysql.connection.commit()
        print("Database setup complete.")
    except Exception as e:
        print(f"Error during database setup: {e}")
    finally:
        cursor.close()

# Main route for books API with search and filter
@app.route('/api/books', methods=['GET'])
def get_books():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search_term = request.args.get('search', '')
        rating = request.args.get('rating', type=int)
        in_stock = request.args.get('in_stock', '')

        # Build the SQL query with dynamic filtering
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND title LIKE %s"
            params.append(f"%{search_term}%")
        
        if rating is not None:
            query += " AND rating >= %s"
            params.append(rating)

        if in_stock:
            query += " AND stock_availability LIKE %s"
            params.append(f"%{in_stock}%")

        # Get total number of filtered books for pagination
        count_query = query.replace("SELECT *", "SELECT COUNT(*) AS total", 1)
        cursor.execute(count_query, tuple(params))
        total_books = cursor.fetchone()['total']
        # total_books = cursor.fetchone()['COUNT(*)']

        # Add pagination to the query
        offset = (page - 1) * limit
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, tuple(params))
        books = cursor.fetchall()
        
        return jsonify({
            'books': books,
            'total_books': total_books,
            'current_page': page,
            'total_pages': math.ceil(total_books / limit)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Route for a single book's details
@app.route('/api/books/<string:book_id>', methods=['GET'])
def get_book_details(book_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(book)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    with app.app_context():
        setup_database()
        scrape_books()
    app.run(debug=True)

# Sneha
# Sneha@@11