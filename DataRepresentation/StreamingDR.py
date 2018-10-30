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
    test_types = [["1", "2", "3", "4", "5", "6"], ["a", "b", "c", "d", "e", "f"]]
    sse.publish({"types": random.choice(test_types)}, type='greeting')
    return "Message sent!"