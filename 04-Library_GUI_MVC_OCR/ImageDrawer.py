
# This code is responsible for drawing rectangles on images and performing OCR.

import tkinter as tk
from PIL import Image, ImageTk
import pyocr
import pyocr.builders

class ImageDrawer:
    # Initialize the ImageDrawer with canvas and buttons
    def __init__(self, root, image_path, save_book_callback, search_library_callback):
        self.root = root
        self.image_path = image_path
        self.save_book_callback = save_book_callback
        self.search_library_callback = search_library_callback
        self.canvas = tk.Canvas(root, width=600, height=600)
        self.canvas.pack()

        # Load the original image
        self.image = Image.open(image_path)
        
        # Scale image to fit canvas
        img_width, img_height = self.image.size
        scale = min(500 / img_width, 500 / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        self.display_image = self.image.resize((new_width, new_height), Image.BICUBIC)
        
        # Create PhotoImage from scaled image
        self.image_tk = ImageTk.PhotoImage(self.display_image)
        
        # Display image on canvas
        self.canvas.create_image(250, 250, anchor=tk.CENTER, image=self.image_tk)

        # Variables for rectangle drawing
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.rect_id = None
        self.label = tk.Label(root, text="Dimensions: Width x Height", font=("Helvetica", 8))
        self.label.place(relx=0.15, rely=.95, anchor=tk.CENTER)
        self.text_label = tk.Label(root, text="Recognized Text: ", font=("Helvetica", 8))
        self.text_label.place(relx=0.5, rely=.9, anchor=tk.CENTER)

        # Save Book button
        self.save_button = tk.Button(root, text="Save Book", font=("Georgia", 10), fg="black", 
                                     command=self.open_add_book, state=tk.DISABLED)
        self.save_button.place(relx=0.4, rely=.95, anchor=tk.CENTER)

        # Search Library button
        self.search_button = tk.Button(root, text="Search Library", font=("Georgia", 10), fg="black", 
                                       command=self.search_library, state=tk.DISABLED)
        self.search_button.place(relx=0.6, rely=.95, anchor=tk.CENTER)

        # Set up OCR tool
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            raise Exception("No OCR tool found")
        self.tool = tools[0]

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Store scale for coordinates
        self.scale = scale

    # Start drawing rectangle
    def on_button_press(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 
                                                self.start_x, self.start_y, 
                                                outline="red", width=2)
        self.rect_id = self.rect

    # Update rectangle while dragging
    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")

    # Finalize rectangle and perform OCR
    def on_button_release(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.label.config(text=f"Dimensions: {width} x {height}")
        self.recognize_text_in_rectangle(self.start_x, self.start_y, event.x, event.y)

    # Recognize text in selected area
    def recognize_text_in_rectangle(self, x1, y1, x2, y2):
        img_width, img_height = self.image.size
        canvas_width, canvas_height = self.display_image.size
        offset_x = (500 - canvas_width) / 2
        offset_y = (500 - canvas_height) / 2
        orig_x1 = abs(int((x1 - offset_x) / self.scale))
        orig_y1 = abs(int((y1 - offset_y) / self.scale))
        orig_x2 = abs(int((x2 - offset_x) / self.scale))
        orig_y2 = abs(int((y2 - offset_y) / self.scale))

        orig_x1 = max(0, min(orig_x1, img_width))
        orig_y1 = max(0, min(orig_y1, img_height))
        orig_x2 = max(0, min(orig_x2, img_width))
        orig_y2 = max(0, min(orig_y2, img_height))

        cropped_image = self.image.crop((orig_x1, orig_y1, orig_x2, orig_y2))
        recognized_text = self.tool.image_to_string(cropped_image, 
                                                    lang='eng', 
                                                    builder=pyocr.builders.TextBuilder())
        self.text_label.config(text=f"Recognized Text: {recognized_text.strip()}")

        if recognized_text.strip():
            self.save_button.config(state=tk.NORMAL)
            self.search_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)
            self.search_button.config(state=tk.DISABLED)

    # Open add book window
    def open_add_book(self):
        recognized_text = self.text_label.cget("text").replace("Recognized Text: ", "")
        if recognized_text:
            self.save_book_callback(recognized_text)

    # Search library with recognized text
    def search_library(self):
        recognized_text = self.text_label.cget("text").replace("Recognized Text: ", "")
        if recognized_text:
            self.search_library_callback(recognized_text)