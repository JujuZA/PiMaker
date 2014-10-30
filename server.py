import os
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return flask.render_template('home.html')

@app.route('/stop')
def stop():
    return "Print stopped"

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5500)
