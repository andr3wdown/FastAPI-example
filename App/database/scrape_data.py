#WARNING: This script is not intended to be run directly. It is a module that is imported by other scripts.
#Script runtime might take a while due to the delay between requests.
import os
import json
import re
import requests
from time import sleep
from datetime import date
from bs4 import BeautifulSoup
from tqdm import tqdm


initialized = False

wiki_url = 'https://hololive.wiki'
members_url = '/wiki/Members'
request_delay = 20 # seconds as instructed in the wiki robots.txt

# This function is used to initialize the script and check if the required directories exist.
def __initialize() -> None:
    # check if all required directiories exists, if not create them
    if not os.path.exists('site_cache'):
        os.makedirs('site_cache')
    if not os.path.exists('site_cache/generations'):
        os.makedirs('site_cache/generations')
    if not os.path.exists('site_cache/holos'):
        os.makedirs('site_cache/holos')
    
    #set the initialized variable to True
    global initialized
    initialized = True
    
    # main function to call to get the data
def get_data() -> tuple:
    if not initialized:
        __initialize()
        
    generations, holos, success, message = __scrape_site()
    print(message)
    
    if not success:
        return [], [], False
    
    return generations, holos, True

# checks if the site cache exists and if it is up to date if not it loads the site again and saves it to the cache
# returns the BeautifulSoup object of the site
def __load_cached_site(filepath, url) -> BeautifulSoup:
    # check if the site was cached today and if not load it again
    today = date.today().strftime("%Y-%m-%d")
    cached_today = False
    # check if the timestamp file exists
    if os.path.exists(filepath+'.timestamp'):
        # read the timestamp from the file
        with open(filepath+'.timestamp', 'r') as file:
            timestamp = json.loads(file.read())
            # check if the site was updated today
            if timestamp == today:
                print("---- Cache is up to date ----")
                cached_today = True
    
    # check if the file exists
    if not os.path.exists(filepath) or not cached_today:
        print("---- Loading site ----")
        # send a GET request to the wiki URL
        response = requests.get(url)
        # if the request was unsuccessful, return None
        if response.status_code != 200:
            return None
        # save the response content to a file
        with open(filepath, 'wb') as file:
            file.write(response.content)
        # save the timestamp of the last update to a file
        with open(filepath+'.timestamp', 'w') as file:
            file.write(json.dumps(today))
         
        # return the BeautifulSoup object 
        return BeautifulSoup(response.content, 'html.parser')
    
    print("---- Loading cached site ----")
    ## if the file exists, read the content and return the BeautifulSoup object
    with open(filepath, 'rb') as file:
        content = file.read()
    return BeautifulSoup(content, 'html.parser')
    
 # scrapes the site and returns a list of generations and a list of holos
def __scrape_site() -> tuple:
    soup = __load_cached_site('site_cache/site.cache', wiki_url + members_url)
    if soup is None:
        return [], [], False, "Error: could not load cached site or fetch new data"
    
    try:
        generations, holos, success = __parse_initial_data(soup)
        if not success:
            return [], [], False, "Error: Could not parse data"
        
        generations = __get_generation_data(generations)
        holos = __get_holo_data(holos)
        
    except Exception as e:
        print(f"Error parsing data: {e}")
        return [], [], False, "Error: Could not parse data"
    
    return generations, holos, True, "Success: Data scraped successfully"

# parses data from the members site and returns a list of generations and a list of holos
def __parse_initial_data(soup) -> tuple:
    generations = []
    holos = []
    
    tables = soup.find_all('table', class_='wikitable')
    for table in tables[0:2]:
        categories = table.find_all('th')
        categories = categories[1:]
        for i in range(len(categories)):
            categories[i] = categories[i].get_text(strip=True)
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')[1:]
            # skip header row
            if len(cells) == 0:
                continue
            
            generation = cells[2 if cells[2].find('a') else 4].get_text(strip=True)
            generation = re.sub(r'\(.*?\)', '', generation)
            
            # skip if member not from hololive
            if 'holostars' in generation or 'HOLOSTARS' in generation or 'Holostars' in generation:
                continue
            
            name = cells[0].get_text(strip=True)
            debut = cells[1].get_text(strip=True)
            
            if not any(gen['name'] == generation for gen in generations):
                gen = {
                    'name': generation,
                    'wiki_link': wiki_url + cells[2].find('a').get('href') if cells[2].find('a') else wiki_url + cells[4].find('a').get('href'),
                    'branch': __determine_branch(generation)
                }      
                generations.append(gen)
            
            #get the link to the wiki page of the member
            link = cells[0].find('a').get('href')
            if link:
                link = wiki_url + link
                
            holo = {
                'name': name,
                'debut': debut,
                'generation': generation,
                'wiki_link': link,
                'retired': False if len(cells) <= 4 else True
            }
            holos.append(holo)
            # in case of fuwamoco add mococo too
            if name == 'Fuwawa Abyssgard':
                mococo = {
                    'name': 'Mococo Abyssgard',
                    'debut': debut,
                    'generation': generation,
                    'wiki_link': wiki_url + '/wiki/Mococo_Abyssgard',
                    'retired': False
                }
                holos.append(mococo)   
            
    
    return generations, holos, True

def __get_generation_data(generations) -> list:
    print("---- Loading generation data ----")
    for i in tqdm(range(5), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
        sleep(20)
    return generations

def __get_holo_data(holos) -> list:
    print("---- Loading holo data ----")
    for i in tqdm(range(100), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
        sleep(20)
    return holos


#determines the branch of the generation based on the name
def __determine_branch(generation):
    if 'EN' in generation:
        return 'EN'
    elif 'ID' in generation:
        return 'ID'
    elif 'CN' in generation:
        return 'CN'
    elif 'DEV_IS' in generation:
        return 'DEV_IS'
    else:
        return 'JP'
    
if __name__ == "__main__":
    #used for testing and developement purposes
    get_data()