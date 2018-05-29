from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

import numpy as np
import pandas as pd

from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Alphabet import generic_dna, generic_protein

from datetime import datetime

app = Flask(__name__)

###Database Connection
#app.config is a dict; update it with database settings
app.config.update(
    #define environment variables for the app
    SECRET_KEY = 'topsecret',
    #SQLALCHEMY_DATABASE_URI = '<database>://<user_id>:<password>@<server>/<database_name>',
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pass@localhost/catalog_db',
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

#SQLAlchemy is ORM that maps python classes to SQL database commands
db = SQLAlchemy(app)

##Create a class to describe the database table
#inherits from db.Model
class Publication(db.Model):

    #set the name of the table
    __tablename__ = 'publication'

    #two column table: id and publication name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        #self.id is added automatically
        self.name = name

    def __repr__(self):
        return 'The publisher is {}'.format(self.name)


#second db table for the books themseleves
class Book(db.Model):

    #set the name of the table
    __tablename__ = 'book'

    #multi-column db table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    author = db.Column(db.String(350))
    avg_rating = db.Column(db.Float)
    format = db.Column(db.String(50))
    image = db.Column(db.String(100), unique=True)
    num_pages = db.Column(db.Integer)
    pub_data = db.Column(db.DateTime, default=datetime.utcnow())

    #foreign key relationship to the primary key 'id' of the publishers table
    pub_id = db.Column(db.Integer, db.ForeignKey('publication.id'))

    def __init__(self, title, author, avg_rating, format, image, num_pages, pub_id):
        #self.id = id #this is done automatically for us
        self.title = title
        self.author = author
        self.avg_rating = avg_rating
        self.format = format
        self.image = image
        self.num_pages = num_pages
        self.pub_id = pub_id
        #self.pub_date = pub_date #this will be populated using the default value

    def __repr__(self):
        return '{} by {}'.format(self.title, self.author)


##Basic URL routing with flask
@app.route('/')
@app.route('/index')
def hello_flask():
    return '<h1>Flask Frontpage</h1>'

##GET request data
#Handling GET request with query string
@app.route('/new/')
def query_string(greeting='hello'):

    #extract the GET data from the request object dict using 'greeting' key
    #.get allows default value that [] does not
    #therefore, if greeting=None, default is greeting (='hello')
    query_val = request.args.get('greeting', greeting)
    return '<h1>Greeting: {} </h1>'.format(query_val)

#Better GET request without query string using <variable> in route
#<xxx> variable must be passed into the function
@app.route('/user/<name>')
def no_query_string(name='DefaultName'):
    return '<h1>Hello: {} </h1>'.format(name)

#By default anything is treated as a string
@app.route('/rc/<string:seq>')
def reverse_complement(seq):
    rc = str(Seq(seq).reverse_complement())
    return '<h1>Reverse Complement is: {}</h1>'.format(rc)

#Change this to work with integers:
@app.route('/add/<int:num1>/<int:num2>')
def addition(num1, num2):
    return '<h1>Adding {} and {} = {} </h1>'.format(num1, num2, num1+num2)

#Or floats:
@app.route('/multiply/<float:num1>/<float:num2>')
def multiply(num1, num2):
    return '<h1>Multiplying {} and {} = {} </h1>'.format(num1, num2, num1*num2)


##Rendering html templates - looks in the templates folder
@app.route('/temp/')
def show_page():
    #render_template needs the html file and any number of additional keyword arguments
    return render_template('hello.html')

##Using Jinja2
@app.route('/movies/')
def display_movies():
    #can pass additional python objects to the browser
    #and then use {{ Jinja2 }} in the html file to display the info
    movies = ['A','B','C','D']
    return render_template('movies.html', movies=movies)

#more complex example with an if statement and a dict
@app.route('/movies2/')
def display_movies_durations():

    #dict with names and durations
    movie_durations = {'A':2,'B':1,'C':2.5,'D':3.3,'E':2.2}
    return render_template('movie_durations.html', movie_durations=movie_durations)


#if .py file being executed directly, run the server
if __name__ == '__main__':
    db.create_all() #creates the database tables if they don't already exist
    app.run(debug=True, port=4997)
