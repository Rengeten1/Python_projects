# Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de
import unittest
from unittest.mock import patch, MagicMock
from library_controller import save_book_controller
from library_model import library

class TestLibraryIntegration(unittest.TestCase):
    # Runs before each test
    def setUp(self):  
        library.clear()
        
        # Creating Fake GUI Elements
        self.enter_title = MagicMock()
        self.display_book = MagicMock()
        self.window_add = MagicMock()
    
    # Runs after each test
    def tearDown(self):
        library.clear()
    
    @patch('library_controller.messagebox')
    @patch('library_controller.update_book_count')
    def test_save_book_controller_integration(self, mock_update_book_count, mock_messagebox):
        # Pretend the user typed "New Book" in the title field
        self.enter_title.get.return_value = "New Book"
        # Set other book details
        author = "New Author"
        year = "2023"
        status = "available"
        
        # To make like user clicked Save        
        save_book_controller(self.enter_title, author, year, status, self.window_add, self.display_book)
        
        # Checking if the book was added to the library
        self.assertEqual(len(library), 1, "Library should have one book")
        self.assertIn("1", library, "Book should be added as 1")
        self.assertEqual(library["1"]["title"], "New Book", "Book title should match")
        self.assertEqual(library["1"]["author"], author, "Book author should match")
        self.assertEqual(library["1"]["year"], year, "Book year should match")
        self.assertEqual(library["1"]["status"], status, "Book status should match")
        
        # Check if the GUI was updated in library_view.py
        mock_messagebox.showinfo.assert_called_once_with("Success!", "Book New Book Added!")
        self.enter_title.delete.assert_called_with(0, "end")
        self.window_add.destroy.assert_called_once()
        mock_update_book_count.assert_called_once_with(self.display_book)
        
if __name__ == "__main__":
    unittest.main()