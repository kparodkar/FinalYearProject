import webview
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import threading
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',  # Change this to your MySQL username
    'password': '',  # Change this to your MySQL password
    'database': 'test'
}

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(**mysql_config)

# Define classes for each page
class StartPage:
    @staticmethod
    def render():
        return render_template('home.html')

class SignUpPage:
    @staticmethod
    def render():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            conn = get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()
            conn.close()
            
            return redirect('/login')
        
        return render_template('signup.html')

class LoginPage:
    @staticmethod
    def render():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            conn = get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['username'] = user[1]
                return redirect('/modules')
            else:
                return 'Invalid username or password'
        
        return render_template('login.html')

class ModulesPage:
    @staticmethod
    def render():
        if 'username' in session:
            return render_template('modules.html')
        else:
            return redirect('/login')
        

# Route for each page
@app.route('/')
def start():
    return StartPage.render()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return SignUpPage.render()

@app.route('/login', methods=['GET', 'POST'])
def login():
    return LoginPage.render()

@app.route('/modules')
def modules():
    return ModulesPage.render()

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


def run_flask():
    app.run()

if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Create desktop window with webview and set size
    webview.create_window("Desktop App", "http://127.0.0.1:5000", width=1000, height=600)

    # Run webview
    webview.start()
