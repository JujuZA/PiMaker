from makerbot_comm import makerbot
import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

mb = makerbot()
mb.r.queue_song(3)

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['gcode'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            mb.execute_gcode_file(filename)
            return "Your file --" + filename + "-- is printing"
    return '''
    <!doctype html>
    <title>Upload a Gcode File to Print</title>
    <h1>Upload new File</h1>
    <img src = "/webcam/?action=stream">
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/printing/')
def printing(filename):
    return "Your file is printing"

if __name__ == "__main__":
   app.run('0.0.0.0')
