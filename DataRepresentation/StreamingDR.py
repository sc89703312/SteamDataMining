from flask import Flask, render_template
from flask_sse import sse
import random

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/hello')
def publish_hello():
    return render_template("eval.html")

@app.route('/price')
def  price():
    return render_template("prices.html")