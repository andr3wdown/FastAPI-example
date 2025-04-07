from scrape_data import get_data
from datetime import date
import sqlite3
import os
import json
#connect to database
connection = sqlite3.connect('holobase.db')
cursor = connection.cursor()

#handle the database creation process
def run_creation():
    if __check_timestamp():
        print("---- Database is up to date ----")
    else:
        print("---- Creating database ----")
        __create_database()
        __close_connection()
        print("---- Database created ----")

#create database
def __create_database():
    generations, holos, success = get_data()
    if not success:
        print("Failed to retrieve data. Database creation aborted.")
        return

    __create_tables()
    __add_generations(generations)
    __add_holos(holos)

#insert branches and generations to database
def __add_generations(generations):
    sql = '''INSERT INTO GENERATION(Branch, Name, Overview, WikiLink)
             VALUES (?, ?, ?, ?)
             ON CONFLICT(Name) DO UPDATE SET
                 Branch = excluded.Branch,
                 Overview = excluded.Overview,
                 WikiLink = excluded.WikiLink'''
    values = []
    #loop through generations and get data
    for i in range(len(generations)):
        #get data from generation
        branch = generations[i]['branch']
        name = generations[i]['name']
        overview = generations[i]['overview']
        wiki_link = generations[i]['wiki_link']
        values.append((branch, name, overview, wiki_link))
        
    #execute sql commands on values
    cursor.executemany(sql, values)
    connection.commit()

#insert hololive members to database 
def __add_holos(holos):
    select_sql = '''SELECT GenerationID, Name FROM GENERATION'''
    cursor.execute(select_sql)
    gen_data = cursor.fetchall()
    gen_dict = {name: generation_id for generation_id, name in gen_data}  
    
    sql = '''INSERT INTO HOLO(GenerationID, EngName, JapName, DebutDate, Height, Birthday, Overview, ImageLink, YoutubeLink, TwitterLink, Retired, WikiLink)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON CONFLICT(EngName) DO UPDATE SET
                 GenerationID = excluded.GenerationID,
                 JapName = excluded.JapName,
                 DebutDate = excluded.DebutDate,
                 Height = excluded.Height,
                 Birthday = excluded.Birthday,
                 Overview = excluded.Overview,
                 ImageLink = excluded.ImageLink,
                 YoutubeLink = excluded.YoutubeLink,
                 TwitterLink = excluded.TwitterLink,
                 Retired = excluded.Retired,
                 WikiLink = excluded.WikiLink'''
    values = []
    #loop through holos and get data
    for i in range(len(holos)):
        #get data from holo
        gen_id = gen_dict.get(holos[i]['generation'])
        name = holos[i]['name']
        jap_name = holos[i]['jp_name']
        debut = holos[i]['debut']
        height = holos[i]['height']
        bday = holos[i]['birthday']
        overview = holos[i]['overview']
        img_link = holos[i]['img_link']
        yt_link = holos[i]['yt_link']
        twt_link = holos[i]['twt_link']
        retired = holos[i]['retired']
        wiki_link = holos[i]['wiki_link']
        values.append((gen_id, name, jap_name, debut, height, bday, overview, img_link, yt_link, twt_link, retired, wiki_link))
    
    #execute sql command on values
    cursor.executemany(sql, values)
    connection.commit()

#create tables with creation scripts
def __create_tables():
    query = __read_query_template('sql/create_generation.sql')  
    cursor.execute(query)
    
    query = __read_query_template('sql/create_holo.sql')
    cursor.execute(query)
    
    connection.commit()
      
#read query from file
def __read_query_template(file_path) -> str:
    with open(file_path, 'r') as file:
        query = file.read()
    return query

#close the database connection
def __close_connection():
    connection.close()
 
#check the timestamp, if it's not up to date return false
def __check_timestamp() -> bool:
    now = date.today().strftime("%Y-%m")
    if os.path.exists('holobase.timestamp'):
        with open('holobase.timestamp', 'r') as file:
            timestamp = json.loads(file.read())
            if now in timestamp:
                return True
    
    with open('holobase.timestamp', 'w') as file:
        file.write(json.dumps(date.today().strftime(r"%Y-%m-%d")))
        
    return False 