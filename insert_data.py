import csv
import pandas as pd
from sqlalchemy import create_engine
import emoji
import re
from unicodedata import normalize

def clean_data(df):
    #remove emojis
    df['name'] = df['name'].apply(lambda s: emoji.replace_emoji(s, ''))
    #remove non alpha-numeric
    df['name'] = df.name.str.replace('[^a-zA-Z0-9]', '')
    df['name'] = df['name'].apply(lambda s: normalize('NFKD', s).encode('ascii','ignore').decode('ascii'))
    return df

# Create engine to connect with DB
try:
    # engine = create_engine(
    #     'postgresql://username:password@localhost:5432/name_of_base')
    engine = create_engine("sqlite:///project.db", echo=True)
except:
    print("Can't create 'engine")

# Get data from CSV file to DataFrame(Pandas)
#get path to file
with open('train.tsv', newline='') as csvfile:
    reader = pd.read_csv(csvfile, sep='\t')
    # reader = csv.DictReader(csvfile, sep='\t')
    columns = ['train_id', 'name', 'item_condition_id', 'category_name','brand_name','price','shipping','item_description']
    df = pd.DataFrame(data=reader, columns=columns)
    df = df.filter(items=['train_id', 'name', 'item_condition_id','category_name','brand_name','price'])
    df = df.rename(columns={"train_id": "product_id", "name": "name", "item_condition_id": "condition_id", "category_name": "category_id", "brand_name":"brand_id",'price':'price'})
    df = clean_data(df)

# Standart method of Pandas to deliver data from DataFrame to PastgresQL
try:
    with engine.begin() as connection:
        df.to_sql('product', con=connection, if_exists='replace', index=False)
        print('Done, ok!')
except Exception as e:
        print(e)