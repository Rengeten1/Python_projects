# Author: Rownak Deb Kabya
# This program scrapes news headlines from various sources, 
# filters them based on a keyword, and serves the results 
# via a FastAPI web application.

# Templates are located in the "templates" directory.
# home.html - to display the search form.
# result.html - to display the filtered results.

# use uvicorn main:app --reload to run the application

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from bs4 import BeautifulSoup
import requests

import json
import time
import re
import os 

# FastAPI Application instance
app = FastAPI()

# Jinja2 template directory
templates = Jinja2Templates(directory="templates")

# Global variables to store headlines and filtered results
headlines = {}
filtered = []
filename = ["cache_headlines.json", "keyword_headlines.json"]

# URLs of news sources to scrape
URL = [
    {"name": "FAZ", "url": "https://www.faz.net/aktuell/"},
    {"name": "SZ.de", "url": "https://www.sueddeutsche.de/"},
    {"name": "The New York Times", "url": "https://www.nytimes.com/"},
    {"name": "BBC", "url": "https://www.bbc.com/"}
]

# Cache expiry time in seconds
CACHE_EXPIRY = 3600  # Cache expiry time in seconds (1 hour)


# checks if the cache file is expired or not
def is_cache_expired(filepath):
    try:
        if not os.path.exists(filepath):
            return True
        if (time.time() - os.path.getmtime(filepath)) > CACHE_EXPIRY:
            os.remove(filepath)
            print(f"Cache file '{filepath}' has expired and has been deleted.")
            return True
        return False
    except Exception as e:
        print(f"Error checking cache expiry: {e}")
        return True
    
# cleans the headlines
def clean_text(text):
    # Remove all unnecessary characters
    text = re.sub(r"[^a-zA-Z0-9\s.,!?'-]", ' ', text)
    return text

# scrapes the news from the websites
def request_parse_strip():
    headers = {'User-Agent': 'Mozilla/5.0'}
    for source in URL:
        try:
            response = requests.get(source["url"], timeout=1, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html5lib')

            # Scraping headlines based on the website structure
            if source["name"] == "FAZ":
                tags = soup.find_all('h3')
            elif source["name"] == "SZ.de":
                tags = soup.find_all('h3')
            elif source["name"] == "BBC":
                tags = soup.find_all('h2')
            elif source["name"] == "The New York Times":
                tags = soup.find_all('div', attrs={'class': 'css-xdandi'})
            else:
                tags = []

            # Extracting and cleaning the text for each headline
            headlines[source["name"]] = [
                # first clean the text and then check if it is less than 100 characters otherwise skip
                clean_text(tag.get_text(strip=True)) for tag in tags if tag.get_text(strip=True) if len(clean_text(tag.get_text(strip=True))) < 100
            ]

        except requests.RequestException as e:
            print(f"An error occurred while fetching data from {source['name']}: {e}")
    return headlines

# filters the headlines based on the keyword
def filter_headlines(headlines, keyword):
    global filtered
    filtered = []
    for src, headlines in headlines.items():
        for headline in headlines:
            if not isinstance(headline, str):
                continue
            if keyword.lower() in headline.lower():
                filtered.append({"headline": headline, "source": src})
    return filtered


# home html page
@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("home.html", {
        "request": request, 
    })

# result html page
@app.post("/result", response_class=HTMLResponse)
def result(request:Request, keyword: str = Form("")):
    global headlines, filtered
    if is_cache_expired(filename[0]):
        headlines = request_parse_strip()
        with open(filename[0], 'w') as f:
            json.dump(headlines, f)
    else:
        with open(filename[0], 'r') as f:
            headlines = json.load(f)

    filtered = filter_headlines(headlines, keyword) if keyword else []

    return templates.TemplateResponse("result.html", {
        "request": request,
        "filtered": filtered,
        "keyword": keyword
    })
