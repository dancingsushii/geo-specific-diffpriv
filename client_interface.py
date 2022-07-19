import dp
import psycopg2
import warnings


def client_request(query,eps):

    if ("select" not in query) or ("from" not in query) or (";" not in query):
        print("Please use a correct SQL query!")
        return

    table = query.partition("from")[2]
    
    #In case the user wants to filter the data for date or counte/state, create a new table with filtered data
    if "where" in query:
        query_list = query.partition("where")
        conditions = query_list[2]
        table = query_list[0].partition("from")[2]
        
        new_query = "CREATE TABLE filtered_data AS SELECT * from "+ table+" where "+conditions

        cursor, conn = dp.db_conn()
        cursor.execute("DROP TABLE filtered_data;")
        cursor.execute(new_query)
        conn.commit()
        cursor.close()

    #eps = 0.1

    #Apply differencial privacy
    
    initial_points,states_list = dp.get_initial_points(table)
    grid_cells = dp.create_grid(initial_points,len(initial_points),eps)
    cell_counts = dp.get_cell_counts(initial_points,grid_cells,eps)

    polygons = dp.get_polygons(cell_counts)
    new_points = dp.get_all_new_points(polygons)

    dp.create_new_table()
    points_df = dp.generate_df_for_new_table(new_points)
    dp.generate_csv_for_new_table(points_df)
    dp.insert_csv_into_new_table()

    #dp.plot_points(initial_points,grid_cells,states_list)
    #dp.plot_points(new_points,grid_cells,states_list)
    
    
    #Check what function
    if "st_envelope" in query.lower():
        bounding_box, polygon = dp.bounding_box()
        print(polygon)
    elif "st_centroid" in query.lower():
        point, center=dp.geom_center()
        print(center)

    

    


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    client_request("select ST_AsText(ST_Envelope(ST_Collect(geom))) from mediumdata where state = 'California' or state = 'Texas';",0.1)
    client_request("select ST_AsText(ST_Centroid(ST_Union(geom))) from mediumdata where state = 'California' or state = 'Texas';",0.1)