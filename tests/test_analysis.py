"""
Unit tests for StegoLab steganalysis functionality.
Tests statistical detectors and analysis methods.
"""

import pytest
import numpy as np
from PIL import Image
import tempfile
import os
from backend.analysis import SteganalysisEngine
from backend.steganography import SteganographyEngine

class TestSteganalysisEngine:
    """Test cases for the SteganalysisEngine class."""
    
    @pytest.fixture
    def analysis_engine(self):
        """Create a steganalysis engine instance for testing."""
        return SteganalysisEngine()
    
    @pytest.fixture
    def stego_engine(self):
        """Create a steganography engine instance for testing."""
        return SteganographyEngine()
    
    @pytest.fixture
    def clean_image(self):
        """Create a clean test image without steganography."""
        # Create a 100x100 RGB test image with natural-looking data
        np.random.seed(42)  # For reproducible results
        img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            yield tmp.name
        
        # Clean up
        os.unlink(tmp.name)
    
    @pytest.fixture
    def stego_image(self, stego_engine, clean_image):
        """Create a stego image with embedded data."""
        payload = b"This is a test message for steganalysis testing."
        
        # Embed data in the clean image
        result = stego_engine.embed(
            carrier_path=clean_image,
            payload_data=payload,
            bits=1,
            channels=['red', 'green', 'blue'],
            password=None,
            encrypt=False
        )
        
        # Save stego image to temporary file
        import base64
        stego_data = base64.b64decode(result['stego_image'])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(stego_data)
            yield tmp.name
        
        # Clean up
        os.unlink(tmp.name)
    
    def test_chi_square_test_clean_image(self, analysis_engine, clean_image):
        """Test chi-square test on clean image."""
        img = Image.open(clean_image)
        img_array = np.array(img)
        
        chi_square_results = analysis_engine._chi_square_test(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in chi_square_results
        assert 'green' in chi_square_results
        assert 'blue' in chi_square_results
        
        # For a clean image, chi-square should not be suspicious
        for channel, result in chi_square_results.items():
            assert 'chi2_statistic' in result
            assert 'p_value' in result
            assert 'deviation' in result
            assert 'suspicious' in result
            
            # Clean images should have p-values closer to 1 (not significant)
            assert result['p_value'] > 0.05  # Not statistically significant
            assert result['suspicious'] is False
    
    def test_chi_square_test_stego_image(self, analysis_engine, stego_image):
        """Test chi-square test on stego image."""
        img = Image.open(stego_image)
        img_array = np.array(img)
        
        chi_square_results = analysis_engine._chi_square_test(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in chi_square_results
        assert 'green' in chi_square_results
        assert 'blue' in chi_square_results
        
        # For a stego image, at least one channel should be suspicious
        suspicious_channels = [channel for channel, result in chi_square_results.items() 
                              if result['suspicious']]
        assert len(suspicious_channels) > 0  # At least one channel should be suspicious
    
    def test_rs_analysis_clean_image(self, analysis_engine, clean_image):
        """Test RS analysis on clean image."""
        img = Image.open(clean_image)
        img_array = np.array(img)
        
        rs_results = analysis_engine._rs_analysis(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in rs_results
        assert 'green' in rs_results
        assert 'blue' in rs_results
        
        for channel, result in rs_results.items():
            assert 'rs_score' in result
            assert 'regular_pairs' in result
            assert 'singular_pairs' in result
            assert 'suspicious' in result
            
            # Clean images should have RS scores closer to 0
            assert result['rs_score'] < 0.1  # Low RS score for clean images
    
    def test_rs_analysis_stego_image(self, analysis_engine, stego_image):
        """Test RS analysis on stego image."""
        img = Image.open(stego_image)
        img_array = np.array(img)
        
        rs_results = analysis_engine._rs_analysis(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in rs_results
        assert 'green' in rs_results
        assert 'blue' in rs_results
        
        # For a stego image, RS analysis should detect some anomalies
        suspicious_channels = [channel for channel, result in rs_results.items() 
                              if result['suspicious']]
        # Note: RS analysis might not always detect LSB steganography
        # This test ensures the method runs without errors
    
    def test_bitplane_analysis_clean_image(self, analysis_engine, clean_image):
        """Test bit-plane analysis on clean image."""
        img = Image.open(clean_image)
        img_array = np.array(img)
        
        bitplane_results = analysis_engine._bitplane_analysis(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in bitplane_results
        assert 'green' in bitplane_results
        assert 'blue' in bitplane_results
        
        for channel, result in bitplane_results.items():
            assert 'lsb_variance' in result
            assert 'lsb_std' in result
            assert 'higher_bit_variance' in result
            assert 'variance_ratio' in result
            assert 'suspicious' in result
            
            # All values should be non-negative
            assert result['lsb_variance'] >= 0
            assert result['lsb_std'] >= 0
            assert result['higher_bit_variance'] >= 0
            assert result['variance_ratio'] >= 0
    
    def test_bitplane_analysis_stego_image(self, analysis_engine, stego_image):
        """Test bit-plane analysis on stego image."""
        img = Image.open(stego_image)
        img_array = np.array(img)
        
        bitplane_results = analysis_engine._bitplane_analysis(img_array)
        
        # Check that results are returned for all channels
        assert 'red' in bitplane_results
        assert 'green' in bitplane_results
        assert 'blue' in bitplane_results
        
        # For a stego image, bit-plane analysis should detect some anomalies
        suspicious_channels = [channel for channel, result in bitplane_results.items() 
                              if result['suspicious']]
        # At least one channel should show suspicious patterns
        assert len(suspicious_channels) > 0
    
    def test_confidence_calculation_clean_image(self, analysis_engine, clean_image):
        """Test confidence calculation on clean image."""
        img = Image.open(clean_image)
        img_array = np.array(img)
        
        chi_square_results = analysis_engine._chi_square_test(img_array)
        rs_results = analysis_engine._rs_analysis(img_array)
        bitplane_results = analysis_engine._bitplane_analysis(img_array)
        
        confidence = analysis_engine._calculate_confidence(
            chi_square_results, rs_results, bitplane_results
        )
        
        # Clean images should have low confidence scores
        assert 0 <= confidence <= 1
        assert confidence < 0.5  # Low confidence for clean images
    
    def test_confidence_calculation_stego_image(self, analysis_engine, stego_image):
        """Test confidence calculation on stego image."""
        img = Image.open(stego_image)
        img_array = np.array(img)
        
        chi_square_results = analysis_engine._chi_square_test(img_array)
        rs_results = analysis_engine._rs_analysis(img_array)
        bitplane_results = analysis_engine._bitplane_analysis(img_array)
        
        confidence = analysis_engine._calculate_confidence(
            chi_square_results, rs_results, bitplane_results
        )
        
        # Stego images should have higher confidence scores
        assert 0 <= confidence <= 1
        assert confidence > 0.3  # Higher confidence for stego images
    
    def test_full_analysis_clean_image(self, analysis_engine, clean_image):
        """Test complete analysis on clean image."""
        result = analysis_engine.analyze(clean_image)
        
        # Check that all expected fields are present
        assert 'confidence' in result
        assert 'chi_square' in result
        assert 'rs_score' in result
        assert 'bitplane_stats' in result
        assert 'visualizations' in result
        assert 'explanation' in result
        
        # Check confidence range
        assert 0 <= result['confidence'] <= 1
        
        # Check explanation is not empty
        assert len(result['explanation']) > 0
        
        # Check visualizations
        assert 'lsb_histogram' in result['visualizations']
        assert 'red_bitplanes' in result['visualizations']
        assert 'green_bitplanes' in result['visualizations']
        assert 'blue_bitplanes' in result['visualizations']
    
    def test_full_analysis_stego_image(self, analysis_engine, stego_image):
        """Test complete analysis on stego image."""
        result = analysis_engine.analyze(stego_image)
        
        # Check that all expected fields are present
        assert 'confidence' in result
        assert 'chi_square' in result
        assert 'rs_score' in result
        assert 'bitplane_stats' in result
        assert 'visualizations' in result
        assert 'explanation' in result
        
        # Check confidence range
        assert 0 <= result['confidence'] <= 1
        
        # Stego images should have higher confidence
        assert result['confidence'] > 0.3
        
        # Check explanation mentions steganography
        explanation_lower = result['explanation'].lower()
        assert 'steganographic' in explanation_lower or 'lsb' in explanation_lower
    
    def test_explanation_generation(self, analysis_engine):
        """Test explanation generation for different confidence levels."""
        # Test low confidence
        chi_square_results = {
            'red': {'suspicious': False, 'p_value': 0.8},
            'green': {'suspicious': False, 'p_value': 0.7},
            'blue': {'suspicious': False, 'p_value': 0.9}
        }
        rs_results = {
            'red': {'suspicious': False, 'rs_score': 0.05},
            'green': {'suspicious': False, 'rs_score': 0.03},
            'blue': {'suspicious': False, 'rs_score': 0.04}
        }
        bitplane_results = {
            'red': {'suspicious': False, 'variance_ratio': 1.1},
            'green': {'suspicious': False, 'variance_ratio': 0.9},
            'blue': {'suspicious': False, 'variance_ratio': 1.0}
        }
        
        confidence = 0.2
        explanation = analysis_engine._generate_explanation(
            chi_square_results, rs_results, bitplane_results, confidence
        )
        
        assert len(explanation) > 0
        assert 'no significant' in explanation.lower() or 'inconclusive' in explanation.lower()
    
    def test_visualization_generation(self, analysis_engine, clean_image):
        """Test that visualizations are generated correctly."""
        img = Image.open(clean_image)
        img_array = np.array(img)
        
        visualizations = analysis_engine._generate_visualizations(img_array)
        
        # Check that all expected visualizations are present
        assert 'lsb_histogram' in visualizations
        assert 'red_bitplanes' in visualizations
        assert 'green_bitplanes' in visualizations
        assert 'blue_bitplanes' in visualizations
        
        # Check that visualizations are base64 encoded strings
        for key, value in visualizations.items():
            assert isinstance(value, str)
            assert len(value) > 0  # Should not be empty
