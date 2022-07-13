import psycopg2
import math
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import polygonize
import fiona
import matplotlib.pyplot as plt
import shapely
import numpy as np
import csv
import pandas as pd
from shapely import wkt
import folium


def db_conn():
    
    conn = psycopg2.connect(
        host="34.159.36.105",
        port ="5432",
        database="geodp",
        user="postgres", 
        password='postgres')
    cur = conn.cursor()

    return cur, conn


'''def disconnect_db():
    conn = getattr(g, 'db', None)
    if conn is not None:
        conn.close()
        g.db = None'''


'''The function calculates the number of data points in the database'''
def get_data_points_count():
    cursor, conn = db_conn()
    cursor.execute("SELECT COUNT(*) from mediumdata;")
    rows = cursor.fetchall()
    cursor.close()

    result = []
    for index in range(len(rows)):
        result.append(
            rows[index][0])

    
    return result[0]

'''The function calculates the grid size m depending on the number of data points (from the paper "Differentially Private Grids for Geospatial Data")'''
def get_grid_size(n):
    c = 10
    epsilon = 0.1
    #print(n)
    m = math.sqrt((n*epsilon)/c)
    #print(m)
    return m


'''This function '''
def get_geometry(table):
    cursor, conn = db_conn()
    cursor.execute("SELECT st_x(geom), st_y(geom), state FROM "+table+";")
    rows = cursor.fetchall()
    cursor.close()

    result = []
    for index in range(len(rows)):
        result.append([
            rows[index][0],
            rows[index][1],
            rows[index][2]
            
        ])
    
    return result

def initial_points(table):

    l = get_geometry(table)
    x = []
    y = []
    states = []
    for i in l:
        x.append(i[0])
        y.append(i[1])
        states.append(i[2])
    states = list(set(states))

    points = gpd.GeoDataFrame({"x":x,"y":y})
    points['geometry'] = points.apply(lambda p: Point(p.x, p.y), axis=1)
    points_unique = points.drop_duplicates()

    return points_unique,states


def create_grid(points_unique,n):
    #n = get_data_points_count()
    #print(n)
    cell_size = get_grid_size(n) #0.7616 
    xmin, ymin, xmax, ymax= points_unique.total_bounds
    # how many cells across and down
    #n_cells=30
    #cell_size = 0.7616#(xmax-xmin)/n_cells
    # projection of the grid
    crs = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
    # create the cells in a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_size, cell_size ):
        for y0 in np.arange(ymin, ymax+cell_size, cell_size):
            # bounds
            x1 = x0-cell_size
            y1 = y0+cell_size
            grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
    cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], 
                                    crs=crs)

    return cell


def plot_points(points,cells,states_list):
    
    states = gpd.read_file('data/tl_2021_us_state.shp')
    states = states.to_crs("EPSG:4326")
    states.boundary.plot(color = 'grey')

    #print(states[states['NAME'].isin(states_list)])
    
    base = states[states['NAME'].isin(states_list)].plot(color='white', edgecolor='black',figsize=(12, 8))
    plt.autoscale(False)
    points.plot(ax=base, marker='o', color='blue', markersize=5)
    cells.plot(ax=base, facecolor="none", edgecolor='grey')
    base.axis("off")


    

def get_cell_counts(points_unique,cell):
    cell = cell.reset_index().rename(columns = {'index':'id'})
    pointInPolys = gpd.sjoin(points_unique, cell, how='inner', op = 'intersects')
    pointInPolys = pointInPolys.drop_duplicates(subset=['x', 'y'], keep='first')
    count_points = pointInPolys.groupby(['id']).size().reset_index(name='count')
    cell_counts = pd.merge(cell,count_points, on = 'id')
    
    eps = 0.1
    dp_count = []
    for row in cell_counts.iterrows():
        dp_count.append(row[1]['count']+np.random.laplace(0, 1 / eps, 1)[0])
    cell_counts['count_dp'] = dp_count
    cell_counts['count_dp'] = cell_counts['count_dp'].apply(lambda x : x if x > 0 else 0)
    cell_counts['count_dp_rounded'] = round(cell_counts['count_dp'])
    #cell_counts[cell_counts['count_dp_rounded']<0]
    return cell_counts



def get_polygons(cell_counts):
    polygons = {}
    for i in range(0,cell_counts.count()[0]):
        polygons[wkt.dumps(cell_counts['geometry'][i])] = cell_counts['count_dp_rounded'][i]
    return polygons


