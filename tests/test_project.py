import unittest
import sys
import os

# Add the path of the 'DEVASC' directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(r"C:\Users\user\Desktop\python folder\DEVASC")

from MapQuest import geocoding

class TestYourFunction(unittest.TestCase):
    def test_geocoding(self):
        instance = GeoLocatorApp()  # Create an instance of the class
        result = instance.geocoding("some_location")  # Call the method
        self.assertEqual(result, expected_value)  # Replace expected_value with the correct result

if __name__ == '__main__':
    unittest.main()