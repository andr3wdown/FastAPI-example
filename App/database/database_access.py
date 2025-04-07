import sqlite3

connection = sqlite3.connect('holobase.db')
cursor = connection.cursor()

column_names = { }

def get_holo(name):
    if 'holo' not in column_names:
        column_names['holo'] = __get_column_names('HOLO')
    
    name = __sanitize_input(name)
    name = name.capitalize()
    name = f"%{name}%"
    
    sql = '''SELECT * FROM HOLO WHERE EngName LIKE ?'''
    cursor.execute(sql, (name,))
    holo = cursor.fetchone()
    return holo

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