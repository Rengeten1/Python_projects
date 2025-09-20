 # Library Management System V: 3.0
# Created by: Rownak Deb Kabya & Marcos Blanco-Leon
# Email: rownak.kabya@stud.th-deg.de 
# Email: marcos.blanco-Leon@stud.th-deg.de
import unittest
from unittest.mock import patch, mock_open
from library_model import book_count, upload_image_model, load_file_model, save_file_model, add_book_model, delete_book_model, search_books_model, library

class TestLibraryModel(unittest.TestCase):
    def setUp(self):
        # Clear the global library to ensure test isolation
        library.clear()
        # Initialize with test data
        self.test_library = {
            "1": {"title": "Test Book 1", "author": "Author 1", "year": "2020", "status": "available"},
            "2": {"title": "Test Book 2", "author": "Author 2", "year": "2021", "status": "lent out"},
            "3": {"title": "Test Book 3", "author": "Author 3", "year": "2022", "status": "missing"}
        }

    def tearDown(self):
        # Clear the library after each test
        library.clear()

    def test_book_count(self):
        library.update(self.test_library)
        self.assertEqual(book_count(), 3, "Book count should match the number of books in the library")
    
    # book addition test for valid data
    def test_add_book_model_valid(self):
        title, author, year, status = "New Book", "New Author", "2023", "available"
        success, message = add_book_model(title, author, year, status)
        self.assertTrue(success, "Adding a valid book should succeed")
        self.assertEqual(message, f"Book {title} Added!", "Message should confirm book addition")
        self.assertIn("1", library, "Book should be added to the library")
        self.assertEqual(library["1"]["title"], title, "Book title should match")
    
    # book addition test invalid status
    def test_add_book_model_invalid_status(self):
        title, author, year, status = "New Book", "New Author", "2023", "invalid"
        success, message = add_book_model(title, author, year, status)
        self.assertFalse(success, "Adding a book with invalid status should fail")
        self.assertEqual(message, "Status is not valid!", "Message should indicate invalid status")
    
    # book addition test
    def test_delete_book_model_valid(self):
        library.update(self.test_library)
        title = "Test Book 1"
        success, message = delete_book_model(title)
        self.assertTrue(success, "Deleting an existing book should succeed")
        self.assertEqual(message, f"Book {title} deleted!", "Message should confirm deletion")
        self.assertEqual(library["1"]["status"], "deleted", "Book status should be set to deleted")
    
    # book deletion test
    def test_delete_book_model_nonexistent(self):
        library.update(self.test_library)
        title = "Nonexistent Book"
        success, message = delete_book_model(title)
        self.assertFalse(success, "Deleting a nonexistent book should fail")
        self.assertEqual(message, "Book with Title not found!", "Message should indicate book not found")
    def test_search_book_model(self):
        library.update(self.test_library)
        title, author, year, status = "Test Book 1", "Author 1", "2020", "available"
        result = search_books_model(title.lower(), author.lower(), year, status.lower())
        self.assertEqual(len(result), 1, "Search should return one book")
        self.assertEqual(result[0]["title"], title, "Book title should match the search criteria")

        
if __name__ == "__main__":
    unittest.main()