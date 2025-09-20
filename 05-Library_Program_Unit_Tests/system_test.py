 # Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de

import unittest  
import subprocess  
import time  
import pyautogui  
from unittest.mock import patch, MagicMock  
from library_model import library  

class TestLibrarySystem(unittest.TestCase):  
    
    # Runs before the test
    def setUp(self): 
        # Clear the book list to start fresh
        library.clear()
        # Make the robot (pyautogui) move faster
        pyautogui.PAUSE = 0.1
        # Start the program like double-clicking it
        self.app = subprocess.Popen(["python3", "library_controller.py"])
        # Wait 2 seconds for the main window to open
        time.sleep(2)
    
    # Runs after the test
    def tearDown(self):  
        # Close the program
        self.app.terminate()
        # Clear the book list
        library.clear()
        # Reset the robot's speed
        pyautogui.PAUSE = 1
        
    # Fake choosing an image
    @patch('library_controller.filedialog.askopenfilename')  
    # Fake the OCR tool
    @patch('pyocr.get_available_tools')  
    @patch('pyocr.builders.TextBuilder')  # Fake the OCR settings
    def test_add_book_with_ocr(self, mock_text_builder, mock_get_tools, mock_askopenfilename):
        # Pretend the user chose an image file
        mock_askopenfilename.return_value = "test_image.png"
        # Pretend the OCR tool found "Sample Book Title"
        mock_tool = MagicMock()
        mock_tool.image_to_string.return_value = "Sample Book Title"
        mock_get_tools.return_value = [mock_tool]
        mock_text_builder.return_value = MagicMock()

        # Click the middle of the screen to focus the main window
        pyautogui.click(960, 540)  # Center of a 1920x1080 screen
        time.sleep(0.5)

        # Click the "Upload Image" button
        pyautogui.click(960, 794)  # Position in the main window
        time.sleep(1)

        # Draw a rectangle in the image window to select text
        pyautogui.moveTo(860, 440)  # Start point
        pyautogui.mouseDown()  # Hold the mouse
        pyautogui.moveTo(1060, 640, duration=0.5)  # Drag to end point
        pyautogui.mouseUp()  # Release the mouse
        time.sleep(1)

        # Click the "Save Book" button
        pyautogui.click(900, 810) 
        time.sleep(1)

        # Type details in the "Add New Book" window
        pyautogui.click(960, 495) 
        pyautogui.write("Sample Author")  
        pyautogui.click(960, 510) 
        pyautogui.write("Sample Author")
        pyautogui.click(960, 555) 
        pyautogui.write("2023")
        pyautogui.click(960, 615)  
        pyautogui.write("available")
        pyautogui.click(960, 495)  
        pyautogui.write("Sample Book Title")

        # Click the "Save" button
        pyautogui.click(960, 690)  # Position in the add book window
        time.sleep(1)

        # Check if the book was added to the library
        self.assertEqual(len(library), 1, "Library should contain one book")
        self.assertIn("1", library, "Book should be added with key '1'")
        self.assertEqual(library["1"]["title"], "Sample Book Title", "Book title should match")
        self.assertEqual(library["1"]["author"], "Sample Author", "Book author should match")
        self.assertEqual(library["1"]["year"], "2023", "Book year should match")
        self.assertEqual(library["1"]["status"], "available", "Book status should match")

if __name__ == "__main__":
    unittest.main()  # Run the test