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
def __load_cached_site(filepath, url) -> tuple:
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
                cached_today = True
    
    # check if the file exists
    if not os.path.exists(filepath) or not cached_today:
        # send a GET request to the wiki URL
        response = requests.get(url)
        # if the request was unsuccessful, return None
        if response.status_code != 200:
            return None, True, f'Error: Could not connect to site {url}'
        # save the response content to a file
        with open(filepath, 'wb') as file:
            file.write(response.content)
        # save the timestamp of the last update to a file
        with open(filepath+'.timestamp', 'w') as file:
            file.write(json.dumps(today))
         
        # return the BeautifulSoup object 
        return BeautifulSoup(response.content, 'html.parser'), True,'---- New site cached ----'
    
    ## if the file exists, read the content and return the BeautifulSoup object
    with open(filepath, 'rb') as file:
        content = file.read()
    return BeautifulSoup(content, 'html.parser'), False, '---- Cached site loaded ----'
    
 # scrapes the site and returns a list of generations and a list of holos
def __scrape_site() -> tuple:
    soup, requested, msg = __load_cached_site('site_cache/site.cache', wiki_url + members_url)
    if requested:
        sleep(request_delay)
    print(msg)
    if soup is None:

        return [], [], False, "Error: could not load cached site or fetch new data"
    
    try:
        generations, holos, success = __parse_initial_data(soup)
        if not success:
            return [], [], False, "Error: Could not parse data"
        
        generations, success = __get_generation_data(generations)
        if not success:
            return [], [], False, "Error: Could not load generation data"
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
            
            if name == 'Shirakami Fubuki':
                generation = 'hololive 1st Generation'
            
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
            
            # in case of fuwamoco add mococo too
            if name == 'Fuwawa Abyssgard':
                mococo = {
                    'name': 'Mococo Abyssgard',
                    'debut': debut,
                    'generation': generation,
                    'wiki_link': wiki_url + '/wiki/fuwamoco',
                    'retired': False,
                }
                holo['wiki_link'] = wiki_url + '/wiki/fuwamoco'
                holos.append(holo)
                holos.append(mococo)
                continue
                
            holos.append(holo)
            
            
            
    return generations, holos, True

def __get_generation_data(generations) -> tuple:
    print("---- Loading generation data ----")
    for i in tqdm(range(len(generations)), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
        soup, requested, msg = __load_cached_site(f'site_cache/generations/{generations[i]['name']}.cache', generations[i]['wiki_link'])
        if soup is None:
            print(msg)
            return generations, False
        overview = "\n" + soup.find('div', class_='mw-parser-output').find('p').get_text().rstrip()
        overview = re.sub(r'\[.*?\]', '', overview)
        generations[i]['overview'] = overview
        if requested:
            sleep(request_delay)
    return generations, True

def __get_holo_data(holos) -> list:
    print("---- Loading holo data ----")
    for i in tqdm(range(len(holos)), bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'):
        soup, requested, msg = __load_cached_site(f'site_cache/holos/{holos[i]['name']}.cache', holos[i]['wiki_link'])
        if soup is None:
            print(msg)
            return holos
        
        '''
            *JapName VARCHAR(64) NOT NULL,
            *Height VARCHAR(128) NOT NULL,
            *Birthday VARCHAR(128) NOT NULL,
            Overview TEXT NOT NULL,
            *ImageLink VARCHAR(128) NOT NULL,
            YoutubeLink VARCHAR(128) NOT NULL,
            TwitterLink VARCHAR(128) NOT NULL,
        '''
        
        if not 'Abyssgard' in holos[i]['name']:
            infobox = soup.find('table', class_='infobox')
            rows = infobox.find_all('tr')
        
            img_link = rows[1].find('a', class_= 'mw-file-description').get('href')
            img_link = wiki_url + img_link
            
            jp_name_row = infobox.find(lambda tag: tag.name == 'th' and 'Japanese Name' in tag.get_text())
            jp_name_parent = jp_name_row.parent if jp_name_row else None
            jp_name = jp_name_parent.find('td').get_text(strip=True) if jp_name_parent else ''
            if holos[i]['name'] in ['AZKi']:
                jp_name = holos[i]['name']
            if jp_name == '':
                print(f'\n{holos[i]['name']}: no Japanese name found')
            
            birthday_row = infobox.find(lambda tag: tag.name == 'a' and 'Birthday' in tag.get_text())
            birthday_parent = birthday_row.parent.parent if birthday_row else None
            birthday = birthday_parent.find('td').get_text(strip=True) if birthday_parent else ''
            birthday = re.sub(r'\[.*?\]', '', birthday)
            if birthday == '':
                print(f'\n{holos[i]['name']}: no birthday found')
            
            height_row = infobox.find(lambda tag: tag.name == 'a' and 'Height' in tag.get_text())
            height_parent = height_row.parent.parent if height_row else None
            height = height_parent.find('td').get_text(strip=True) if height_parent else ''
            height = re.sub(r'\[.*?\]', '', height)
            height = re.sub(r'\(.*?\)', '', height)
            if height == '':
                print(f'\n{holos[i]['name']}: no height found')
            
            yt_link = infobox.find(lambda tag: tag.name == 'a' and 'YouTube' in tag.get_text())
            yt_parent = yt_link.parent.parent if yt_link else None
            yt_link = yt_parent.find('a', class_='external').get('href') if yt_parent else ''
            if yt_link == '':
                print(f'\n{holos[i]['name']}: no link found')
        else:
            twin_name = holos[i]['name'].replace(' Abyssgard', '')
            
            
            

        
        
    
    
        if requested and i != len(holos) - 1:
            sleep(20)
    for holo in holos:
        print(holo['name'])        
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