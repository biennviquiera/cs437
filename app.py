from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlite3 import connect
from contextlib import closing
from sys import stderr
import jinja2
# from flask import Flask, flash, redirect, render_template, request, session, make_response, url_for

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    Column('season_id', Integer),
    Column('score', Integer)
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
    Column('brand_id', String, ForeignKey('brand.brand_id'))
)

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


@app.route("/")
@app.route("/index")
def hello_world():
    metadata.create_all(engine)
    insert_sample_data()
    products = print_sample_data()
    # return f"<p>Hello, World!</p>"
    return render_template("index.html", products = products[:20])