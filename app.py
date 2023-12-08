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
from datetime import date

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)

try:
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
    Column('fame_score', Integer),
    Column('popularity_score', Integer)
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

def get_season(north_hemisphere: bool = True) -> str:
    today = date.today()
    now = (today.month, today.day)
    if (3, 1) <= now < (6, 1):
        season = 'spring' if north_hemisphere else 'fall'
    elif (6, 1) <= now < (9, 1):
        season = 'summer' if north_hemisphere else 'winter'
    elif (9, 1) <= now < (12, 1):
        season = 'fall' if north_hemisphere else 'spring'
    else:
        season = 'winter' if north_hemisphere else 'summer'
    return season


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    metadata.create_all(engine)
    products = []
    form = Form()
    avg_price = 0
    max_price = 0
    min_price = 0
    curr_season = get_season()
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
        
        query_str = "SELECT MIN(price) AS min_price FROM product"
        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)
        min_price_result = query_db(query_str, args)
        if min_price_result and min_price_result[0][0] is not None:
            min_price = "${:,.2f}".format(min_price_result[0][0])
        else:
            min_price = "$0.00"
        
        query_str = "SELECT MAX(price) AS max_price FROM product"
        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)
        max_price_result = query_db(query_str, args)
        if max_price_result and max_price_result[0][0] is not None:
            max_price = "${:,.2f}".format(max_price_result[0][0])
        else:
            max_price = "$0.00"
        
        if products is not None and len(products) > 0:
            products_display = products[:50]
        else:
            products_display = []
        category_season_query = "SELECT season_id from seasonality WHERE category_id = ?"
        curr_season_out = query_db(category_season_query, [category])

        query_str = "SELECT fame_score, popularity_score FROM product NATURAL JOIN brand"
        if conditions:
            query_str += " WHERE " + " AND ".join(conditions)
        print(query_str)
        brand_scores = query_db(query_str, args)
        if brand_scores and brand_scores[0][0] and brand_scores[0][1] is not None:
            brand_fame = "{}%".format(brand_scores[0][0])
            brand_popularity = "{}%".format(brand_scores[0][1])
        else:
            brand_fame = None
            brand_popularity = None

        in_season = False
        out_of_season = False
        if curr_season_out and len(curr_season_out) > 0:
            in_season = (curr_season == curr_season_out[0][0])
            if in_season == False:
                if (curr_season == "winter" and curr_season_out[0][0] == "summer") or (curr_season == "summer" and curr_season_out[0][0] == "winter"):
                    out_of_season = True
        return render_template("index.html", products=products_display, form=form, 
                               avg_price=avg_price, min_price=min_price, 
                               max_price=max_price, in_season = in_season, out_season = out_of_season, 
                               item_name = item_name, brand_fame=brand_fame, brand_popularity=brand_popularity)


    return render_template("index.html", products=[], form=form, avg_price=avg_price, min_price=min_price, max_price=max_price)

@app.route("/autocomplete")
def autocomplete():
    search = request.args.get('q')
    field = request.args.get('field')
    valid_fields = {
        'category': 'category_id',
        'condition': 'condition_id',
        'brand': 'brand_id'
    }
    column = valid_fields[field]
    if field not in valid_fields:
        return jsonify([])
    suggestions = []

    _DATABASE_URL = 'project.db'

    try:
        with connect(_DATABASE_URL, isolation_level=None, uri=True) as conn:
            query = f"SELECT DISTINCT {column} FROM product WHERE {column} LIKE ? LIMIT 20"

            with closing(conn.cursor()) as cursor:
                cursor.execute(query, ('%' + search + '%',))
                result = cursor.fetchall()

            suggestions = [{"label": row[0], "value": row[0]} for row in result]
    
    except Exception as e:
        print(f"An error occurred: {e}")
    # Return the suggestions as JSON
    return jsonify(suggestions)

@app.route("/autocomplete/condition")
def autocomplete_condition():
    condition_mapping = {1: "Fair", 2: "Good", 3: "Excellent"}
    suggestions = [{"label": condition_mapping.get(key), "value": key} for key in condition_mapping]
    return jsonify(suggestions)