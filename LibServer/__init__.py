"""
The flask application package.
"""

from flask import Flask,render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html',year=2017,title="Hello!")