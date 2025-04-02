from scrape_data import get_data
import sqlite3
#connect to database
connection = sqlite3.connect('holobase.db')
cursor = connection.cursor()



#insert branches and generations to database
def add_generations(generations, sql):
    
    
    return sql

#insert hololive members to database 
def add_holos(holos, sql):
    
    return sql
    
#create database tables
def create_database():
    generations, holos, success = get_data()
    
    #create tables   
    query = reqd_query_template('sql/create_generation.sql')
    
    cursor.execute(query)
    
    query = reqd_query_template('sql/create_holo.sql')
    
    cursor.execute(query)
    connection.commit()
    
#read query from file
def reqd_query_template(file_path) -> str:
    with open(file_path, 'r') as file:
        query = file.read()
    return query
    
def close_connection():
    connection.close()
 


if __name__ == "__main__":
    create_database()
    close_connection()
    
    