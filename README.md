
---

# 📘 Book Explorer

Book Explorer is a **Flask-based web application** that scrapes book data from [Books to Scrape](http://books.toscrape.com/) and provides:

* **User Authentication** (Register, Login, Logout) with secure password hashing.
* **Book Scraper** that populates a MySQL database with book details.
* **REST API** to search, filter, and paginate through books.
* **Frontend Pages** (Login, Register, Dashboard/Books).

---

## 🚀 Features

* 🔐 **User System**

  * Register with username, email, and password.
  * Passwords are hashed using Werkzeug for security.
  * Login and Logout functionality.

* 📚 **Book Scraper**

  * Scrapes book data from [Books to Scrape](http://books.toscrape.com/).
  * Stores data in MySQL with fields like `title`, `price`, `rating`, `stock_availability`, and `thumbnail`.

* 🌐 **Book API**

  * `GET /api/books` → Paginated and filterable book list.
  * `GET /api/books/<book_id>` → Single book details.
  * Supports search (`title`), filter (`rating`, `in_stock`), and pagination.

---

## 🛠️ Tech Stack

* **Backend**: Flask (Python)
* **Database**: MySQL
* **Web Scraping**: BeautifulSoup + Requests
* **Authentication**: Flask sessions + Werkzeug Security
* **Frontend**: HTML templates (Jinja2)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/book-explorer.git
cd book-explorer
```

### 2️⃣ Create Virtual Environment (Optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac
```

### 3️⃣ Install Dependencies

```bash
pip install flask flask-mysqldb requests beautifulsoup4 werkzeug
```

### 4️⃣ Configure Database

* Open MySQL and create database:

```sql
CREATE DATABASE book_explorer_db;
```

* Create **users** table:

```sql
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
```

* The app automatically creates the **books** table on startup.

### 5️⃣ Update Database Credentials

Edit in `app.py`:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'yourpassword'
app.config['MYSQL_DB'] = 'book_explorer_db'
```

### 6️⃣ Run the App

```bash
python app.py
```

App will start at 👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🔑 API Endpoints

### 1. Get Books

```http
GET /api/books?page=1&limit=10&search=python&rating=4&in_stock=In%20stock
```

**Query Params:**

* `page` → Page number (default `1`)
* `limit` → Number of results per page (default `10`)
* `search` → Search by title (optional)
* `rating` → Filter by minimum rating (1–5)
* `in_stock` → Filter by stock availability (`In stock`)

**Response Example:**

```json
{
  "books": [
    {
      "id": "1234-uuid",
      "title": "Book Title",
      "price": 45.50,
      "stock_availability": "In stock",
      "rating": 4,
      "thumbnail_image_url": "http://books.toscrape.com/media/book.jpg"
    }
  ],
  "total_books": 50,
  "current_page": 1,
  "total_pages": 5
}
```

---

### 2. Get Book Details

```http
GET /api/books/<book_id>
```

**Response Example:**

```json
{
  "id": "1234-uuid",
  "title": "Book Title",
  "price": 45.50,
  "stock_availability": "In stock",
  "rating": 4,
  "thumbnail_image_url": "http://books.toscrape.com/media/book.jpg"
}
```

---

## 👤 Authentication Routes

* `/register` → User Registration
* `/login` → User Login
* `/logout` → Logout

---

## 📝 Notes

* Books are scraped automatically on first run. If books already exist in DB, scraping is skipped.
* Passwords are never stored in plain text.

---

## 📌 Future Improvements

* Add book favorites for each user.
* Implement JWT-based authentication for APIs.
* Add Docker support for easy deployment.

---

