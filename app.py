import webview 
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import threading
import secrets
import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import cv2
from PIL import Image, ImageDraw
import numpy as np
import base64
import io
import tkinter as tk
from PIL import ImageTk, Image
import base64
import requests
from flask_socketio import SocketIO, emit
from sklearn.cluster import KMeans

app = Flask(__name__)
socketio = SocketIO(app)

# Define the upload and processed image directories
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

root = tk.Tk()
canvas = tk.Canvas(root, width=500, height=400)
canvas.pack()

brush_colour = "black"
hex_codes = []
def rgb_to_hex(rgb_array):
    # Convert each RGB value to a hex string
    # Format the values as two-digit hex strings and combine them
    hex_code = "#{:02X}{:02X}{:02X}".format(rgb_array[0], rgb_array[1], rgb_array[2])
    return hex_code

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/generatepaint')
def index():
    return render_template('start_page.html')

@app.route('/select_and_process_image', methods=['POST'])
def select_and_process_image():
    try:
        if 'image_file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['image_file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load the selected image
            img = cv2.imread(filepath)
            if img is None:
                return jsonify({'error': 'Failed to load image'})
            
            height, width, _ = img.shape
            
            # Convert to Grayscale
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Gaussian Blur
            img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

            # Canny Edge Detection
            img_edge = cv2.Canny(img_gray, 100, 200)

            # Dilate Edges
            kernel_dilate = np.ones((1, 1), np.uint8)
            thick = cv2.dilate(img_edge, kernel_dilate, iterations=1)

            # Sharpening
            kernel_sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(thick, -1, kernel_sharpen)

            # Thresholding
            threshold_value = 120
            _, binary_inverse = cv2.threshold(sharpened, threshold_value, 255, cv2.THRESH_BINARY_INV)
            binary_inverse_pil = Image.fromarray(binary_inverse)

            # Resize the processed image to match the dimensions of the selected image
            binary_inverse_pil = binary_inverse_pil.resize((500, 400))
            binary_inverse_np = np.array(binary_inverse_pil)
            
            # Define the canvas dimensions
            canvas_width = 500
            canvas_height = 400

            # Define the number of rows and columns for your grid
            n_rows = 3
            n_cols = 3

            # Calculate cell width and cell height
            cell_width = canvas_width // n_cols
            cell_height = canvas_height // n_rows
            
            if canvas_width % n_cols != 0:
                cell_width += 1
            if canvas_height % n_rows != 0:
                cell_height += 1
            # Draw grid lines on the image
            for i in range(1, n_rows):
                cv2.line(binary_inverse_np, (0, i * cell_height), (canvas_width, i * cell_height), (0, 0, 255), 1)
            for j in range(1, n_cols):
                cv2.line(binary_inverse_np, (j * cell_width, 0), (j * cell_width, canvas_height), (0, 0, 255), 1)


            # Convert the numpy array back to a PIL image
            binary_inverse_pil_with_grid = Image.fromarray(binary_inverse_np)
            
            pil_img = binary_inverse_pil_with_grid
            
            # Save the processed image
            processed_filename = f"processed_{filename}"
            processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            pil_img.save(processed_filepath)
            
            # Convert PIL image to base64
            buffered = io.BytesIO()
            pil_img.save(buffered, format="JPEG")
            processed_image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Perform K-Means clustering to identify dominant colors
            iimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            c_img = iimg.copy()
            c_img = np.reshape(c_img, (-1,3))
            
            kmeans = KMeans(n_clusters=12,random_state=2)
            kmeans.fit_predict(c_img)
            centers = kmeans.cluster_centers_.astype(int)
            per = np.array(np.unique(kmeans.labels_, return_counts=True)[1], dtype=np.float32)
            per = per/c_img.shape[0]
            dom = [ [per[ix], centers[ix]] for ix in range(kmeans.n_clusters) ]
            DOM = sorted(dom, reverse=True)
            color_p = np.zeros((50,500,3)).astype(int)

            start = 0
            for ix in range(kmeans.n_clusters):
                width = int( (DOM[ix][0])*color_p.shape[1] )
                end = start+width
                color_p[:,start:end, :] = DOM[ix][1]
                start = end
            
            for ix in range(c_img.shape[0]):
                c_img[ix] = centers[kmeans.labels_[ix]]
            c_img = np.reshape(c_img, (img.shape[0], img.shape[1], 3))
            
            color_p_flattened = color_p.reshape(-1, 3)
            unique_colors = np.unique(color_p_flattened, axis=0)
            hex_codes = [rgb_to_hex(color) for color in unique_colors]
            print("Hex Codes:", hex_codes)
            # Modify the return statement to include the processed image filename and hex codes
            return jsonify({'success': 'Image processed successfully!', 
                            'data': {'processed_image_data': processed_image_data, 
                                     'processed_filename': processed_filename,
                                     'hex_codes': hex_codes}})
        
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'An error occurred during image processing'})

    return jsonify({'error': 'Invalid file format'})

   
@app.route('/page_one')
def page_one():
    try:
        global hex_codes  # Access the global hex_codes variable
        # Pass the hex codes array as a context variable to the template
        print("Hex Codes:", hex_codes)
        return render_template('page_one.html', hex_codes=hex_codes)
        
    except Exception as e:
        print("Error:", e)

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
@app.route('/stage2_recreate')
def stage2_recreate():
    return render_template('stage2_recreate.html')
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
