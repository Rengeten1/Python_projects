# Making a Web scraper for scraping key words from generic news
To A
### Making the HTTP requests 
At first we install 
```
pip install requests
```

```
import requests
```
After 
### To parse the HTML we use: 
```
from bs4 import BeautifulSoup
```
### To save to a file we use JSON

```
import json
```
### Finding the headline
To find the headline we goto the browser and open the website then,
```
ctrl + shift + c
```
This opens the inspect window with select element. Click on the headline to find out it's location in the HTML content.
Then use the python function __find_all__ and through location we find all the headlines and then strip it to obtain a clear string with the headline.
Afterwards we use the __filtered__ list to filter out the headlines with the keyword provided by the user, through terminal input.