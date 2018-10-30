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
    test_tags = [
        [
            {"value": 100, "name": "A"},
            {"value": 60, "name": "B"},
            {"value": 40, "name": "C"},
            {"value": 20, "name": "D"}
        ],
        [
            {"value": 100, "name": "D"},
            {"value": 60, "name": "C"},
            {"value": 40, "name": "B"},
            {"value": 20, "name": "A"}
        ]
    ]
    sse.publish({"tags": random.choice(test_tags)}, type='greeting')
    return "Message sent!"