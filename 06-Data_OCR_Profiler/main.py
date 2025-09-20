# Created by: Rownak Deb Kabya 
# Email: rownak.kabya@stud.th-deg.de 

import json
import time
import random
import string
import pytesseract
from PIL import Image
from line_profiler import profile
from memory_profiler import profile as mem_profile

filename = "data_output.json"
data_list = []

@profile
def generate_entries(num_entries):
    """Generate a list of random string entries."""
    entries = []
    for _ in range(num_entries):
        entry = ''.join(random.choices(string.ascii_letters, k=3))
        entries.append(entry)
    return entries

@profile
def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, 'w') as fh:
        json.dump(data, fh)

@profile
def run_ocr(image_path):
    """Perform OCR on an image without user interaction."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        return f"OCR error: {e}"

@mem_profile
def main():
    print("--------------------------------------")
    # Generating 1 million entries
    start_time = time.time()
    global data_list
    data_list = generate_entries(1000000)
    end_time = time.time()
    gen_time = end_time - start_time
    print(f"Time to generate 1M entries: {gen_time:.2f} seconds")
    
    print("--------------------------------------")
    # Saving to JSON
    start_time = time.time()
    save_to_json(data_list, filename)
    end_time = time.time()
    io_time = end_time - start_time
    print(f"Time to save JSON: {io_time:.2f} seconds")
    
    print("--------------------------------------")
    # OCR
    start_time = time.time()
    ocr_result = run_ocr("sample.png")
    end_time = time.time()
    ocr_time = end_time - start_time
    print(f"OCR time: {ocr_time:.2f} seconds")
    print(f"OCR result: {ocr_result[:100]}...") 

if __name__ == "__main__":
    main()