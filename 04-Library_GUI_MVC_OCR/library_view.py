# Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de
# This code is responsible for the GUI of the Library Management System.
from tkinter import messagebox, filedialog, simpledialog, ttk
from tkinter import *

# Function to create the main window and its components
def create_main_window_view(book_count_value, save_cmd, load_cmd, generate_cmd, about_cmd, add_cmd, delete_cmd, lend_cmd, upload_cmd):
    
    # Create the main window
    window = Tk()
    window.title("Library Management System V: 2.0")
    window.geometry('400x350')

    # Label 
    main_label = Label(window, text='Main Menu', font=('Georgia', 15), fg='black')
    main_label.place(relx=0.5, rely=0.1, anchor=CENTER)

    # Display Book Number
    display_book = Label(window, text=f'Current Book Count: {book_count_value}', font=('georgia',12), fg='black')
    display_book.place(relx=0.5, rely=.85, anchor=CENTER)

    # Menu
    menu = Menu(window)
    window.config(menu=menu)
    file_menu = Menu(menu)

    # File
    menu.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Save File', command=save_cmd)
    file_menu.add_command(label='Load File', command=load_cmd)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=window.quit)

    # Generate books 1 million
    generate_menu = Menu(menu)
    menu.add_cascade(label='Generate', menu=generate_menu)
    generate_menu.add_command(label='Generate books', command=generate_cmd)

    # Help
    help_menu = Menu(menu)
    menu.add_cascade(label='Help', menu=help_menu)
    help_menu.add_command(label='About', command=about_cmd)

    # Buttons for the main window
    color = 'black'
    button_size = 13

    button_add = Button(window, text='Add New Book', font=('Georgia', button_size), fg=color, command=add_cmd)
    button_add.place(relx=0.5, rely=.2, anchor=CENTER)
    button_delete = Button(window, text='Delete Book', font=('Georgia', button_size), fg=color, command=delete_cmd)
    button_delete.place(relx=0.5, rely=.375, anchor=CENTER)
    button_lend = Button(window, text='Lend/Receive Book', font=('Georgia', button_size), fg=color, command=lend_cmd)
    button_lend.place(relx=0.5, rely=.55, anchor=CENTER)
    button_upload = Button(window, text='Upload Image', font=('Georgia', button_size), fg=color, command=upload_cmd)
    button_upload.place(relx=0.5, rely=.725, anchor=CENTER)

    return window, display_book

# Function for Menu
def about_page_view():
    about_window = Toplevel()
    about_window.title('About')
    about_window.geometry('300x300')
    
    Label(about_window, text='Library Management System', font=('Georgia', 15), fg='black').place(relx=0.5, rely=0.1, anchor=CENTER)
    Label(about_window, text='Version: 2.0', font=('Georgia', 12), fg='black').place(relx=0.5, rely=0.3, anchor=CENTER)
    Label(about_window, text='Created by:', font=('Georgia', 12), fg='black').place(relx=0.5, rely=0.5, anchor=CENTER)
    Label(about_window, text='Rownak Deb Kabya & Marcos Blanco-Leon', font=('Georgia', 10), fg='black').place(relx=0.5, rely=0.7, anchor=CENTER)
    Label(about_window, text='THD', font=('Georgia', 10), fg='black').place(relx=0.5, rely=0.9, anchor=CENTER)

# Function for adding books to library
def add_book_view(save_cmd, default_title=''):
    window_add = Toplevel()
    window_add.geometry('300x300')
    window_add.title('Add New Book')
    
    Label(window_add, text='Title: ').place(relx=0.5, rely=.075, anchor=CENTER)
    enter_title = Entry(window_add)
    enter_title.insert(0, default_title)
    enter_title.place(relx=0.5, rely=.15, anchor=CENTER)
    
    Label(window_add, text='Author: ').place(relx=0.5, rely=.275, anchor=CENTER)
    enter_author = Entry(window_add)
    enter_author.place(relx=0.5, rely=.35, anchor=CENTER)
    
    Label(window_add, text='Year: ').place(relx=0.5, rely=.475, anchor=CENTER)
    enter_year = Entry(window_add)
    enter_year.place(relx=0.5, rely=.55, anchor=CENTER)

    Label(window_add, text='Status: Missing, Available or Lent Out ').place(relx=0.5, rely=.675, anchor=CENTER)
    enter_status = Entry(window_add)
    enter_status.place(relx=0.5, rely=.75, anchor=CENTER)
    
    button_save = Button(window_add, text='Save', font=('Georgia', 12), command=lambda: save_cmd(enter_title, 
                                                                                              enter_author.get(), 
                                                                                              enter_year.get(), 
                                                                                              enter_status.get(), 
                                                                                              window_add))
    button_save.place(relx=0.5, rely=0.9, anchor=CENTER)

# Function to delete a book
def delete_book_view(confirm_cmd):
    delete_window = Toplevel()
    delete_window.title('Delete')
    delete_window.geometry('300x300')

    Label(delete_window, text='Enter Book Title: ').place(relx=0.5, rely=0.4, anchor=CENTER)
    enter_title = Entry(delete_window)
    enter_title.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    Button(delete_window, text='Confirm', font=('Georgia', 13), fg='red', command=lambda: confirm_cmd(enter_title.get())).place(relx=0.5, rely=0.7, anchor=CENTER)

