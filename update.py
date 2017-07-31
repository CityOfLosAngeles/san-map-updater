import pandas as pd
import folium

if __name__ == '__main__':
    readings_df = pd.read_csv('https://docs.google.com/spreadsheets/d/1WuwQwoloZsbl9vJoMUj7COMhiPVo8SncIU85dG_vjow/export?gid=0&format=csv',
                              skiprows=[0,1,2])
    location_df = pd.read_csv('https://docs.google.com/spreadsheets/d/1WuwQwoloZsbl9vJoMUj7COMhiPVo8SncIU85dG_vjow/export?gid=1752938175&format=csv')
    location_df['station_id'] = location_df['LARWMP Station ID'].apply(lambda x: int(x[-3:]))
    map = folium.Map(location=[34.0407, -118.2468],
                     zoom_start=12,
                     tiles='Stamen Terrain')
    for location in location_df.iterrows():
        folium.Marker([location[1]['Latitude'],location[1]['Longitude']], popup=location[1]['Station Description']).add_to(map)
    map.save('output.html')
