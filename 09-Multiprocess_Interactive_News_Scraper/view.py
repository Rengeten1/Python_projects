from tkinter import messagebox, filedialog
import tkinter as tk
import time
import threading

def window(initial_headlines, filter_headlines_func, export_func, request_parse_strip_func):
    
    # Worker thread function to fetch news and update the UI 
    def _update_news_worker_thread():
        
        # This function runs in a separate thread to fetch news
        
        nonlocal tk_window # Allow access to the main Tkinter window object
        
        try:
            # Disable button during update
            if hasattr(tk_window, 'update_button'):
                tk_window.update_button.config(state=tk.DISABLED)
            
            new_headlines = request_parse_strip_func() 

            # Schedule UI updates back on the main Tkinter thread
            tk_window.after(0, lambda: _finalize_news_update(new_headlines, None))

        except Exception as e:
            tk_window.after(0, lambda: _finalize_news_update(None, e))
            
        finally:
            # Ensure button is re-enabled, schedule it on main thread
            if hasattr(tk_window, 'update_button'):
                tk_window.after(0, lambda: tk_window.update_button.config(state=tk.NORMAL))

    def _finalize_news_update(new_headlines, error):
        
        nonlocal tk_window # Allow access to the main Tkinter window object
        if error:
            messagebox.showerror("Error", f"Failed to update news: {error}")
        elif new_headlines is not None: # Check if new_headlines is not None
            tk_window.current_headlines = new_headlines 
            display_filtered() 
            messagebox.showinfo("Success", "News updated successfully.")
        else:
            messagebox.showwarning("Update Info", "News update completed, but no new data was returned.")

    def update_news_triggered():
        
        # Create and start the worker thread

        thread = threading.Thread(target=_update_news_worker_thread, daemon=True)
        thread.start()
    
    def filter_action():
        
        # Filters headlines based on the keyword from the entry.
        
        nonlocal tk_window 
        keyword_text = keyword_entry.get()
        if not keyword_text: 
            
            # Ensure the format is consistent for display_filtered
            if not tk_window.current_headlines:
                return []
            
            all_formatted = []
            if isinstance(tk_window.current_headlines, dict):
                 for source, news_list in tk_window.current_headlines.items():
                    for head_text in news_list: # Assuming news_list contains strings
                        all_formatted.append({'headline': head_text, 'source': source})
            return all_formatted

        # Use the filter_headlines_func passed from main.py
        filtered = filter_headlines_func(tk_window.current_headlines, keyword_text)
        return filtered

    def display_filtered():
        
        # Displays the filtered headlines in the listbox.
        
        nonlocal tk_window 
        listbox.delete(0, tk.END) 
        
        if not hasattr(tk_window, 'current_headlines') or not tk_window.current_headlines:
            listbox.insert(tk.END, "No headlines available. Try updating.")
            return

        filtered_results = filter_action() 
        
        if not filtered_results:
            listbox.insert(tk.END, "No results found for your criteria.")
        else:
            for head in filtered_results: 
                if isinstance(head, dict) and 'headline' in head and 'source' in head:
                    listbox.insert(tk.END, f"[{head['source']}] {head['headline']}")
                elif isinstance(head, str): 
                    listbox.insert(tk.END, head)


    def export_data():
        # Exports the current headlines (all or filtered) to a file.
        nonlocal tk_window 
        export_filename = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Exported Data"
        )

        if not export_filename:
            return

        try:
            data_to_export = []
            keyword_text = keyword_entry.get()

            if not keyword_text: # No keyword, export all current headlines
                if hasattr(tk_window, 'current_headlines') and tk_window.current_headlines:
                    # Format all headlines 
                    if isinstance(tk_window.current_headlines, dict):
                        for source, news_list in tk_window.current_headlines.items():
                            for head_text in news_list:
                                data_to_export.append({'headline': head_text, 'source': source})
                    else: 
                        data_to_export = tk_window.current_headlines
                else:
                    messagebox.showwarning("Export", "No headlines available to export.")
                    return
            else: # Export filtered headlines
                data_to_export = filter_action() # This should return list of dicts

            if not data_to_export:
                messagebox.showwarning("Export", "No data to export based on current filter.")
                return
            
            # Calling the export func from main.py

            export_func(data_to_export, export_filename, exception_view)
            messagebox.showinfo("Success", f"Data exported successfully to {export_filename}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

    # 

    try:
        tk_window = tk.Tk()
        tk_window.title("News Scraper")
        tk_window.geometry("500x450") # Adjusted size for better component fit
        tk_window.configure(bg="#f0f0f0") # Light grey background

        # Store initial headlines on the window object
        tk_window.current_headlines = initial_headlines if initial_headlines else {}

        tk.Label(tk_window, 
                 text="News Menu", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#333").pack(pady=15)

        # Frame for keyword input
        keyword_frame = tk.Frame(tk_window, bg="#f0f0f0")
        keyword_frame.pack(pady=5)
        tk.Label(keyword_frame, text="Keyword:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        keyword_entry = tk.Entry(keyword_frame, width=40, font=("Arial", 12), bd=2, relief="groove")
        keyword_entry.pack(side=tk.LEFT)
        keyword_entry.bind("<Return>", lambda event: display_filtered()) # Search on Enter

        # Frame for buttons
        button_frame = tk.Frame(tk_window, bg="#f0f0f0")
        button_frame.pack(pady=10)

        search_button = tk.Button(button_frame, text="Search", command=display_filtered, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", padx=10, pady=3)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Store update button on tk_window to manage its state
        tk_window.update_button = tk.Button(button_frame, text="Update News", command=update_news_triggered, font=("Arial", 10, "bold"), bg="#2196F3", fg="white", padx=10, pady=3)
        tk_window.update_button.pack(side=tk.LEFT, padx=5)
        
        export_button = tk.Button(button_frame, text="Export", command=export_data, font=("Arial", 10, "bold"), bg="#FF9800", fg="white", padx=10, pady=3)
        export_button.pack(side=tk.LEFT, padx=5)
        
        # Frame for listbox and scrollbar
        listbox_frame = tk.Frame(tk_window, bd=1, relief="sunken")
        listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, width=70, height=15, font=("Arial", 10), bd=0) # Adjusted width/height
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initial display of headlines
        display_filtered()
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while creating the window: {e}")
        if 'tk_window' in locals() and tk_window:
            tk_window.destroy()
        return
    tk_window.mainloop()

# Exception handling function to display errors in a messagebox
def exception_view(e):
    error_message = str(e) if isinstance(e, (str, Exception)) else "An unknown error occurred."
    messagebox.showerror("Error", f"An error occurred: {error_message}")