# Progress window for the generation process
def generate_books_view(cancel_cmd):
    progress_window = Toplevel()
    progress_window.title('Generation Progress')
    progress_window.geometry('300x300')

    # Progress window label
    label_gen = Label(progress_window, text='Generation In Progress...', font=('georgia', 15))
    label_gen.place(relx=0.5, rely=.4, anchor=CENTER)
    progress_bar = ttk.Progressbar(progress_window, orient=HORIZONTAL, length=200, mode='determinate')
    progress_bar.place(relx=0.5, rely=.5, anchor=CENTER)
    progress_bar['value'] = 0
    
    Button(progress_window, text='Cancel Generation', fg='red', command=cancel_cmd).place(relx=0.5, rely=.6, anchor=CENTER)
    
    return progress_window, label_gen, progress_bar

# Function to view the library list
def lend_receive_view(search_cmd, exit_cmd, double_click_cmd):
    # Create the list window for displaying books
    list_window = Toplevel()
    list_window.title('Library List')
    list_window.geometry('600x500')

    # Adding Menu for search
    menu = Menu(list_window)
    list_window.config(menu=menu)
    search_menu = Menu(menu)

    # Search book
    menu.add_cascade(label='Options', menu=search_menu)
    search_menu.add_command(label='Search Books', command=search_cmd)
    search_menu.add_separator()
    search_menu.add_command(label='Exit', command=exit_cmd)

    # Frame to hold  listbox and scrollbar 
    list_frame = Frame(list_window)
    list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Scrollbar
    list_box_scroll = Scrollbar(list_frame, orient=VERTICAL)
    list_box_scroll.pack(side=RIGHT, fill=Y)

    # Listbox
    list_box = Listbox(list_frame, width=50, height=20, font=('Georgia', 10), selectmode=SINGLE, yscrollcommand=list_box_scroll.set)
    list_box.pack(side=LEFT, fill=BOTH, expand=True)

    # Connect the scrollbar with the listbox
    list_box_scroll.config(command=list_box.yview)

    try:
        list_box.bind("<Double-Button-1>", double_click_cmd)
    except TclError:
        messagebox.showerror('Error', 'Please click a valid book!')
    except Exception as e:
        messagebox.showerror('Error', f'Operation failed due to: {e}')

    return list_window, list_box

# Function to search books
def search_books_view(search_cmd):
    window_search = Toplevel()
    window_search.geometry('300x300')
    window_search.title('Search Books')
    
    Label(window_search, text='Fill one or more entries to start Search.', font=('georgia', 10)).place(relx=0.5, rely=.15, anchor=CENTER)    

    Label(window_search, text='Title: ').place(relx=0.5, rely=.275, anchor=CENTER)
    enter_title = Entry(window_search)
    enter_title.place(relx=0.5, rely=.35, anchor=CENTER)
    
    Label(window_search, text='Author: ').place(relx=0.5, rely=.425, anchor=CENTER)
    enter_author = Entry(window_search)
    enter_author.place(relx=0.5, rely=.5, anchor=CENTER)
    
    Label(window_search, text='Year: ').place(relx=0.5, rely=.575, anchor=CENTER)
    enter_year = Entry(window_search)
    enter_year.place(relx=0.5, rely=.65, anchor=CENTER)
    
    Label(window_search, text='Status: Missing, Available, Lent Out or deleted').place(relx=0.5, rely=.725, anchor=CENTER)
    enter_status = Entry(window_search)
    enter_status.place(relx=0.5, rely=.8, anchor=CENTER)
    
    button_search = Button(window_search, text='Search', font=('Georgia', 12), command=lambda: search_cmd(enter_title.get(), 
                                                                                                      enter_author.get(), 
                                                                                                      enter_year.get(), 
                                                                                                      enter_status.get()))
    button_search.place(relx=0.5, rely=0.9, anchor=CENTER)

# Function to display search results from recognized text
def display_search_results(filtered_books, search_title):
    result_window = Toplevel()
    result_window.title(f'Search Results for "{search_title}"')
    result_window.geometry('600x500')

    # Frame to hold listbox and scrollbar
    list_frame = Frame(result_window)
    list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Scrollbar
    list_box_scroll = Scrollbar(list_frame, orient=VERTICAL)
    list_box_scroll.pack(side=RIGHT, fill=Y)

    # Listbox
    list_box = Listbox(list_frame, width=50, height=20, font=('Georgia', 10), selectmode=SINGLE, yscrollcommand=list_box_scroll.set)
    list_box.pack(side=LEFT, fill=BOTH, expand=True)

    # Connect the scrollbar with the listbox
    list_box_scroll.config(command=list_box.yview)

    # Update listbox with results
    update_list_view(list_box, filtered_books)

    # Show message if no results
    if not filtered_books:
        messagebox.showinfo('Unsuccessful', 'No Books Found.')

# Function to update the list box with current library books
def update_list_view(list_box, books):
    list_box.delete(0, END)
    keys = list(books.keys())
    index = 0
    batch_size = 1000
    def insert_batch():
        nonlocal index
        for _ in range(batch_size):
            if index >= len(keys):
                return
            key = keys[index]
            val = books[key]
            list_box.insert(END, f"{key} - Title: {val['title']} Author: {val['author']} Year: {val['year']} Status: {val['status']}")
            index += 1
        list_box.after(10, insert_batch)
    insert_batch()
