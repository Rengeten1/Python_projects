# Rownak Deb Kabya
# rownak.kabya@stud.th-deg.de
# News Scraping and Headline API Server

# This program provides a simple HTTP API server for scraping news headlines from various sources.
# It includes functionality to manage news sources, scrape headlines, cache results, and search through headlines.

# Features:
# RESTful API endpoints for managing news sources
# Web scraping of headlines from configurable news websites
# Caching mechanism with expiry for performance
# Search functionality across scraped headlines
# JSON-based configuration and data storage

# The server runs on localhost:8000 and provides endpoints for:
# Managing news sources (GET, POST)
# Scraping headlines from sources
# Searching cached headlines
# Retrieving cached data


import json
import requests
from bs4 import BeautifulSoup
import os
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Cache expiry time in 1 hour 
CACHE_EXPIRY = 3600

# File paths
SOURCES_FILE = "sources.json"
HEADLINES_FILE = "headlines.json"

def is_cache_expired(filepath):
    # Check if cache file is expired (from original exec_7.py)
    if not os.path.exists(filepath):
        return True
    if (time.time() - os.path.getmtime(filepath)) > CACHE_EXPIRY:
        # Delete the cache file if it is expired
        os.remove(filepath)
        print(f"Cache file '{filepath}' has expired and has been deleted.")
        return True
    return False

def clean_text(text):
    # Clean text function 
    text = re.sub(r'[^a-zA-Z0-9\s.!?-]', ' ', text)
    return text

def load_sources():
    # Load news sources from JSON file# 
    if not os.path.exists(SOURCES_FILE):
        # Creating default sources 
        default_sources = [
            {"id": 1, "name": "FAZ", "url": "https://www.faz.net/aktuell/", "selector": "h3", "enable": True},
            {"id": 2, "name": "SZ.de", "url": "https://www.sueddeutsche.de/", "selector": "h3", "enable": True},
            {"id": 3, "name": "The New York Times", "url": "https://www.nytimes.com/", "selector": "div.css-xdandi", "enable": True},
            {"id": 4, "name": "BBC", "url": "https://www.bbc.com/", "selector": "h2", "enable": True}
        ]
        save_sources(default_sources)
        return default_sources
    
    try:
        with open(SOURCES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_sources(sources):
    # Save sources to JSON file
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=4)

