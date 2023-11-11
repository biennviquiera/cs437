import csv
import pandas as pd
from sqlalchemy import create_engine

# Create engine to connect with DB
try:
    # engine = create_engine(
    #     'postgresql://username:password@localhost:5432/name_of_base')
    engine = create_engine("sqlite:///project.db", echo=True)
except:
    print("Can't create 'engine")

# Get data from CSV file to DataFrame(Pandas)
#get path to file
with open('test.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    columns = ['train_id', 'name', 'item_condition_id', 'category_name','brand_name','price','shipping','item_description']
    df = pd.DataFrame(data=reader, columns=columns)
    df = df.filter(items=['train_id', 'item_condition_id','category_name','brand_name'])
    df.rename(columns={"train_id": "product_id", "item_condition_id": "condition_id", "category_name": "category_id", "brand_name":"brand_id",})
    

# Standart method of Pandas to deliver data from DataFrame to PastgresQL
try:
    with engine.begin() as connection:
        df.to_sql('product', con=connection, index_label='product_id', if_exists='replace')
        print('Done, ok!')
except Exception as e:
        print(e)