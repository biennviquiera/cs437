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
with open('seasonality.csv', newline='') as csvfile:
    reader = pd.read_csv(csvfile)
    columns = ['Category', 'Season']
    df = pd.DataFrame(data=reader, columns=columns)
    df = df.rename(columns={"Category": "category_id", "Season": "season_id"})
    

# Standart method of Pandas to deliver data from DataFrame to PastgresQL
try:
    with engine.begin() as connection:
        df.to_sql('product', con=connection, if_exists='replace', index=False)
        print('Done, ok!')
except Exception as e:
        print(e)