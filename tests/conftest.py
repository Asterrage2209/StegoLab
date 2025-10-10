"""
Pytest configuration and shared fixtures for StegoLab tests.
"""

import pytest
import tempfile
import os
from PIL import Image
import numpy as np

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_png_image(test_data_dir):
    """Create a sample PNG image for testing."""
    # Create a 200x200 RGB image with some pattern
    img_array = np.zeros((200, 200, 3), dtype=np.uint8)
    
    # Add some pattern to make it more realistic
    for i in range(200):
        for j in range(200):
            img_array[i, j, 0] = (i + j) % 256  # Red channel
            img_array[i, j, 1] = (i * 2 + j) % 256  # Green channel
            img_array[i, j, 2] = (i + j * 2) % 256  # Blue channel
    
    img = Image.fromarray(img_array, 'RGB')
    img_path = os.path.join(test_data_dir, 'sample.png')
    img.save(img_path)
    
    return img_path

@pytest.fixture
def sample_bmp_image(test_data_dir):
    """Create a sample BMP image for testing."""
    # Create a 100x100 RGB image
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')
    img_path = os.path.join(test_data_dir, 'sample.bmp')
    img.save(img_path)
    
    return img_path

@pytest.fixture
def sample_text_payload():
    """Create a sample text payload for testing."""
    return b"This is a test message for StegoLab steganography testing. " * 10

@pytest.fixture
def sample_binary_payload():
    """Create a sample binary payload for testing."""
    return bytes(range(256))  # All byte values 0-255

@pytest.fixture
def large_payload():
    """Create a large payload for capacity testing."""
    return b"Large payload data " * 1000  # ~18KB

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
