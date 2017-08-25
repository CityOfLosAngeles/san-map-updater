
# coding: utf-8


import pandas as pd
from scipy.stats import mstats
import folium
import numpy as np
import scipy as sp
import datetime
import boto3

def loc_lookup_color(location): 
    try: 
        return colors[str(location[1]['station_id'])]
    except IndexError: 
        return 'lightgray'

def gen_text_for_popup(location):
    return location[1]['Station Description'] + '\n'            + 'lat: ' + str(location[1]['Latitude']) + '\n'            + 'long: ' + str(location[1]['Longitude']) + '\n'            + 'Description: ' + location[1]['Station Description']


def set_color(c):
    num_readings = c.count()
    if num_readings >= 5:
        c = c.dropna()
        c = pd.to_numeric(c)
        geo_mean = sp.stats.mstats.gmean(c.values)
        if geo_mean <= 127 or (c > 235).count() <= 2: 
            """Green – Rolling Geo Mean using the last 5 sample results within 35 days is 
            <127 and <2 single sample results >235 using those same 5 sample results."""
            return 'green'
        elif geo_mean >= 126 and geo_mean <= 160 or (c > 235).count() > 235:
            """Rolling Geo Mean is >126 and <160 and 2 or more single samples >235"""
            return 'orange'
        else:
            return 'red'
    else:
        return 'lightgray'

def lambda_job(event, context):

    readings_df = pd.read_csv('https://docs.google.com/spreadsheets/d/1WuwQwoloZsbl9vJoMUj7COMhiPVo8SncIU85dG_vjow/export?gid=0&format=csv',
                              skiprows=[0,1,2])
    location_df = pd.read_csv('https://docs.google.com/spreadsheets/d/1WuwQwoloZsbl9vJoMUj7COMhiPVo8SncIU85dG_vjow/export?gid=1752938175&format=csv')
    location_df['station_id'] = location_df['LARWMP Station ID'].apply(lambda x: int(x[-3:]))
    m = folium.Map(location=[34.0407, -118.2468],
                     zoom_start=12,
                     tiles='Stamen Terrain')
    SINGLE_SAMPLE_LIMT = 235
    GEO_MEAN_LIMIT = 126
    SAMPLE_RANGE = 35
    readings_df['date'] = pd.to_datetime(readings_df['DATE'])

    cur_date = datetime.date.today()
    mask = (readings_df['date'] > cur_date - datetime.timedelta(days=SAMPLE_RANGE))         & (readings_df['date'] <= cur_date)
    readings = readings_df.loc[mask]
    readings = readings.set_index('date')
    del(readings['DATE'])


    readings.replace(to_replace='<10', value=5, inplace=True)
    readings.replace(to_replace='NS', value=np.nan, inplace=True)
    output_color_data = {}
    colors = readings.apply(set_color)

    for location in location_df.iterrows():
        folium.Marker([location[1]['Latitude'],location[1]['Longitude']], 
                       popup=gen_text_for_popup(location),
                       icon = folium.Icon(color = loc_lookup_color(location))).add_to(m)

    m.save('output.html')
    s3 = boto3.resource('s3')
    data = open('output.html', 'rb')
    s3.Bucket('la-san-readings-map').put_object(Key='output.html', Body=data)

if __name__ == '__main__':
    lambda_job('ev','con')



