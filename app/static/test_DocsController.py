import unittest
from io import BytesIO
from app.controllers.DocsControlller import compress_file
import zlib

# FILE: app/controllers/test_DocsControlller.py


class TestDocsController(unittest.TestCase):

    def test_compress_file_with_content(self):
        # Create a BytesIO object to simulate a file with content
        file_content = b'This is a test file content'
        file = BytesIO(file_content)
        
        # Compress the file using the function
        compressed_data = compress_file(file)
        
        # Verify that the compressed data is not None
        self.assertIsNotNone(compressed_data)
        
        # Verify that the compressed data is actually compressed
        self.assertNotEqual(file_content, compressed_data)
        
        # Verify that the compressed data can be decompressed back to the original content
        decompressed_data = zlib.decompress(compressed_data)
        self.assertEqual(decompressed_data, file_content)

    def test_compress_file_with_none(self):
        # Compress the file using the function with None
        compressed_data = compress_file(None)
        
        # Verify that the compressed data is None
        self.assertIsNone(compressed_data)

if __name__ == '__main__':
    unittest.main()
    