def load_headlines():
    # Load headlines from cache file
    try:
        with open(HEADLINES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_headlines(headlines):
    # Save headlines to cache file# 
    with open(HEADLINES_FILE, 'w') as f:
        json.dump(headlines, f, indent=4)

def scrape_single_source(source):
    # Scrape headlines from a single source 
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(source["url"], timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html5lib')

        # Use the selector from source configuration
        if source["name"] == "FAZ":
            tags = soup.find_all('h3')
        elif source["name"] == "SZ.de":
            tags = soup.find_all('h3')
        elif source["name"] == "BBC":
            tags = soup.find_all('h2')
        elif source["name"] == "The New York Times":
            tags = soup.find_all('div', attrs={'class': 'css-xdandi'})
        else:
            tags = soup.select(source["selector"])

        # Extract and clean headlines
        headlines = []
        for tag in tags:
            text = tag.get_text(strip=True)
            if text:
                cleaned = clean_text(text)
                if len(cleaned) < 100:  
                    headlines.append({
                        "text": cleaned,
                        "source": source["name"],
                        "scraped_at": time.time()
                    })

        return headlines

    except requests.RequestException as e:
        print(f"Error scraping {source['name']}: {e}")
        return []

def scrape_all_sources():
    # Scrape all enabled sources 
    sources = load_sources()
    all_headlines = []
    
    for source in sources:
        if source.get("enable", True):
            headlines = scrape_single_source(source)
            all_headlines.extend(headlines)
    
    return all_headlines

def search_headlines(headlines, keyword):
    # Search headlines by keyword 
    filtered = []
    for headline in headlines:
        if isinstance(headline, dict) and "text" in headline:
            if keyword.lower() in headline["text"].lower():
                filtered.append(headline)
    return filtered

def get_source_by_id(source_id):
    # Get a source by its ID
    sources = load_sources()
    for source in sources:
        if source.get("id") == source_id:
            return source
    return None

# Simple HTTP request handler
class SimpleAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Handle GET requests# 
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Route requests to different handlers
        if path == "/sources":
            self.handle_get_sources()
        elif path.startswith("/sources/"):
            # Extract source ID from path
            source_id = int(path.split("/")[-1])
            self.handle_get_source(source_id)
        elif path == "/scrape/all":
            self.handle_scrape_all()
        elif path.startswith("/scrape/"):
            # Extract source ID from path
            source_id = int(path.split("/")[-1])
            self.handle_scrape_source(source_id)
        elif path == "/headlines":
            self.handle_get_headlines()
        elif path == "/search":
            # Get keyword from query parameters
            keyword = query_params.get('keyword', [''])[0]
            self.handle_search(keyword)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        # Handle POST requests 
        if self.path == "/sources":
            self.handle_add_source()
        else:
            self.send_error(404, "Not Found")
    
    def handle_get_sources(self):
        # GET /sources - List all sources
        sources = load_sources()
        self.send_json(sources)
    
    def handle_get_source(self, source_id):
        # GET /sources/{id} - Get single source
        source = get_source_by_id(source_id)
        if source:
            self.send_json(source)
        else:
            self.send_error(404, "Source not found")
    
    def handle_add_source(self):
        # POST /sources - Add new source 
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            new_source = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            if 'url' not in new_source or 'selector' not in new_source:
                self.send_error(400, "Missing required fields: url, selector")
                return
            
            # Load existing sources and add new one
            sources = load_sources()
            # Generate new ID
            max_id = max([s.get('id', 0) for s in sources], default=0)
            new_source['id'] = max_id + 1
            new_source.setdefault('enable', True)
            
            sources.append(new_source)
            save_sources(sources)
            
            self.send_json(new_source, status_code=201)
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def handle_scrape_all(self):
        # GET /scrape/all - Scrape all enabled sources# 
        headlines = scrape_all_sources()
        save_headlines({"headlines": headlines, "last_updated": time.time()})
        
        response = {
            "message": f"Scraped {len(headlines)} headlines",
            "count": len(headlines)
        }
        self.send_json(response)
    
    def handle_scrape_source(self, source_id):
        # GET /scrape/{id} - Scrape single source
        source = get_source_by_id(source_id)
        if not source:
            self.send_error(404, "Source not found")
            return
        
        headlines = scrape_single_source(source)
        
        response = {
            "message": f"Scraped {len(headlines)} headlines from {source['name']}",
            "source": source,
            "headlines": headlines
        }
        self.send_json(response)
    
    def handle_get_headlines(self):
        # GET /headlines - Get cached headlines
        cached_data = load_headlines()
        headlines = cached_data.get("headlines", [])
        self.send_json(headlines)
    
    def handle_search(self, keyword):
        # GET /search?keyword=... - Search headlines
        cached_data = load_headlines()
        headlines = cached_data.get("headlines", [])
        
        if keyword:
            filtered = search_headlines(headlines, keyword)
        else:
            filtered = headlines
        
        response = {
            "keyword": keyword,
            "total": len(headlines),
            "found": len(filtered),
            "results": filtered
        }
        self.send_json(response)
    
    def send_json(self, data, status_code=200):
        # Send JSON response
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_str = json.dumps(data, indent=2)
        self.wfile.write(json_str.encode('utf-8'))

def run_server():
    # Start the server
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    
    print("News API Server started on http://localhost:8000")
    print("Available endpoints:")
    print("  GET  /sources          - List all news sources")
    print("  GET  /sources/{id}     - Get specific source")
    print("  POST /sources          - Add new source")
    print("  GET  /scrape/all       - Scrape all enabled sources")
    print("  GET  /scrape/{id}      - Scrape specific source")
    print("  GET  /headlines        - Get cached headlines")
    print("  GET  /search?keyword=X - Search headlines")
    print("\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()