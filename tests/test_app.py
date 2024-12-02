import pytest
from app.main import geocoding  # Example of testing your geocoding function

def test_geocoding_valid():
    # Test valid geocoding request
    status, lat, lng, location, _ = geocoding("New York")
    assert status == 200
    assert lat is not None
    assert lng is not None

def test_geocoding_invalid():
    # Test invalid geocoding request
    status, lat, lng, location, _ = geocoding("InvalidLocation123")
    assert status != 200