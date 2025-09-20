# Created by: Rownak Deb Kabya 
# Python program to scrape website, get headlines and then filtered headlines using user entered keywords
# We use BeautifulSoup to scrape the website and get the keywords
# requests to get the HTML content of the website
# json to save the data in a json file
# tabulate to display the data in a table format
# os to check if the file exists
# re to remove unwanted characters from the text
# time to check the cache expiry time

import json
import requests
from bs4 import BeautifulSoup
import tabulate as tb
import os
import re
import time

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
        print(f"Cache file '{filepath}' has expired and has been deleted.")
        return True
    return False


def clean_text(text):
    # Remove all characters except a-z, A-Z, 0-9, space, dot, comma, exclamation, question mark, hyphen
    text = re.sub(r'[^a-zA-Z0-9\s.!?-]', ' ', text)
    return text


# Making the HTTP get request to get the HTML content from the websites
def request_parse_strip():
    for source in URL:
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
            headlines[source["name"]] = [
                # first clean the text and then check if it is less than 100 characters otherwise skip
                clean_text(tag.get_text(strip=True)) for tag in tags if tag.get_text(strip=True) if len(clean_text(tag.get_text(strip=True))) < 100
            ]

        except requests.RequestException as e:
            print(f"An error occurred while fetching data from {source['name']}: {e}")

    return headlines

# Function to save the headlines to a JSON file
def save_headlines(headlines):
    with open(filename[0], 'w') as f:
        json.dump(headlines, f, indent=4)
        
def save_keyword_headlines(filtered):
    with open(filename[1], 'w') as f:
        json.dump(filtered, f, indent=4)

# Function to filter the headlines based on the keyword
def filter_headlines(headlines, keyword):
    global filtered
    filtered = []
    for src, headlines in headlines.items():
        for headline in headlines:
            if not isinstance(headline, str):
                continue
            if keyword.lower() in headline.lower():
                filtered.append({"headline": headline, "source": src})
    display_headlines(filtered)

# Function to display the filtered headlines
def display_headlines(filtered):
    """Display headlines in a console table."""
    if not filtered:
        print("No headlines found.")
        return
    # Create a table with index, headline, and source
    MAX_LENGTH = 100
    table = [
        [i + 1, (item["headline"][:MAX_LENGTH] + '...') if len(item["headline"]) > MAX_LENGTH else item["headline"], item["source"]]
        for i, item in enumerate(filtered)]
    # Use tabulate to format the table
    print(tb.tabulate(table, headers=["#", "Headline", "Source"], tablefmt="fancy_grid"))

# Function to load the headlines from the JSON file
def load_cache():
    try:
        with open(filename[0], 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in the file. Starting fresh.")
        return 

# Main function to run the generic news scraper
def main():
    print("Generic News Scraper")
    # Check if cache file exists and is valid
    if is_cache_expired(filename[0]):
        headlines = request_parse_strip()
        save_headlines(headlines)
    else:
        headlines = load_cache()
    try:
        keyword = input("Enter the keyword to search for: ").strip()
        filter_headlines(headlines, keyword)
        
        # Ask user to save filtered headlines or not
        response = input("Do you want to save the filtered headlines? (y/n): ").strip().lower()
        if response == 'y':
            save_keyword_headlines(filtered)
            print(f"Filtered headlines saved to {filename[1]}")
        else:
            print("Filtered headlines not saved.")
    except Exception as e:
        print(f"An error occurred: {e}")
    

        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")