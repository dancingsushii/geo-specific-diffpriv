#from sqlite3 import connect
#from flask import g


import psycopg2
import math



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
    cursor.execute("SELECT COUNT(*) from smalldata;")
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
    print(n)
    m = math.sqrt((n*epsilon)/c)
    print(m)
    return m






n = get_data_points_count()
get_grid_size(n)
