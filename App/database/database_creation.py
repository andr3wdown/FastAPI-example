import sqlite3
#connect to database
connection = sqlite3.connect('holobase.db')
cursor = connection.cursor()

#read query from file
def read_query_from_file(file_path):
    with open(file_path, 'r') as file:
        query = file.read()
    return query

#insert branches and generations to database
def add_groups(groups, table_name):
    sql_template = f'INSERT INTO {table_name}(EngName, JapName, DebutDate, Overview, ImageLink) VALUES(_en, _jn, _dd, _ov, _il)'
    for group in groups:
        sql_query = sql_template.replace('_en', group['EngName']).replace('_jn', group['JapName']).replace('_dd', group['DebutDate']).replace('_ov', group['Overview']).replace('_il', group['ImageLink'])
        cursor.execute(sql_query)
    connection.commit()

#insert hololive members to database 
def add_holos(holos):
    sql_template = f'INSERT INTO HOLO(EngName, JapName, BranchID, GenerationID, DebutDate, Height, Birthday, Overview, Personality, ImageLink, YoutubeLink, TwitterLink) VALUES(_en, _jn, _bid, _gid, _dd, _ht, _bd, _ov, _per, _il, _yl, _tl)'
    for holo in holos:
        sql_query = sql_template.replace('_en', holo['EngName']).replace('_jn', holo['JapName']).replace('_bid', holo['BranchID']).replace('_gid', holo['GenerationID']).replace('_dd', holo['DebutDate']).replace('_ht', holo['Height']).replace('_bd', holo['Birthday']).replace('_ov', holo['Overview']).replace('_per', holo['Personality']).replace('_il', holo['ImageLink']).replace('_yl', holo['YoutubeLink']).replace('_tl', holo['TwitterLink'])
        cursor.execute(sql_query)
    connection.commit()
    
#create database tables
def create_database():
    #create tables
    query = read_query_from_file('sql/create_branch.sql')
    cursor.execute(query)
    
    query = read_query_from_file('sql/create_generation.sql')
    cursor.execute(query)
    
    query = read_query_from_file('sql/create_holo.sql')
    cursor.execute(query)
    connection.commit()
    
def close_connection():
    connection.close()
 
