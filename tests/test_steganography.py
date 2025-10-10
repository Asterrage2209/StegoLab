"""
Unit tests for StegoLab steganography functionality.
Tests embedding, extraction, and roundtrip operations.
"""

import pytest
import numpy as np
from PIL import Image
import tempfile
import os
from backend.steganography import SteganographyEngine

class TestSteganographyEngine:
    """Test cases for the SteganographyEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create a steganography engine instance for testing."""
        return SteganographyEngine()
    
    @pytest.fixture
    def test_image(self):
        """Create a test PNG image for embedding."""
        # Create a 100x100 RGB test image
        img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            yield tmp.name
        
        # Clean up
        os.unlink(tmp.name)
    
    @pytest.fixture
    def test_payload(self):
        """Create test payload data."""
        return b"Hello, StegoLab! This is a test message for LSB steganography."
    
    def test_calculate_capacity(self, engine, test_image):
        """Test capacity calculation for different configurations."""
        img = Image.open(test_image)
        
        # Test 1 LSB, all channels
        capacity_1bit = engine._calculate_capacity(img, 1, 3)
        assert capacity_1bit > 0
        
        # Test 2 LSB, all channels
        capacity_2bit = engine._calculate_capacity(img, 2, 3)
        assert capacity_2bit > capacity_1bit
        
        # Test 1 LSB, single channel
        capacity_1bit_1channel = engine._calculate_capacity(img, 1, 1)
        assert capacity_1bit_1channel < capacity_1bit
    
    def test_header_creation_and_validation(self, engine, test_payload):
        """Test header creation and validation."""
        # Create payload with header
        payload_with_header = engine._create_payload_with_header(test_payload, False, None)
        
        # Check header size
        assert len(payload_with_header) == len(test_payload) + engine.HEADER_SIZE
        
        # Validate header
        header_data = payload_with_header[:engine.HEADER_SIZE]
        assert engine._validate_header(header_data)
        
        # Test invalid header
        invalid_header = b'INVALID_HEADER_DATA'
        assert not engine._validate_header(invalid_header)
    
    def test_embed_extract_roundtrip_1bit(self, engine, test_image, test_payload):
        """Test complete embed-extract roundtrip with 1 LSB."""
        # Embed data
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=None,
            encrypt=False
        )
        
        assert result['success'] is True
        assert 'stego_image' in result
        assert 'metrics' in result
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=1,
                channels=['red', 'green', 'blue'],
                password=None,
                encrypt=False
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_text'] == test_payload.decode('utf-8')
            assert extract_result['payload_type'] == 'text'
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_embed_extract_roundtrip_2bit(self, engine, test_image, test_payload):
        """Test complete embed-extract roundtrip with 2 LSBs."""
        # Embed data
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=2,
            channels=['red', 'green', 'blue'],
            password=None,
            encrypt=False
        )
        
        assert result['success'] is True
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=2,
                channels=['red', 'green', 'blue'],
                password=None,
                encrypt=False
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_text'] == test_payload.decode('utf-8')
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_embed_extract_with_password(self, engine, test_image, test_payload):
        """Test embed-extract roundtrip with password permutation."""
        password = "test_password_123"
        
        # Embed data with password
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=password,
            encrypt=False
        )
        
        assert result['success'] is True
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data with correct password
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=1,
                channels=['red', 'green', 'blue'],
                password=password,
                encrypt=False
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_text'] == test_payload.decode('utf-8')
            
            # Test extraction with wrong password
            with pytest.raises(ValueError, match="Invalid stego image"):
                engine.extract(
                    stego_path=stego_path,
                    bits=1,
                    channels=['red', 'green', 'blue'],
                    password="wrong_password",
                    encrypt=False
                )
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_embed_extract_with_encryption(self, engine, test_image, test_payload):
        """Test embed-extract roundtrip with encryption."""
        password = "encryption_password_456"
        
        # Embed data with encryption
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=password,
            encrypt=True
        )
        
        assert result['success'] is True
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data with correct password
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=1,
                channels=['red', 'green', 'blue'],
                password=password,
                encrypt=True
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_text'] == test_payload.decode('utf-8')
            
            # Test extraction with wrong password
            with pytest.raises(Exception):  # Should fail with wrong password
                engine.extract(
                    stego_path=stego_path,
                    bits=1,
                    channels=['red', 'green', 'blue'],
                    password="wrong_password",
                    encrypt=True
                )
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_single_channel_embedding(self, engine, test_image, test_payload):
        """Test embedding in single color channel."""
        # Test red channel only
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=1,
            channels=['red'],
            password=None,
            encrypt=False
        )
        
        assert result['success'] is True
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=1,
                channels=['red'],
                password=None,
                encrypt=False
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_text'] == test_payload.decode('utf-8')
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_payload_too_large(self, engine, test_image):
        """Test error handling when payload is too large."""
        # Create payload larger than capacity
        large_payload = b"x" * 100000  # Very large payload
        
        with pytest.raises(ValueError, match="Payload too large"):
            engine.embed(
                carrier_path=test_image,
                payload_data=large_payload,
                bits=1,
                channels=['red'],
                password=None,
                encrypt=False
            )
    
    def test_binary_payload(self, engine, test_image):
        """Test embedding and extracting binary data."""
        # Create binary payload (not valid UTF-8)
        binary_payload = bytes(range(256))  # All byte values 0-255
        
        # Embed data
        result = engine.embed(
            carrier_path=test_image,
            payload_data=binary_payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=None,
            encrypt=False
        )
        
        assert result['success'] is True
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            stego_path = tmp.name
        
        try:
            # Extract data
            extract_result = engine.extract(
                stego_path=stego_path,
                bits=1,
                channels=['red', 'green', 'blue'],
                password=None,
                encrypt=False
            )
            
            assert extract_result['success'] is True
            assert extract_result['payload_type'] == 'binary'
            assert 'payload_file' in extract_result
            
            # Verify extracted binary data
            import base64
            extracted_data = base64.b64decode(extract_result['payload_file'])
            assert extracted_data == binary_payload
            
        finally:
            # Clean up
            os.unlink(stego_path)
    
    def test_metrics_calculation(self, engine, test_image, test_payload):
        """Test that metrics are calculated correctly."""
        result = engine.embed(
            carrier_path=test_image,
            payload_data=test_payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=None,
            encrypt=False
        )
        
        metrics = result['metrics']
        
        # Check that all expected metrics are present
        assert 'capacity_bytes' in metrics
        assert 'payload_size' in metrics
        assert 'embedding_efficiency' in metrics
        assert 'psnr' in metrics
        assert 'ssim' in metrics
        assert 'bits_used' in metrics
        assert 'channels_used' in metrics
        
        # Check metric values
        assert metrics['payload_size'] == len(test_payload)
        assert metrics['bits_used'] == 1
        assert metrics['channels_used'] == ['red', 'green', 'blue']
        assert 0 <= metrics['embedding_efficiency'] <= 1
        assert metrics['psnr'] > 0  # PSNR should be positive
        assert 0 <= metrics['ssim'] <= 1  # SSIM should be between 0 and 1
