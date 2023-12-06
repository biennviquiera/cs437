from flask import Flask, render_template, request, jsonify
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

try:
    # engine = create_engine(
    #     'postgresql://username:password@localhost:5432/name_of_base')
    engine = create_engine("sqlite:///project.db", echo=True)
except:
    print("Can't create 'engine")

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
    item_name = StringField('Item Name')
    category = StringField('Category')
    condition = StringField('Condition')
    brand = StringField('Brand')
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
def index():
    metadata.create_all(engine)
    insert_sample_data()
    products = print_sample_data()
    form = Form()
    avg_price = 0

    if form.validate_on_submit():
        item_name = form.item_name.data
        condition = form.condition.data
        category = form.category.data
        brand = form.brand.data
        print(item_name, condition, brand)

        conditions = []
        args = []
        # Build SQL Query based on provided fields
        if condition:
            conditions.append("condition_id = ?")
            args.append(condition)
        if brand:
            conditions.append("brand_id = ?")
            args.append(brand)
        if category:
            conditions.append("category_id = ?")
            args.append(category)

        query_str = "SELECT * FROM product"
        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)
        products = query_db(query_str, args)

        query_str = "SELECT AVG(price) AS average_price FROM product"
        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)
        avg_price_result = query_db(query_str, args)
        if avg_price_result and avg_price_result[0][0] is not None:
            avg_price = "${:,.2f}".format(avg_price_result[0][0])
        else:
            avg_price = "$0.00"

    return render_template("index.html", products=products[:20], form=form, avg_price=avg_price)

@app.route("/autocomplete")
def autocomplete():
    search = request.args.get('q')
    suggestions = []

    _DATABASE_URL = 'project.db'

    try:
        with connect(_DATABASE_URL, isolation_level=None, uri=True) as conn:
            # Prepare the SQL query. Use parameterized queries to prevent SQL injection
            query = "SELECT DISTINCT category_id FROM product WHERE category_id LIKE ? LIMIT 20"

            # Execute the query with the search term
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, ('%' + search + '%',))
                result = cursor.fetchall()

            # Process the result and prepare the suggestions list
            suggestions = [{"label": row[0], "value": row[0]} for row in result]
    
    except Exception as e:
        print(f"An error occurred: {e}")
    # Return the suggestions as JSON
    return jsonify(suggestions)
