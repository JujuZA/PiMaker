import os
import flask
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/pi/finalapp/gcode'
ALLOWED_EXTENSIONS = set(['gcode'])

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print app.config['UPLOAD_FOLDER']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return flask.render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5500)