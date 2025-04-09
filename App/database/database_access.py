import sqlite3
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
connection = sqlite3.connect(os.path.join(SCRIPT_DIR, 'holobase.db'))
cursor = connection.cursor()

column_names = { }

# get the hololive member data from the database using the name or ID
# if the name is an integer, it will be treated as a HoloID
def get_holo(name) -> tuple:
    __initialize_column_names()
    
    checked_category = 'EngName'
    if is_integer(name):
        name = int(name)
        checked_category = 'HoloID'
    else:
        name = __parse_name(name)
    
    try:
        sql = f'''SELECT * FROM HOLO WHERE {checked_category} LIKE ?'''
        holo, success = __get_single_result(sql, (name,), lambda result: __result_is_valid(result, len(column_names['holo']), 'holo'))
        if not success:
            print(f"Error: No holo found with name: {name}")
            return None, False
        
        sql = '''SELECT Name, Branch FROM GENERATION WHERE GenerationID = ?'''     
        generation, success = __get_single_result(sql, (holo[1],), lambda result: __result_is_valid(result, 2, 'generation'))
        if not success:
            print(f"Error: No generation found with ID: {holo[1]} for holo {name}")
            return None, False
        
        data = dict(zip(column_names['holo'], holo))
        data['Generation'] = generation[0]
        data['Branch'] = generation[1]

        return data, True
    
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, False

# get all holos from the database
def get_all_holos() -> tuple:
    __initialize_column_names()
    
    try:
        sql = '''SELECT HoloID, EngName FROM HOLO'''
        holos, success = __get_all_results(sql, (), lambda result: result and not result is None and len(result) > 0)
        if not success:
            print("Error: No holos found.")
            return None, False
        
        holos = [{"HoloID": holo[0], "EngName": holo[1]} for holo in holos]
        return holos, True
    
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, False

# get generation data from the database using the name or ID
# if the name is an integer, it will be treated as a GenerationID
def get_generation(name) -> tuple:
    __initialize_column_names()
    
    checked_category = 'Name'
    if is_integer(name):
        name = int(name)
        checked_category = 'GenerationID'
    else:
        name = re.sub(r'[_]', ' ', name)
        
    try:
        sql = f'''SELECT * FROM GENERATION WHERE {checked_category} LIKE ?'''
        generation, success = __get_single_result(sql, (name,), lambda result: __result_is_valid(result, len(column_names['generation']), 'generation'))
        if not success:
            print(f"Error: No generation found with name: {name}")
            return None, False
        
        sql = '''SELECT HoloID, EngName FROM HOLO WHERE GenerationID = ?'''
        holos, success = __get_all_results(sql, (generation[0],), lambda result: result and not result is None and len(result) > 0)
        if not success:
            print(f"Error: No holos found for GenerationID: {generation[0]}")
            return None, False
        
        data = dict(zip(column_names['generation'], generation))
        data['Members'] = [{"GenerationID": holo[0], "Name": holo[1]} for holo in holos]
        
        return data, True
    
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, False

# get all generations from the database
def get_all_generations() -> tuple:
    __initialize_column_names()
    
    try:
        sql = '''SELECT GenerationID, Name FROM GENERATION'''
        generations, success = __get_all_results(sql, (), lambda result: result and not result is None and len(result) > 0)
        if not success:
            print("Error: No generations found.")
            return None, False
        
        generations = [{"GenerationID": generation[0], "Name": generation[1]} for generation in generations]
        return generations, True
    
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, False
    
# get data from the first matching row in a database using the sql command and parameters
def __get_single_result(sql, params, check) -> tuple:
    #execute the sql command and get the result
    #check if the result is valid using the check function
    cursor.execute(sql, params)
    result = cursor.fetchone()
    success = check(result)
    if not success:
        return None, False
    return result, True

# get all data from the database matching the sql command and parameters
# check if the result is valid using the check function
def __get_all_results(sql, params, check) -> tuple:
    #execute the sql command and get the result
    cursor.execute(sql, params)
    result = cursor.fetchall()
    
    success = check(result)
    if not success:
        print("Error: No results found.")
        return None, False
    
    return result, True

#transform the name to match the format in the database
def __parse_name(name) -> str:
    names = re.split(r'[ -_]', name)
    for i in range(len(names)):
        names[i] = names[i].capitalize()
    name = ' '.join(names)
    name = __sanitize_input(name)

    name = f"%{name}%"
    return name

# Get the column names of the tables in the database and store them in a dictionary
def __initialize_column_names() -> None:
    if 'holo' not in column_names:
        column_names['holo'] = __get_column_names('HOLO')
    if 'generation' not in column_names:
        column_names['generation'] = __get_column_names('GENERATION')
        
# Get the column names of a table in the database using PRAGMA table_info
def __get_column_names(table_name) -> list:
    sql = f"PRAGMA table_info({table_name})"
    cursor.execute(sql)
    columns = [column[1] for column in cursor.fetchall()]
    return columns

# check if the result is valid
def __result_is_valid(result, expected_column_count, table) -> bool:
    if not result or result is None:
        print(f"Error: No {table} found.")
        return False
    if result[0] is None or result[0] == "":
        print(f"Error: No {table} found.")
        return False
    if len(result) == 0 or len(result) != expected_column_count:
        print(f"Error: Number of columns in the {table} result does not match the expected number of columns.")
        return False
    return True

# check if the string is an integer
def is_integer(string):
    #try to cast the string to an integer
    #if it fails, it's not an integer
    try:
        int(string)
        return True
    except ValueError:
        return False


# Remove any special characters or SQL injection attempts
# this isn't strictly necessary since I'm using parameterized queries and sqlite3 already escapes inputs, 
# but it's a good practice to sanitize inputs anyway to prevent any potential risks
def __sanitize_input(input_string) -> str:
    sanitized_string = ''.join(e for e in input_string if e.isalnum() or e.isspace())
    return sanitized_string