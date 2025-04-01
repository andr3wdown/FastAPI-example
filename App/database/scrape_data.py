from bs4 import BeautifulSoup
import requests
import re
import json

wiki_url = 'https://hololive.wiki/wiki/Main_Page'

def scrape_site(url):
    response = requests.get(wiki_url)
    if response.status_code != 200:
        return [], [], [], False, "Error: Could not connect to site or couldn't find the path"
    
    soup = BeautifulSoup(response.content, 'html.parser')
    branches = []
    generations = []
    holos = []
    
    print(soup.prettify())
    
    
if __name__ == "__main__":
    scrape_site(wiki_url)