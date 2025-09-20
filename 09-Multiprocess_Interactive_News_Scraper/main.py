# Created by: Rownak Deb Kabya 
# This program scrapes headlines from multiple news websites in parallel using multiprocessing.
# It cleans and normalizes the headlines, removes unwanted characters and news source names,
# and caches the results to a JSON file with automatic cache expiry and deletion.
# Users can filter headlines by keyword, export filtered results, and interact with the data
# through a UI provided by view.py.

from multiprocessing import Pool
from bs4 import BeautifulSoup
import unicodedata
import requests
import json
import time
import view
import os
import re


# Dictionary to store all the headlines with the news as the key
headlines = {}

# To store all the filtered headlines
filtered = []

# File paths
filename = ["cache_headlines.json", "keyword_headlines.json"]

# URL of all the News channels that the data will be scrapped from
URL = [
    {"name": "FAZ", "url": "https://www.faz.net/aktuell/"},
    {"name": "SZ.de", "url": "https://www.sueddeutsche.de/"},
    {"name": "The New York Times", "url": "https://www.nytimes.com/"},
    {"name": "BBC", "url": "https://www.bbc.com/"}
]

# Cache expiry time in 1 hour
CACHE_EXPIRY = 3600

def is_cache_expired(filepath):
    if not os.path.exists(filepath):
        return True
    if (time.time() - os.path.getmtime(filepath)) > CACHE_EXPIRY:
        # Delete the cache file if it is expired
        os.remove(filepath)

        return True
    return False


def clean_text(text):
    text = unicodedata.normalize("NFC", text)
    # Removes all characters that are unnecessary
    text = re.sub(r'[^a-zA-Z0-9ÄÖÜßäöüẞ\s.,!?-]', ' ', text)

    # Removes News Source Name at start
    NEWS_SOURCES = ["FAZ", "SZ", "BBC"]
    for source in NEWS_SOURCES:
        pattern = rf"^{re.escape(source)}[\s:\-–—]*"
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Removes extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_and_parse_single_source(source):
    source_headlines = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Making the HTTP get request to get the HTML content from the websites
        response = requests.get(source["url"], timeout=10, headers=headers)
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
        for tag in tags:
            text = tag.get_text(strip=True)
            cleaned = clean_text(text)
            # Filters out headlines that are too short or too long
            if 20 < len(cleaned) < 100:
                source_headlines.append(cleaned)

    except requests.RequestException as e:
        print(f"An error occurred while fetching data from {source['name']}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {source['name']}: {e}")

    return {source["name"]: source_headlines}


def request_parse_strip_multiprocess():
    all_headlines = {}
    with Pool() as pool:
        # Apply the fetching function to each URL asynchronously
        results = pool.map(fetch_and_parse_single_source, URL)

    # Collect results
    for item in results:
        all_headlines.update(item)

    return all_headlines


def save_cache(headlines_data):
    try:
        with open(filename[0], 'w', encoding='utf-8') as f:
            json.dump(headlines_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        view.exception_view(f"Error saving cache: {e}")


def export(headlines_data, export_filename, exception_view_func):
    try:
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(headlines_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        exception_view_func(e)


def filter_headlines(headlines_data, keyword):
    filtered_results = []
    # Regex pattern to match the keyword as a whole word
    pattern = rf'\b{re.escape(keyword)}\b'

    for source_name, headline_list in headlines_data.items():
        for headline in headline_list:
            if not isinstance(headline, str):
                continue
            if re.search(pattern, headline, re.IGNORECASE):
                filtered_results.append({
                    "headline": headline,
                    "source": source_name
                })
    return filtered_results


def load_cache():
    try:
        with open(filename[0], 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        view.exception_view("Invalid JSON in the cache file. It might be corrupted.")
        return {}
    except FileNotFoundError:
        view.exception_view("Cache file not found. It will be created on the next update.")
        return {}
    except Exception as e:
        view.exception_view(f"An error occurred while loading cache: {e}")
        return {}

def update_and_get_headlines():
    global headlines
    start_time = time.time()
    updated_headlines = request_parse_strip_multiprocess()
    save_cache(updated_headlines)
    end_time = time.time()
    print(f"Time taken to scrape and save updated headlines: {end_time - start_time:.2f} seconds")
    headlines = updated_headlines # Update the global headlines after scraping
    return updated_headlines


def main():
    global headlines

    # Check if cache file exists and is valid
    if is_cache_expired(filename[0]):
        headlines = request_parse_strip_multiprocess()
        save_cache(headlines)
    else:
        headlines = load_cache()

    # initializes the GUI
    try:
        # Pass the update function to the view
        view.window(headlines, filter_headlines, export, update_and_get_headlines)

    except Exception as e:
        view.exception_view(e)


if __name__ == "__main__":
    main()