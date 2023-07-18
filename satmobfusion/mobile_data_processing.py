import skmob
import geopandas as gpd
import pandas as pd

class mobiledatamodule():
    def __init__(self, data=None, file_path=None):
        self.file_path = file_path

        if file_path is not None:
            self.read_data(file_path)
        elif data is not None:
            self.data = data
    
    def read_data(self, file_path):
        self.data = pd.read_csv(file_path)
        return self.data
    
    def read_as_gdf(self, crs, lat='lat', lng='lon'):
        self.data_gdf = gpd.GeoDataFrame(self.data, crs=crs, geometry=gpd.points_from_xy(df[lng], df[lat]))
        return self.data_gdf
    
    def add_datetime(self, time_col = 'timestamp', unit='s'):
        self.data['datetime'] = pd.to_datetime(self.data[time_col], unit=unit)

    def choose_user(self, uid):
        return self.data[self.data.uid == uid]
    
    def subset_by_time(self, starttime, endtime, datetime='datetime'):
        if (starttime is not None) & (endtime is not None):
            return self.data[(self.data[datetime] >= starttime) & (self.data[datetime] <= endtime)].reset_index()
        elif (starttime is not None) & (endtime is None):
            return self.data[self.data[datetime] >= starttime].reset_index()
        elif (endtime is not None) & (starttime is None):
            return self.data[self.data[datetime] <= endtime].reset_index()
    
    def subset_by_geo(self, geo_df, data_gdf=None, how='left', predicate='predicate'):
        if (self.data_gdf is None) & (data_gdf is None):
            return "Please run the read_as_gdf() function or pass a GeoDataFrame as an argument!"
        else:
            return gpd.sjoin(data_gdf, geo_df, how=how, predicate=predicate)


def preprocess_mobile_data(df, state_df=None, crs='EPSG:4269', max_speed_kmh=400, spatial_radius_km=0.2):
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=gpd.points_from_xy(df['lon'], df['lat']))

    # Exclude points outside of relevant state
    if state_df is not None:
        gdf = gpd.sjoin(gdf, state_df, how='left', predicate='within')

    # Create datetime column using timestamps
    gdf['datetime'] = pd.to_datetime(gdf['timestamp'], unit='s')

    # Keep first 13 columns
    #comp1_gpd = comp1_gpd.iloc[:, :13]
    # Create a date column
    #comp1_gpd['date'] = comp1_gpd['datetime'].dt.date
    tdf = skmob.TrajDataFrame(gdf, latitude='lat', longitude='lon', datetime='datetime', user_id='uid')
    print('Original number of points: ', tdf.shape[0])
    f_tdf = skmob.preprocessing.filtering.filter(tdf, max_speed_kmh=max_speed_kmh, include_loops=False)
    print('Number of points after filtering: ', f_tdf.shape[0])
    fc_tdf = skmob.preprocessing.compression.compress(f_tdf, spatial_radius_km=spatial_radius_km)
    print('Number of points after compression: ', fc_tdf.shape[0])

    preproc_gdf = gpd.GeoDataFrame(fc_tdf, crs=crs, geometry=gpd.points_from_xy(fc_tdf['lng'], fc_tdf['lat']))
    preproc_gdf['datetime'] = pd.to_datetime(preproc_gdf['datetime'], format='%Y-%m-%d %H:%M:%S')  
    return preproc_gdf  