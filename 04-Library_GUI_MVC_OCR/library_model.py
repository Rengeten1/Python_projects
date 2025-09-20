# Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de
# This code is the model for the Library Management System.

from random import randint, choice
import pyocr.builders
import pyocr
import json

library = {}

# Lists for generating 
adj = ["Dusk", "Dawn", "Ancient", "Lost", "Sacred", "Salvation"]
noun = ["Empiress", "Roy", "Paris", "Frankfurt", "Munich", "Deggendorf", "Berlin", "Garry", "Berry"]
themes = ["Sun", "Moon", "Destiny", "Mars", "Neptune", "Winter", "Summer", "Time", "Abyss", "Hole", "End", "Start", "Middle", "Ground", "Sea", "Ocean"]

# Author Names
name = ["Rey", "Key", "Garry", "Frow", "Grpw", "Arrow", "Aron", "Baron", "Ron", "Roney"]
surname = ["jerrey", "Kein", "Garry", "Frow", "Grpw", "Arrow", "Aron", "Baron", "Ron", "Roney"]

# Book Status
status_base = ["available", "lent out", "missing"]

status_count = []

# Returns the library count
def book_count():
    return len(library)

# Function to upload image
def upload_image_model(recognized_text):
    try:
        if recognized_text:
            return True, f"Recognized Text: {recognized_text}"
        return False, 'No text recognized.'
    except Exception as e:
        return False, f"Failed to process image. {str(e)}"

# Function for loading books from a JSON file
def load_file_model(file_path):
    try:
        if file_path:
            with open(file_path, 'r') as file:
                library_load = json.load(file)
            library.update(library_load)
            return True, 'Library loaded successfully!'
        return False, 'No file selected.'
    except json.JSONDecodeError:
        return False, "Failed to load library. Invalid JSON format."
    except FileNotFoundError:
        return False, "File not found. Please select a valid file."

# Function for saving library as a JSON file
def save_file_model(file_path):
    try:
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(library, file, indent=4)
            return True, 'Library saved successfully!'
        return False, 'No file selected.'
    except Exception as e:
        return False, f"Failed to save library. {str(e)}"

# Function for adding books to library
def add_book_model(title, author, year, status):
    book_attribute_value = [title, author, year, status]
    if title and author and year.isdigit():
        if status not in status_base:
            return False, "Status is not valid!"
        else:
            book_attribute = ['title', 'author', 'year', 'status']
            library[str(len(library) + 1)] = {book_attribute[i]: book_attribute_value[i] for i in range(len(book_attribute))}
            return True, "Book " + title + " Added!"
    else:
        return False, "All Boxes need to be filled correctly!"

# Function to Generate books using string random functions
def generate_books_model():
    pre_lib = library.copy()
    target = 1_000_000
    index = 0
    not_cancelled = True

    def generate_batch():
        nonlocal index, not_cancelled
        for _ in range(1000):
            if index >= target or not_cancelled == False:
                break
            title = adj[randint(0, len(adj)-1)] + " in " + noun[randint(0, len(noun)-1)] + " of the " + themes[randint(0, len(themes)-1)]
            author = name[randint(0, len(name)-1)] + " " + surname[randint(0, len(surname)-1)]
            year = str(randint(1900, 2023))
            status = status_base[randint(0, 2)]
            library['book ' + str(len(library) + 1)] = {'title': title, 'author': author, 'year': year, 'status': status}
            index += 1
        return index, not_cancelled, (index / target) * 100

    def cancel_generation():
        nonlocal not_cancelled, pre_lib
        not_cancelled = False
        library.clear()
        library.update(pre_lib)
        return not_cancelled

    return generate_batch, cancel_generation

# Functions for the buttons
def delete_book_model(title):
    for key, val in list(library.items()):
        if val['title'].lower() == title.lower():
            library[key] = {'status': 'deleted'}
            return True, f'Book {title} deleted!'
    return False, "Book with Title not found!"

# Function to change the status of a book
def change_status_model(book_number, new_status):
    if new_status in status_base:
        library[book_number]['status'] = new_status.lower()
        return True, "Status changed successfully!"
    return False, 'Invalid Input As Status!'

# Searching books
def search_books_model(title, author, year, status):
    filtered = {}
    for key, val in library.items():
        if (title in val['title'].lower() if title else True) and \
           (author in val['author'].lower() if author else True) and \
           (year in val['year'] if year else True) and \
           (status in val['status'].lower() if status else True):
            filtered[key] = val
    return filtered