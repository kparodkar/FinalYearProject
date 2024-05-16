import webview 
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import threading
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MySQL Configurationm
mysql_config = {
    'host': 'localhost',
    'user': 'root',  # Change this to your MySQL username
    'password': '',  # Change this to your MySQL password
    'database': 'test'
}

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(**mysql_config)
#classes
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
        
class Learn:
    @staticmethod
    def render():
        return render_template('learn.html')
class ColorMix:
    @staticmethod
    def render():
         return render_template('mixingcolors.html')  
class Recreatepaint:
    @staticmethod
    def render():
        return render_template('recreatepainting.html')  

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

@app.route('/learn')
def learn():
    return Learn.render()

@app.route('/mixingcolors')
def mixingcolors():
    return ColorMix.render()  

@app.route('/colormixstages')
def col_mixstage1():
    return render_template('colormixstages.html')

@app.route('/recreatepainting')
def recreatepainting():
    return render_template('recreatepainting.html')
 
@app.route('/stage2_colormixing')
def stage2_colormixing():
    return render_template('stage2_colormixing.html')    


@app.route('/stage2colmix')
def stage2colmix():
    return render_template('stage2colmix.html') 
       
@app.route('/stage1_recreate')
def stage1_recreate():
    return render_template('stage1_recreate.html') 

@app.route('/stage3_learnpaint')
def stage3_learnpaint():
    return render_template('stage3_learnpaint.html') 

from flask import Flask, render_template, request, jsonify
from PIL import Image
import os
import base64
from io import BytesIO



@app.route('/save', methods=['POST'])
def save():
    data = request.json['imageData']
    image_data = base64.b64decode(data.split(',')[1])
    image = Image.open(BytesIO(image_data))
    save_path = os.path.join('static', 'image.png')
    image.save(save_path)
    return jsonify({"message": "Image saved successfully!"})                                           
def run_flask():
    app.run()

if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Create desktop window with webview and set size
    webview.create_window("Desktop App", "http://127.0.0.1:5000", fullscreen=True)

    # Run webview
    webview.start()
