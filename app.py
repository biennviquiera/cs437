from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlite3 import connect
from contextlib import closing
from sys import stderr
import os
import jinja2
# from flask import Flask, flash, redirect, render_template, request, session, make_response, url_for

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)

engine = create_engine('sqlite:///project.db')
db = SQLAlchemy(app)
metadata = MetaData()

# Define tables
condition_table = Table('condition', metadata,
    Column('condition_id', Integer, primary_key=True),
    Column('discount_score', Integer)
)

seasonality_table = Table('seasonality', metadata,
    Column('category_id', String, primary_key=True),
    Column('season', String)
)

brand_table = Table('brand', metadata,
    Column('brand_id', String, primary_key=True),
    Column('tier', Integer),
    Column('trendy_score', Integer)
)

product_table = Table('product', metadata,
    Column('product_id', Integer, primary_key=True),
    Column('condition_id', Integer, ForeignKey('condition.condition_id')),
    Column('category_id', String, ForeignKey('seasonality.category_id')),
    Column('brand_id', String, ForeignKey('brand.brand_id')),
    Column('price', Integer)
)

class Form(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    submit = SubmitField('Submit')

_DATABASE_URL = 'project.db'  
def query_db(query, args):
    try:
        with connect(_DATABASE_URL, isolation_level=None, uri=True) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, args)
                results = cursor.fetchall()
                return results
    except Exception as ex:
        print(ex, file=stderr)
        return None
        
def insert_sample_data():
    query_db("INSERT INTO product VALUES(1,1,1,1)", [])

def print_sample_data():
    # with engine.connect() as connection:
    # with connect('project.db') as conn:
    #     with closing(conn.cursor()) as cursor:
    #         cursor.execute("SELECT * from product")
    #         products = cursor.fetchall()
    query_str = "SELECT * from product"
    products = query_db(query_str, [])
    # print(products)
    return products


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def hello_world():
    metadata.create_all(engine)
    insert_sample_data()
    products = print_sample_data()
    form = Form()
    avg_price = 0

    if form.validate_on_submit():
        # Retrieve input data from the form
        item_name = form.item_name.data
        condition = form.condition.data
        brand = form.brand.data
        print(item_name, condition, brand)

        # Construct an SQL query to search for matching rows, get avg
        query_str = "SELECT * FROM product WHERE condition_id = ? AND brand_id = ?"
        args = (condition, brand)

        # Execute the SQL query using the query_db function
        products = query_db(query_str, args)

        # SQL query to get averages
        query_str = "SELECT AVG(price) AS average_price FROM product WHERE condition_id = ? AND brand_id = ?;"
        avg_price = query_db(query_str, args)

    # return f"<p>Hello, World!</p>"
    return render_template("index.html", products = products[:20], form = form, avg_price = avg_price)