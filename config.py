from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os

consumerKey = os.getenv('APIKey')
consumerKeySecret = os.getenv('APIKeySecret')
accessToken = os.getenv('accessToken')
accessTokenSecret = os.getenv('accessTokenSecret')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('dbURI')
db = SQLAlchemy(app)

class Question:
    statusID = db.Column(db.Integer, primary_key = True)
    correctAnswer = db.Column(db.Integer, nullable = False)