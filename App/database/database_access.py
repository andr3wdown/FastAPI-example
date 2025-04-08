import sqlite3
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
connection = sqlite3.connect(os.path.join(SCRIPT_DIR, 'holobase.db'))
cursor = connection.cursor()

column_names = { }

def get_holo(name):
    if 'holo' not in column_names:
        column_names['holo'] = __get_column_names('HOLO')
    
    name = __parse_name(name)
    try:
        sql = '''SELECT * FROM HOLO WHERE EngName LIKE ?'''
        cursor.execute(sql, (name,))
        holo = cursor.fetchone()
        if not holo or holo is None:
            print("Error: No results found.")
            return None
        if holo[2] is None or holo[2] == "":
            print("Error: No results found.")
            return None
        if len(holo) == 0 or len(holo) != len(column_names['holo']):
            print("Error: Number of columns in the result does not match the expected number of columns.")
            return None
        
        return dict(zip(column_names['holo'], holo))
    
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None

#transform the name to match the format in the database
def __parse_name(name) -> str:
    name = __sanitize_input(name)
    names = re.split(r'[ -_]', name)
    for i in range(len(names)):
        names[i] = names[i].capitalize()
    name = ' '.join(names)
    name = f"%{name}%"
    return name

# Get the column names of a table in the database using PRAGMA table_info
def __get_column_names(table_name):
    
    sql = f"PRAGMA table_info({table_name})"
    cursor.execute(sql)
    columns = [column[1] for column in cursor.fetchall()]
    return columns

# Remove any special characters or SQL injection attempts
# this isn't strictly necessary since I'm using parameterized queries and sqlite3 already escapes inputs, 
# but it's a good practice to sanitize inputs anyway to prevent any potential risks
def __sanitize_input(input_string):
    sanitized_string = ''.join(e for e in input_string if e.isalnum() or e.isspace())
    return sanitized_string