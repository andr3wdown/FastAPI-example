# Hololive API | FastAPI example


## Table of contents:

- [1. Overview](#1-overview)
- [2. How to use](#2-how-to-use)
- [3. Screenshots](#3-screenshots)
- [4. Status](#4-status)
- [5. Credits](#5-credits)
- [6. License](#6-license)

## 1. Overview

This is a simple example of using the Hololive API with FastAPI with a sqlite3 database. The API provides information about Hololive members, including their names, debut dates, and other details.</p>

## 2. How to use

Highly recommended to make a virtual environment

Step 1: have/install python 3.13

Step 2: install requirements from requirements.txt

Step 3: set API_KEY environment variable to a key of your choice

Step 4: navigate to the App folder and run using the command: fastapi run main.py

Step 5: wait for the data to be scraped and added to the database
(NOTE: this can take quite long as the wiki we're scraping from has a 20s mandated delay in their robots.txt - avg runtime is ~35min the first time)

After step 5 your the API is now up and running!

## 3. Screenshots
![screenshot](https://i.ibb.co/4gmB3ndc/image.png)

## 4. Status

Project is complete
No further changes planned for now

## 5. Credits

- [Chong Lee](https://github.com/andr3wdown)

## 6. License
MIT license @ [Chong Lee](https://github.com/andr3wdown)
