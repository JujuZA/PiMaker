import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
   app.run('0.0.0.0')