def new_points(polygon,n):
    cursor, conn = db_conn()
    #polygon = "POLYGON ((-124.6588619852515620 41.4117418382433868, -124.6588619852515620 42.1733418382433882, -123.8972619852515606 42.1733418382433882, -123.8972619852515606 41.4117418382433868, -124.6588619852515620 41.4117418382433868))"
    cursor.execute("select st_asText(ST_GeneratePoints(ST_GeomFromText('"+polygon+"'),"+str(n)+"));")
    #cursor.execute("select st_asText(ST_GeneratePoints(ST_GeomFromText(POLYGON ((-123.8972619852515606 39.1269418382433827, -123.8972619852515606 39.8885418382433841, -123.1356619852515593 39.8885418382433841, -123.1356619852515593 39.1269418382433827, -123.8972619852515606 39.1269418382433827))),"+str(n)+"));")
    rows = cursor.fetchall()
    cursor.close()

    result = []
    for index in range(len(rows)):
        result.append([
            rows[index][0]
            
        ])
    points = result[0][0].replace('MULTIPOINT(','').replace(")","")
    point_list = points.split(",")
    x_y = []
    for i in point_list:
        x_y.append(i.split(" "))
        
    
    return x_y

def get_all_new_points(polygons):
    all_new_points = []
    #count = 0
    for pol in polygons:
        if polygons[pol].astype('int')!=0:
        
            p = new_points(pol,polygons[pol].astype('int'))
            all_new_points.append(p)

    df_new_points = generate_df_for_new_table(all_new_points).drop(columns=["before", "between", "after"])
    new_points_gpd = gpd.GeoDataFrame(df_new_points, geometry=gpd.points_from_xy(df_new_points['x'], df_new_points['y']))

            
    return new_points_gpd


def create_new_table():
    cursor, conn = db_conn()
    cursor.execute("CREATE TABLE test  ( new_id int4 primary key, new_geom geometry(POINT,4326) );")
    conn.commit()
    cursor.close()

def generate_df_for_new_table(points):
    point_dict = {'before':[],'x': [],'between':[], 'y': [], 'after':[]}
    for pol in points:
        for point in pol:
            point_dict['before'].append('SRID=4326;POINT(')
            point_dict['x'].append(point[0])
            point_dict['between'].append(' ')
            point_dict['y'].append(point[1])
            point_dict['after'].append(')')
            
    points_df = pd.DataFrame.from_dict(point_dict)
    return points_df  


def generate_csv_for_new_table(df):
    df = df.reset_index().rename(columns = {'index':'id'})
    df["geom"] = df[["before","x", "between","y", "after"]].apply("".join, axis=1)
    df = df.drop(columns=["before","x", "between","y", "after"])
    
    df.to_csv('points.csv',index = False)

def insert_csv_into_new_table():
    cursor, conn = db_conn()
    cursor.execute("delete from test;")
    cursor.execute("COPY test FROM '/home/ingastrelnikova28/points.csv' DELIMITERS ',' CSV HEADER;")
    conn.commit()
    cursor.close()



def bounding_box1():
    cursor, conn = db_conn()
    cursor.execute("select ST_AsText(ST_Envelope(ST_Collect(geom))) from  (select * from smalldata where  date = '2020-12-10') as foo;")
    rows = cursor.fetchall()
    result = []
    for index in range(len(rows)):
        result.append([
            rows[index][0]
        ])
    cursor.close()
    polygon_postgis = result[0]
    x_y = []
    x = []
    y = []
    polygon_postgis = polygon_postgis[0].replace('POLYGON((','').replace("))","")
    #print(polygon_original)
    points_list = polygon_postgis.split(",")
    #print(points_list)
    for i in points_list:
        x.append(i.split(" ")[0])
        y.append(i.split(" ")[1])
    lon_point_list = list(map(float, x))
    lat_point_list = list(map(float, y))
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]) 
    coord_lon = int(lon_point_list[-1])
    coord_lat = int(lat_point_list[-1])
    
    m = folium.Map([coord_lat, coord_lon], zoom_start=4, tiles='cartodbpositron')
    folium.GeoJson(polygon).add_to(m)
    folium.LatLngPopup().add_to(m)
    return m



def hexagon():
    cursor, conn = db_conn()
    cursor.execute("SELECT ST_AsText(ST_SetSRID(ST_Hexagon(1.0, 0, 0, st_makepoint(st_x(geom), st_y(geom))), 4326)) from smalldata;")
    rows = cursor.fetchall()
    result = []
    for index in range(len(rows)):
        result.append([
            rows[index][0]
        ])
    cursor.close()
    polygon_postgis = result[0]
    x_y = []
    x = []
    y = []
    polygon_postgis = polygon_postgis[0].replace('POLYGON((','').replace("))","")
    #print(polygon_original)
    points_list = polygon_postgis.split(",")
    #print(points_list)
    for i in points_list:
        x.append(i.split(" ")[0])
        y.append(i.split(" ")[1])
    lon_point_list = list(map(float, x))
    lat_point_list = list(map(float, y))
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    crs = {'init': 'epsg:4326'}
    polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom]) 
    coord_lon = int(lon_point_list[-1])
    coord_lat = int(lat_point_list[-1])
    
    m = folium.Map([coord_lat, coord_lon], zoom_start=4, tiles='cartodbpositron')
    folium.GeoJson(polygon).add_to(m)
    folium.LatLngPopup().add_to(m)
    return result, m
    
    #return result
    #print(result)
     

