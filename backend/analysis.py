"""
Steganalysis engine for detecting LSB steganography in images.
Implements statistical detectors and visual analysis tools.
"""

import os
import base64
import tempfile
from typing import Dict, Any, List, Tuple
import numpy as np
from PIL import Image
import cv2
from scipy import stats
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import io

class SteganalysisEngine:
    """
    Steganalysis engine implementing:
    - Chi-square test for LSB distribution
    - RS analysis for sample pairs
    - Bit-plane analysis and visualization
    - Combined confidence scoring
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive steganalysis on an image.
        
        Args:
            image_path: Path to image to analyze
            
        Returns:
            Dictionary with analysis results and visualizations
        """
        # Load image
        img = Image.open(image_path)
        if img.mode not in ['RGB', 'RGBA']:
            img = img.convert('RGB')
        
        img_array = np.array(img)
        
        # Perform various analyses
        chi_square_results = self._chi_square_test(img_array)
        rs_results = self._rs_analysis(img_array)
        bitplane_results = self._bitplane_analysis(img_array)
        
        # Generate visualizations
        visualizations = self._generate_visualizations(img_array)
        
        # Calculate combined confidence
        confidence = self._calculate_confidence(chi_square_results, rs_results, bitplane_results)
        
        # Generate explanation
        explanation = self._generate_explanation(chi_square_results, rs_results, bitplane_results, confidence)
        
        return {
            "confidence": confidence,
            "chi_square": chi_square_results,
            "rs_score": rs_results,
            "bitplane_stats": bitplane_results,
            "visualizations": visualizations,
            "explanation": explanation
        }
    
    def _chi_square_test(self, img_array: np.ndarray) -> Dict[str, float]:
        """
        Perform chi-square test on LSB distribution.
        Tests for unnatural distribution of LSB values.
        """
        results = {}
        
        for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
            channel_data = img_array[:, :, channel_idx]
            
            # Count LSB values (0 and 1)
            lsb_values = channel_data & 1
            observed = np.bincount(lsb_values.flatten(), minlength=2)
            
            # Expected frequency (should be roughly equal)
            total_pixels = len(lsb_values.flatten())
            expected = np.array([total_pixels / 2, total_pixels / 2])
            
            # Chi-square test
            chi2_stat, p_value = stats.chisquare(observed, expected)
            
            # Calculate deviation from expected
            deviation = abs(observed[0] - observed[1]) / total_pixels
            
            results[channel_name] = {
                "chi2_statistic": float(chi2_stat),
                "p_value": float(p_value),
                "deviation": float(deviation),
                "suspicious": p_value < 0.05 and deviation > 0.1
            }
        
        return results
    
    def _rs_analysis(self, img_array: np.ndarray) -> Dict[str, float]:
        """
        Simplified RS analysis for detecting LSB steganography.
        Analyzes sample pairs and their relationships.
        """
        results = {}
        
        for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
            channel_data = img_array[:, :, channel_idx].astype(np.float32)
            
            # Create sample pairs (horizontal neighbors)
            pairs = []
            for i in range(channel_data.shape[0]):
                for j in range(channel_data.shape[1] - 1):
                    pairs.append((channel_data[i, j], channel_data[i, j + 1]))
            
            # Calculate RS statistics
            regular_pairs = 0
            singular_pairs = 0
            
            for x, y in pairs:
                # Simplified RS logic
                if abs(x - y) <= 1:
                    regular_pairs += 1
                elif abs(x - y) >= 2:
                    singular_pairs += 1
            
            total_pairs = len(pairs)
            if total_pairs > 0:
                rs_ratio = regular_pairs / total_pairs
                rs_score = abs(rs_ratio - 0.5)  # Deviation from expected 0.5
            else:
                rs_score = 0.0
            
            results[channel_name] = {
                "rs_score": float(rs_score),
                "regular_pairs": regular_pairs,
                "singular_pairs": singular_pairs,
                "suspicious": rs_score > 0.1
            }
        
        return results
    
    def _bitplane_analysis(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        Analyze bit-planes for steganographic artifacts.
        """
        results = {}
        
        for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
            channel_data = img_array[:, :, channel_idx]
            
            # Extract bit-planes
            bitplanes = []
            for bit in range(8):
                bitplane = (channel_data >> bit) & 1
                bitplanes.append(bitplane)
            
            # Analyze LSB plane (bit 0) for noise patterns
            lsb_plane = bitplanes[0]
            
            # Calculate noise variance in blocks
            block_size = 8
            noise_variances = []
            
            for i in range(0, lsb_plane.shape[0] - block_size, block_size):
                for j in range(0, lsb_plane.shape[1] - block_size, block_size):
                    block = lsb_plane[i:i+block_size, j:j+block_size]
                    variance = np.var(block.astype(np.float32))
                    noise_variances.append(variance)
            
            # Calculate statistics
            mean_variance = np.mean(noise_variances)
            std_variance = np.std(noise_variances)
            
            # Compare with higher bit-planes
            higher_bit_variance = np.var(bitplanes[1].astype(np.float32))
            
            # Suspicious if LSB variance is significantly different
            variance_ratio = mean_variance / (higher_bit_variance + 1e-6)
            
            results[channel_name] = {
                "lsb_variance": float(mean_variance),
                "lsb_std": float(std_variance),
                "higher_bit_variance": float(higher_bit_variance),
                "variance_ratio": float(variance_ratio),
                "suspicious": variance_ratio > 2.0 or variance_ratio < 0.5
            }
        
        return results
    
    def _generate_visualizations(self, img_array: np.ndarray) -> Dict[str, str]:
        """Generate visualization images for analysis."""
        visualizations = {}
        
        # Generate bit-plane visualizations
        for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
            channel_data = img_array[:, :, channel_idx]
            
            # Create bit-plane grid
            fig, axes = plt.subplots(2, 4, figsize=(12, 6))
            fig.suptitle(f'{channel_name.upper()} Channel Bit-Planes', fontsize=14)
            
            for bit in range(8):
                row = bit // 4
                col = bit % 4
                
                bitplane = (channel_data >> bit) & 1
                axes[row, col].imshow(bitplane, cmap='gray')
                axes[row, col].set_title(f'Bit {bit}')
                axes[row, col].axis('off')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            bitplane_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            visualizations[f'{channel_name}_bitplanes'] = bitplane_b64
            plt.close(fig)
        
        # Generate LSB histogram
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('LSB Distribution Analysis', fontsize=14)
        
        for channel_idx, channel_name in enumerate(['red', 'green', 'blue']):
            channel_data = img_array[:, :, channel_idx]
            lsb_values = channel_data & 1
            
            # Count LSB values
            counts = np.bincount(lsb_values.flatten(), minlength=2)
            axes[channel_idx].bar(['0', '1'], counts, color=['red', 'blue'])
            axes[channel_idx].set_title(f'{channel_name.upper()} Channel LSB Distribution')
            axes[channel_idx].set_ylabel('Count')
            
            # Add expected line
            expected = len(lsb_values.flatten()) / 2
            axes[channel_idx].axhline(y=expected, color='green', linestyle='--', 
                                    label=f'Expected: {expected:.0f}')
            axes[channel_idx].legend()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        histogram_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        visualizations['lsb_histogram'] = histogram_b64
        plt.close(fig)
        
        return visualizations
    
    def _calculate_confidence(self, 
                            chi_square_results: Dict[str, Any], 
                            rs_results: Dict[str, Any], 
                            bitplane_results: Dict[str, Any]) -> float:
        """
        Calculate combined confidence score for steganography detection.
        Returns value between 0 and 1.
        """
        confidence_scores = []
        
        # Chi-square confidence
        for channel, result in chi_square_results.items():
            if result['suspicious']:
                # Higher deviation and lower p-value = higher confidence
                deviation_score = min(result['deviation'] * 2, 1.0)
                p_value_score = 1.0 - result['p_value']
                chi_confidence = (deviation_score + p_value_score) / 2
                confidence_scores.append(chi_confidence)
        
        # RS analysis confidence
        for channel, result in rs_results.items():
            if result['suspicious']:
                rs_confidence = min(result['rs_score'] * 5, 1.0)
                confidence_scores.append(rs_confidence)
        
        # Bit-plane analysis confidence
        for channel, result in bitplane_results.items():
            if result['suspicious']:
                if result['variance_ratio'] > 2.0:
                    bp_confidence = min((result['variance_ratio'] - 2.0) / 3.0, 1.0)
                elif result['variance_ratio'] < 0.5:
                    bp_confidence = min((0.5 - result['variance_ratio']) / 0.5, 1.0)
                else:
                    bp_confidence = 0.0
                confidence_scores.append(bp_confidence)
        
        # Return maximum confidence (most suspicious channel)
        if confidence_scores:
            return min(max(confidence_scores), 1.0)
        else:
            return 0.0
    
    def _generate_explanation(self, 
                            chi_square_results: Dict[str, Any], 
                            rs_results: Dict[str, Any], 
                            bitplane_results: Dict[str, Any], 
                            confidence: float) -> str:
        """Generate human-readable explanation of analysis results."""
        explanations = []
        
        if confidence < 0.3:
            explanations.append("No significant steganographic artifacts detected.")
        elif confidence < 0.6:
            explanations.append("Some statistical anomalies detected, but inconclusive.")
        else:
            explanations.append("Strong evidence of steganographic content detected.")
        
        # Add specific findings
        suspicious_channels = []
        
        for channel, result in chi_square_results.items():
            if result['suspicious']:
                suspicious_channels.append(channel)
                explanations.append(f"{channel.upper()} channel shows unnatural LSB distribution (p={result['p_value']:.3f}).")
        
        for channel, result in rs_results.items():
            if result['suspicious']:
                explanations.append(f"{channel.upper()} channel RS analysis indicates potential LSB manipulation.")
        
        for channel, result in bitplane_results.items():
            if result['suspicious']:
                explanations.append(f"{channel.upper()} channel bit-plane analysis shows unusual noise patterns.")
        
        if suspicious_channels:
            explanations.append(f"Most suspicious channels: {', '.join(suspicious_channels).upper()}")
        
        return " ".join(explanations)
