# Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de
# This is a library management system that allows users to manage a collection of books.
# This code is responsible for the controller of the Library Management System.

from library_model import *
from library_view import *
from ImageDrawer import *
from tkinter import messagebox, filedialog, simpledialog, ttk

# Funnction to load the json file
def load_file_controller(display_book):
    try:
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        success, message = load_file_model(file_path)
        if success:
            messagebox.showinfo('Success', message)
            update_book_count(display_book)
        else:
            messagebox.showerror("Error", message)
    except Exception as e:
        messagebox.showerror("Error", f"Operation failed due to: {str(e)}")

# Function for saving library as a JSON file
def save_file_controller():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                 filetypes=[("JSON files", "*.json")])
        success, message = save_file_model(file_path)
        if success:
            messagebox.showinfo('Success', message)
        else:
            messagebox.showerror("Error", message)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save library. {str(e)}")

# Function to update book count
def update_book_count(display_book):
    display_book.configure(text=f'Current Book Count: {book_count()}')
    display_book.place(relx=0.5, rely=.85, anchor=CENTER)

# Function for adding books to library
def save_book_controller(enter_title, author, year, status, window_add, display_book):
    success, message = add_book_model(enter_title.get(), author, year, status.lower())
    if success:
        messagebox.showinfo('Success!', message)
        enter_title.delete(0, END)
        window_add.destroy()
        update_book_count(display_book)
    else:
        messagebox.showerror("Failed!", message)
        
# Confirms deleting a book if it exists in the library
def confirm_delete_controller(title, display_book):
    success, message = delete_book_model(title)
    if success:
        messagebox.showinfo('Success', message)
        update_book_count(display_book)
    else:
        messagebox.showinfo('Failed!', message)

# Function to Generate books using string random functions with button for cancellation of creation of already created books
def generate_books_controller(window, display_book):
    generate_batch, cancel_generation = generate_books_model()
    progress_window, label_gen, progress_bar = generate_books_view(lambda: [cancel_generation(), 
                                                                            progress_window.destroy(), 
                                                                            update_book_count(display_book)])
    
    def update_progress():
        if progress_window.winfo_exists():
            index, not_cancelled, progress = generate_batch()
            progress_bar['value'] = progress
            progress_window.update_idletasks()
            if index < 1_000_000 and not_cancelled:
                window.after(1, update_progress)
            else:
                label_gen.configure(text="Done!")
                update_book_count(display_book)
                window.after(100, lambda: progress_window.destroy())

    update_progress()

# Function for uploading image
def upload_image_controller(display_book):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image_window = Toplevel()
        image_window.title('Draw Rectangle on Image with OCR')
        image_window.geometry('600x600')
        # Pass callbacks to open add_book_view and search library with recognized text
        def save_book(recognized_text):
            add_book_view(lambda enter_title, author, year, status, 
                          window_add: save_book_controller(enter_title, 
                                                           author, 
                                                           year, 
                                                           status, 
                                                           window_add, 
                                                           display_book), recognized_text)
        def search_library(recognized_text):
            filtered = search_books_model(recognized_text.lower(), "", "", "")
            display_search_results(filtered, recognized_text)
        app = ImageDrawer(image_window, file_path, save_book, search_library)
        # Show OCR result when window closes
        def on_image_window_close():
            recognized_text = app.text_label.cget("text").replace("Recognized Text: ", "")
            success, message = upload_image_model(recognized_text)
            image_window.destroy()
            messagebox.showinfo('OCR Result', message)
        image_window.protocol("WM_DELETE_WINDOW", on_image_window_close)
    else:
        messagebox.showerror("Error", "No file selected.")

# Function for lending and receiving books
def lend_receive_controller():
    def search_books_controller():
        def search(title, author, year, status):
            filtered = search_books_model(title.lower(), author.lower(), year, status.lower())
            update_list_view(list_box, filtered)
            if not filtered:
                messagebox.showinfo('Unsuccessful', 'No Books Found.')
        search_books_view(search)

    def on_book_double_click(event):
        try:
            selected_book = list_box.get(list_box.curselection())
            book_number = selected_book.split(' - ')[0]
            new_status = simpledialog.askstring("Change Status", 
                                                "Enter new status (available/lent out/missing/deleted):")
            success, message = change_status_model(book_number, new_status)
            if success:
                messagebox.showinfo("Success", message)
                update_list_view(list_box, library)
            else:
                messagebox.showerror('Error', message)
        except IndexError:
            messagebox.showerror('Error', 'Please choose a valid book!')
        except Exception as e:
            messagebox.showerror('Error', f'Operation failed due to: {e}')

    def list_window_exit():
        list_window.destroy()

    list_window, list_box = lend_receive_view(search_books_controller, 
                                              list_window_exit, 
                                              on_book_double_click)
    if len(library) > 0:
        update_list_view(list_box, library)

# Initialize and run the application
if __name__ == "__main__":
    window, display_book = create_main_window_view(
        book_count_value=book_count(),
        save_cmd=lambda: save_file_controller(),
        load_cmd=lambda: load_file_controller(display_book),
        generate_cmd=lambda: generate_books_controller(window, display_book),
        about_cmd=lambda: about_page_view(),
        add_cmd=lambda: add_book_view(lambda enter_title, 
                                      author, 
                                      year, 
                                      status, 
                                      window_add: save_book_controller(enter_title, 
                                                                       author, 
                                                                       year, 
                                                                       status, 
                                                                       window_add, 
                                                                       display_book)),
        delete_cmd=lambda: delete_book_view(lambda title: confirm_delete_controller(title, display_book)),
        lend_cmd=lambda: lend_receive_controller(),
        upload_cmd=lambda: upload_image_controller(display_book)
    )
    # start the main loop
    window.mainloop()
