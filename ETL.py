"""
Ce fichier permet de créer la base de données à partir du dataset
"""
import pandas as pd
import os
import sqlite3

folder_path = "datas/"

dataframes = []


for file in os.listdir(folder_path):
    if file.endswith(".parquet"):
        file_path = os.path.join(folder_path, file)
        df = pd.read_parquet(file_path)
        dataframes.append(df)


nyc_data = pd.concat(dataframes, ignore_index=True)
print(nyc_data.head())
print(nyc_data.info())

nyc_data['pickup_datetime'] = pd.to_datetime(nyc_data['tpep_pickup_datetime'], errors='coerce')

nyc_data['pickup_date'] = nyc_data['pickup_datetime'].dt.date
nyc_data['pickup_hour'] = nyc_data['pickup_datetime'].dt.hour 

df_aggregated = nyc_data.groupby(['pickup_date','pickup_hour', 'payment_type']).agg(
    total_rides=('PULocationID', 'count'),
    total_distance=('trip_distance', 'sum'),
    total_passenger=('passenger_count', 'sum'),
    total_tips=('tip_amount', 'sum'), 
    total_amount=('total_amount', 'sum')
).reset_index()


df_weather = pd.read_csv('datas/weather.csv')


df_weather['datetime'] = pd.to_datetime(df_weather['datetime'], errors='coerce').dt.date
df_weather = df_weather[['datetime', 'tempmax', 'tempmin', 'temp', 'feelslikemax', 'feelslikemin', 'feelslike', 'humidity', 'snow']]

df_final = pd.merge(df_aggregated, df_weather, left_on='pickup_date', right_on='datetime', how='inner')

df_final = df_final.drop(columns=['datetime'])

print(df_final.head())
print(df_final.info())

conn = sqlite3.connect("nyc_taxi_data.db")

df_final.to_sql("taxi_trips", conn, if_exists="replace", index=False)

print(pd.read_sql("SELECT * FROM taxi_trips", conn))
