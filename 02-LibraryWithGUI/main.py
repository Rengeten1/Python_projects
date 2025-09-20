# This code is a uses a GUI to make a interface to perform library management system operations, such as:
## Adding new books library
## Removing books
## Loading books from a json file
## Saving books to a json file
## Sorting books in a library by alphabet

from tkinter import *
from tkinter import messagebox
import json

# Initializing library
library = {}
# File path
file = "assignment2/library.json"

# Current book
def current_books():
    return len(library)

# List box function
def list_box_f():
    def quit_listbox():
        list_box_window.destroy()

    list_box_window = Toplevel(window)
    list_box_window.title('List Books')
    list_box_window.geometry('350x300')

    list_box = Listbox(list_box_window, width=50)
    list_box.pack(pady=10)

    for item, value in library.items():
        list_box.insert(END, f"{item} - {value['title']} {value['author']} ({value['year']})")

    Button(list_box_window, text='Close', command=quit_listbox).pack(pady=10)

# Add book function
def add_book():
    def save_book():
        title = entry_title.get()
        author = entry_author.get()
        year = entry_year.get()

        if title and author and year.isdigit():
            library['Book ' + str(current_books() + 1)] = {"title": title, "author": author, "year": year}
            messagebox.showinfo("Success", f"Book '{title}' added!")
            add_window.destroy()
        else:
            messagebox.showerror("Error", "All fields must be filled correctly!")
    
    add_window = Toplevel(window)
    add_window.title('Add a Book')
    add_window.geometry("250x175")
    
    Label(add_window, text='Title: ').pack()
    entry_title = Entry(add_window)
    entry_title.pack()
    
    Label(add_window, text='Author: ').pack()
    entry_author = Entry(add_window)
    entry_author.pack()
    
    Label(add_window, text='Year: ').pack()
    entry_year = Entry(add_window)
    entry_year.pack()
    
    Button(add_window, text='Save', command=save_book).pack()

# Sorting book function
def sort_books():
    global library

    # Sort books by title
    sorted_books = sorted(library.items(), key=lambda item: item[1]['title'].lower())

    sorted_library = {}

    # Iterate through sorted books and update the library
    for i, (key, value) in enumerate(sorted_books):
        new_key = f'Book {i + 1}'
        sorted_library[new_key] = value

    # Update the global library with sorted books
    library = sorted_library

    # Show message
    messagebox.showinfo("Sorted", "Books sorted alphabetically!")

    
# Delete book function
def delete_book():
    
    # Create a new window for deletion
    
    delete_window = Toplevel(window)
    delete_window.title("Delete a Book")
    delete_window.geometry("300x150")

    Label(delete_window, text="Enter Book Title:").pack()
    entry_title = Entry(delete_window)
    entry_title.pack()

    def confirm_delete():
        
        title = entry_title.get()
        
        # Search for the book and delete if found
        for key, value in library.items():
            if value["title"].lower() == title.lower():
                del library[key]
                messagebox.showinfo("Success", f"Book '{title}' deleted!")
                delete_window.destroy()
                return
        messagebox.showerror("Error", "Book not found!")

    Button(delete_window, text="Delete", command=confirm_delete).pack()


# Load books from json file
def load_book():
    global library
    try:
        with open(file, 'r', encoding="utf-8") as f:
            library = json.load(f)
        messagebox.showinfo("Success!", "Books Loaded successfully!")
    except FileNotFoundError:
        messagebox.showerror("Failed!", "File not found!")
    except json.JSONDecodeError:
        messagebox.showwarning("Warning","Invalid JSON format in file!")
    
# Saving book to library json file
def save_file():
    try:
        with open(file, 'w', encoding="utf-8") as f:
            json.dump(library, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Success!", "File saved successfully!")
    except FileNotFoundError:
        messagebox.showerror("Failed!", "File not found!")

# Search books function
def search_book():
    def perform_search():
        search_query = entry_search.get().lower()
        results.delete(0, END)

        for title, details in library.items():
            if (search_query in details["title"].lower()) or (search_query in details["author"].lower()):
                results.insert(END, f"{details['title']} - {details['author']} ({details['year']})")

    search_window = Toplevel(window)
    search_window.title("Search Books")
    search_window.geometry("400x250")

    Label(search_window, text="Search by Title or Author:").pack()
    entry_search = Entry(search_window)
    entry_search.pack()

    Button(search_window, text="Search", command=perform_search).pack()

    results = Listbox(search_window, width=50, height=10)
    results.pack()

# Quit program function
def quit_program():
    window.quit()

# Creating window
window = Tk()
window.title("Library Management System")
window.geometry('500x500')

# Adding label
lbl = Label(window, text = "Library System Manangement", font = ('Georgia', 18), bd=40)
lbl.place(relx=0.5, rely=.1, anchor= CENTER)

# Creating buttons

button_size = 12
button_color = 'black'

button_add = Button(window, text = 'Add New Book',font=('Georgia', button_size), fg= button_color, command=add_book)
button_add.place(relx=0.5, rely=.2, anchor= CENTER)
button_sort = Button(window, text = 'Sort Books',font=('Georgia', button_size), fg= button_color, command=sort_books)
button_sort.place(relx=0.5, rely=.3, anchor= CENTER)
button_delete = Button(window, text = 'Delete Book',font=('Georgia', button_size),fg= button_color, command=delete_book)
button_delete.place(relx=0.5, rely=.4, anchor= CENTER)
button_list = Button(window, text = 'List Books',font=('Georgia', button_size),fg= button_color, command=list_box_f)
button_list.place(relx=0.5, rely=.5, anchor= CENTER)
button_load = Button(window, text = 'Load File',font=('Georgia', button_size),fg= button_color, command=load_book)
button_load.place(relx=0.5, rely=.6, anchor= CENTER)
button_save = Button(window, text = 'Save File',font=('Georgia', button_size),fg= button_color, command=save_file)
button_save.place(relx=0.5, rely=.7, anchor= CENTER)
button_quit = Button(window, text = 'Quit',font=('Georgia', button_size),fg= 'red', command=quit_program)
button_quit.place(relx=0.5, rely=.8, anchor= CENTER)

# Execute Tkinter
window.mainloop()
