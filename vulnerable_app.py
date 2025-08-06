#!/usr/bin/env python3
"""
Vulnerable Web Application for Testing SQL Injection Scanner
WARNING: This application contains intentional security vulnerabilities.
DO NOT deploy this in production or on public servers.
Use only for educational and testing purposes in isolated environments.
"""

from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Initialize database
def init_db():
    """Initialize the SQLite database with sample data"""
    if os.path.exists('test.db'):
        os.remove('test.db')
    
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT
        )
    ''')
    
    # Insert sample data
    users_data = [
        (1, 'admin', 'admin123', 'admin@test.com'),
        (2, 'user1', 'password1', 'user1@test.com'),
        (3, 'user2', 'password2', 'user2@test.com'),
        (4, 'john_doe', 'secret123', 'john@test.com')
    ]
    
    products_data = [
        (1, 'Laptop', 999.99, 'High-performance laptop'),
        (2, 'Mouse', 29.99, 'Wireless optical mouse'),
        (3, 'Keyboard', 79.99, 'Mechanical keyboard'),
        (4, 'Monitor', 299.99, '24-inch LCD monitor')
    ]
    
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', users_data)
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', products_data)
    
    conn.commit()
    conn.close()

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Test App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .nav { background: #f0f0f0; padding: 15px; margin-bottom: 20px; }
        .nav a { margin-right: 20px; text-decoration: none; color: #333; }
        .form-group { margin-bottom: 15px; }
        input[type="text"], input[type="password"] { padding: 8px; width: 200px; }
        input[type="submit"] { padding: 10px 20px; background: #007cba; color: white; border: none; }
        .warning { background: #ffebee; padding: 15px; border-left: 4px solid #f44336; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="warning">
            <strong>⚠️ WARNING:</strong> This is a deliberately vulnerable application for testing purposes only!
        </div>
        
        <div class="nav">
            <a href="/">Home</a>
            <a href="/login">Login</a>
            <a href="/search">Search Products</a>
            <a href="/user">User Profile</a>
            <a href="/news">News</a>
        </div>
        
        <h1>Vulnerable Test Application</h1>
        <p>This application contains several SQL injection vulnerabilities for testing your scanner:</p>
        
        <h3>Available Test Endpoints:</h3>
        <ul>
            <li><strong>GET /login?username=X&password=Y</strong> - Vulnerable login via GET</li>
            <li><strong>POST /login</strong> - Vulnerable login via POST</li>
            <li><strong>GET /search?q=X</strong> - Vulnerable product search</li>
            <li><strong>GET /user?id=X</strong> - Vulnerable user profile lookup</li>
            <li><strong>GET /news?category=X</strong> - Vulnerable news filtering</li>
        </ul>
        
        <h3>Sample SQL Injection Tests:</h3>
        <ul>
            <li><code>/login?username=admin'--&password=anything</code></li>
            <li><code>/search?q=' OR 1=1--</code></li>
            <li><code>/user?id=1' UNION SELECT 1,2,3,4--</code></li>
        </ul>
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Vulnerable Test App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 400px; margin: 0 auto; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="password"] { padding: 8px; width: 100%; box-sizing: border-box; }
        input[type="submit"] { padding: 10px 20px; background: #007cba; color: white; border: none; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <input type="submit" value="Login">
        </form>
        
        <p><a href="/">Back to Home</a></p>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if success %}
            <div class="success">{{ success }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return HOME_TEMPLATE

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    
    if request.method == 'GET' and (request.args.get('username') or request.args.get('password')):
        # Vulnerable GET login
        username = request.args.get('username', '')
        password = request.args.get('password', '')
    elif request.method == 'POST':
        # Vulnerable POST login
        username = request.form.get('username', '')
        password = request.form.get('password', '')
    else:
        return render_template_string(LOGIN_TEMPLATE)
    
    if username and password:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # VULNERABLE: Direct string concatenation - susceptible to SQL injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                success = f"Login successful! Welcome {result[1]}"
            else:
                error = "Invalid credentials"
                
        except sqlite3.Error as e:
            # Make sure SQL errors are visible for detection
            error = f"SQL Error: {str(e)}"
        
        conn.close()
    
    return render_template_string(LOGIN_TEMPLATE, error=error, success=success)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    error = None
    
    if query:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # VULNERABLE: Direct string concatenation
        sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
        
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except sqlite3.Error as e:
            error = f"SQL syntax error: {str(e)}"
        
        conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>Product Search</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h2>Product Search</h2>
        <form method="GET">
            <input type="text" name="q" value="{}" placeholder="Search products...">
            <input type="submit" value="Search">
        </form>
        <p><a href="/">Back to Home</a></p>
        
        {}
        
        {}
    </body>
    </html>
    '''.format(
        query,
        f'<p style="color: red;">Error: {error}</p>' if error else '',
        '<h3>Results:</h3><ul>' + ''.join([f'<li>{r[1]} - ${r[2]}</li>' for r in results]) + '</ul>' if results else '<p>No results found.</p>' if query else ''
    )
    
    return html

@app.route('/user')
def user_profile():
    user_id = request.args.get('id', '')
    user_data = None
    error = None
    
    if user_id:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # VULNERABLE: Direct string concatenation
        sql = f"SELECT * FROM users WHERE id = {user_id}"
        
        try:
            cursor.execute(sql)
            user_data = cursor.fetchone()
        except sqlite3.Error as e:
            error = f"SQL syntax error: {str(e)}"
        
        conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>User Profile</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h2>User Profile</h2>
        <form method="GET">
            <input type="text" name="id" value="{}" placeholder="User ID">
            <input type="submit" value="Get Profile">
        </form>
        <p><a href="/">Back to Home</a></p>
        
        {}
        
        {}
    </body>
    </html>
    '''.format(
        user_id,
        f'<p style="color: red;">Error: {error}</p>' if error else '',
        f'<h3>User Info:</h3><p>ID: {user_data[0]}<br>Username: {user_data[1]}<br>Email: {user_data[3]}</p>' if user_data else '<p>User not found.</p>' if user_id else ''
    )
    
    return html

@app.route('/news')
def news():
    category = request.args.get('category', '')
    error = None
    
    # Simulated vulnerable query (no actual news table, but will trigger SQL errors)
    if category:
        # VULNERABLE: This will cause SQL syntax errors for injection testing
        try:
            conn = sqlite3.connect('test.db')
            cursor = conn.cursor()
            
            # This query will fail but demonstrate SQL injection detection
            sql = f"SELECT * FROM news WHERE category = '{category}'"
            cursor.execute(sql)
            
        except sqlite3.Error as e:
            error = f"SQL syntax error in news query: {str(e)}"
        
        conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head><title>News</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h2>News Section</h2>
        <form method="GET">
            <input type="text" name="category" value="{}" placeholder="News category">
            <input type="submit" value="Filter News">
        </form>
        <p><a href="/">Back to Home</a></p>
        
        {}
        
        <p>This endpoint is intentionally broken to test SQL error detection.</p>
    </body>
    </html>
    '''.format(
        category,
        f'<p style="color: red;">Error: {error}</p>' if error else ''
    )
    
    return html

if __name__ == '__main__':
    print("⚠️  SECURITY WARNING ⚠️")
    print("This application contains intentional vulnerabilities!")
    print("Only use for testing in isolated environments.")
    print("=" * 50)
    
    # Initialize database
    init_db()
    print("✅ Database initialized with sample data")
    
    # Run the app
    print("🚀 Starting vulnerable web application...")
    print("📍 Access at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
