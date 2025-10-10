"""
Core LSB steganography implementation for StegoLab.
Handles embedding and extraction of data in images using LSB substitution.
"""

import os
import struct
import hashlib
import random
import base64
from typing import List, Optional, Dict, Any, Tuple
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import zlib

class SteganographyEngine:
    """
    LSB steganography engine supporting:
    - PNG/BMP embedding (lossless formats)
    - 1-2 LSBs per channel
    - Multiple color channels (R, G, B)
    - Password-based permutation
    - AES encryption of payload
    - Header with length and checksum
    """
    
    # Header format: 4-byte magic + 4-byte length + 4-byte CRC32 + 4-byte reserved
    HEADER_SIZE = 16
    MAGIC_BYTES = b'STEG'
    
    def __init__(self):
        self.max_file_size = 5 * 1024 * 1024  # 5MB limit
    
    def embed(self, 
              carrier_path: str, 
              payload_data: bytes, 
              bits: int = 1, 
              channels: List[str] = None,
              password: Optional[str] = None,
              encrypt: bool = False) -> Dict[str, Any]:
        """
        Embed payload data into carrier image using LSB steganography.
        
        Args:
            carrier_path: Path to carrier image
            payload_data: Data to embed
            bits: Number of LSBs to use (1 or 2)
            channels: List of channels to use ['red', 'green', 'blue']
            password: Optional password for permutation/encryption
            encrypt: Whether to encrypt payload before embedding
            
        Returns:
            Dictionary with stego image data and metrics
        """
        if channels is None:
            channels = ['red', 'green', 'blue']
        
        # Load and validate carrier image
        carrier_img = Image.open(carrier_path)
        if carrier_img.mode not in ['RGB', 'RGBA']:
            carrier_img = carrier_img.convert('RGB')
        
        # Calculate capacity
        capacity = self._calculate_capacity(carrier_img, bits, len(channels))
        if len(payload_data) > capacity:
            raise ValueError(f"Payload too large: {len(payload_data)} bytes > {capacity} bytes capacity")
        
        # Prepare payload with header
        payload_with_header = self._create_payload_with_header(payload_data, encrypt, password)
        
        # Encrypt if requested
        if encrypt and password:
            payload_with_header = self._encrypt_payload(payload_with_header, password)
        
        # Convert image to numpy array
        img_array = np.array(carrier_img)
        original_array = img_array.copy()
        
        # Generate embedding positions
        positions = self._generate_embedding_positions(
            img_array.shape, len(payload_with_header), password
        )
        
        # Embed data
        self._embed_data(img_array, payload_with_header, positions, bits, channels)
        
        # Create stego image
        stego_img = Image.fromarray(img_array)
        
        # Calculate metrics
        metrics = self._calculate_metrics(original_array, img_array)
        
        # Save stego image to temporary file
        stego_path = os.path.join(os.path.dirname(carrier_path), "stego_temp.png")
        stego_img.save(stego_path, "PNG")
        
        # Read stego image as base64
        with open(stego_path, "rb") as f:
            stego_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # Clean up
        os.remove(stego_path)
        
        return {
            "success": True,
            "stego_image": stego_base64,
            "metrics": {
                "capacity_bytes": capacity,
                "payload_size": len(payload_data),
                "embedding_efficiency": len(payload_data) / capacity,
                "psnr": metrics["psnr"],
                "ssim": metrics["ssim"],
                "bits_used": bits,
                "channels_used": channels
            }
        }
    
    def extract(self, 
                stego_path: str, 
                bits: int = 1, 
                channels: List[str] = None,
                password: Optional[str] = None,
                encrypt: bool = False) -> Dict[str, Any]:
        """
        Extract payload data from stego image.
        
        Args:
            stego_path: Path to stego image
            bits: Number of LSBs used
            channels: List of channels used
            password: Password used during embedding
            encrypt: Whether payload was encrypted
            
        Returns:
            Dictionary with extracted payload data
        """
        if channels is None:
            channels = ['red', 'green', 'blue']
        
        # Load stego image
        stego_img = Image.open(stego_path)
        if stego_img.mode not in ['RGB', 'RGBA']:
            stego_img = stego_img.convert('RGB')
        
        img_array = np.array(stego_img)
        
        # Extract header first
        header_positions = self._generate_embedding_positions(
            img_array.shape, self.HEADER_SIZE, password
        )
        
        header_data = self._extract_data(img_array, header_positions, bits, channels, self.HEADER_SIZE)
        
        # Validate header
        if not self._validate_header(header_data):
            raise ValueError("Invalid stego image: header not found or corrupted")
        
        # Parse header
        magic, payload_length, crc32, _ = struct.unpack('>4sIII', header_data)
        
        # Extract payload
        payload_positions = self._generate_embedding_positions(
            img_array.shape, payload_length, password, offset=self.HEADER_SIZE
        )
        
        payload_data = self._extract_data(img_array, payload_positions, bits, channels, payload_length)
        
        # Decrypt if needed
        if encrypt and password:
            payload_data = self._decrypt_payload(payload_data, password)
        
        # Verify CRC32
        if zlib.crc32(payload_data) != crc32:
            raise ValueError("Payload corruption detected: CRC32 mismatch")
        
        # Try to decode as text, otherwise return as binary
        try:
            payload_text = payload_data.decode('utf-8')
            return {
                "success": True,
                "payload_text": payload_text,
                "payload_type": "text"
            }
        except UnicodeDecodeError:
            # Return as base64 encoded binary data
            payload_base64 = base64.b64encode(payload_data).decode('utf-8')
            return {
                "success": True,
                "payload_file": payload_base64,
                "payload_type": "binary"
            }
    
    def _calculate_capacity(self, img: Image.Image, bits: int, num_channels: int) -> int:
        """Calculate maximum payload capacity in bytes."""
        width, height = img.size
        pixels = width * height
        bits_per_pixel = bits * num_channels
        total_bits = pixels * bits_per_pixel
        # Reserve space for header
        available_bits = total_bits - (self.HEADER_SIZE * 8)
        return available_bits // 8
    
    def _create_payload_with_header(self, payload_data: bytes, encrypt: bool, password: Optional[str]) -> bytes:
        """Create payload with header containing length and checksum."""
        crc32 = zlib.crc32(payload_data) & 0xffffffff
        header = struct.pack('>4sIII', self.MAGIC_BYTES, len(payload_data), crc32, 0)
        return header + payload_data
    
    def _validate_header(self, header_data: bytes) -> bool:
        """Validate stego header."""
        if len(header_data) != self.HEADER_SIZE:
            return False
        magic, _, _, _ = struct.unpack('>4sIII', header_data)
        return magic == self.MAGIC_BYTES
    
    def _generate_embedding_positions(self, 
                                    img_shape: Tuple[int, ...], 
                                    data_length: int, 
                                    password: Optional[str] = None,
                                    offset: int = 0) -> List[Tuple[int, int, int]]:
        """Generate positions for embedding data."""
        height, width, channels = img_shape
        total_pixels = height * width
        
        # Calculate number of pixels needed
        bits_needed = data_length * 8
        pixels_needed = (bits_needed + 7) // 8  # Round up
        
        if password:
            # Use password to seed random number generator for permutation
            seed = int(hashlib.sha256(password.encode()).hexdigest()[:8], 16)
            rng = random.Random(seed)
            positions = [(i // width, i % width, i % channels) for i in range(total_pixels)]
            rng.shuffle(positions)
            return positions[offset:offset + pixels_needed]
        else:
            # Sequential embedding
            positions = []
            for i in range(offset, offset + pixels_needed):
                row = i // width
                col = i % width
                channel = i % channels
                positions.append((row, col, channel))
            return positions
    
    def _embed_data(self, 
                   img_array: np.ndarray, 
                   data: bytes, 
                   positions: List[Tuple[int, int, int]], 
                   bits: int, 
                   channels: List[str]) -> None:
        """Embed data into image array at specified positions."""
        channel_map = {'red': 0, 'green': 1, 'blue': 2}
        bit_mask = (1 << bits) - 1  # Create mask for LSBs
        
        for i, (row, col, channel_idx) in enumerate(positions):
            if i * 8 >= len(data) * 8:
                break
                
            # Get byte and bit position
            byte_idx = i // 8
            bit_idx = i % 8
            
            if byte_idx >= len(data):
                break
                
            # Extract bits from data
            data_byte = data[byte_idx]
            bits_to_embed = (data_byte >> (7 - bit_idx)) & bit_mask
            
            # Clear LSBs and embed new bits
            img_array[row, col, channel_idx] &= ~bit_mask
            img_array[row, col, channel_idx] |= bits_to_embed
    
    def _extract_data(self, 
                     img_array: np.ndarray, 
                     positions: List[Tuple[int, int, int]], 
                     bits: int, 
                     channels: List[str], 
                     length: int) -> bytes:
        """Extract data from image array at specified positions."""
        channel_map = {'red': 0, 'green': 1, 'blue': 2}
        bit_mask = (1 << bits) - 1
        result = bytearray()
        
        for i in range(length * 8):  # length in bytes, so * 8 for bits
            if i >= len(positions):
                break
                
            row, col, channel_idx = positions[i]
            
            # Extract bits from pixel
            pixel_value = img_array[row, col, channel_idx]
            extracted_bits = pixel_value & bit_mask
            
            # Pack bits into bytes
            byte_idx = i // 8
            bit_idx = i % 8
            
            if byte_idx >= len(result):
                result.append(0)
            
            result[byte_idx] |= (extracted_bits << (7 - bit_idx))
        
        return bytes(result)
    
    def _encrypt_payload(self, payload: bytes, password: str) -> bytes:
        """Encrypt payload using AES encryption."""
        # Derive key from password
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        
        # Encrypt payload
        encrypted = fernet.encrypt(payload)
        
        # Prepend salt to encrypted data
        return salt + encrypted
    
    def _decrypt_payload(self, encrypted_payload: bytes, password: str) -> bytes:
        """Decrypt payload using AES decryption."""
        # Extract salt
        salt = encrypted_payload[:16]
        encrypted_data = encrypted_payload[16:]
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        
        # Decrypt payload
        return fernet.decrypt(encrypted_data)
    
    def _calculate_metrics(self, original: np.ndarray, stego: np.ndarray) -> Dict[str, float]:
        """Calculate PSNR and SSIM metrics."""
        # Calculate PSNR
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
        
        # Calculate SSIM (simplified version)
        mu1 = np.mean(original)
        mu2 = np.mean(stego)
        sigma1 = np.var(original)
        sigma2 = np.var(stego)
        sigma12 = np.mean((original - mu1) * (stego - mu2))
        
        c1 = 0.01 ** 2
        c2 = 0.03 ** 2
        
        ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
               ((mu1 ** 2 + mu2 ** 2 + c1) * (sigma1 + sigma2 + c2))
        
        return {
            "psnr": float(psnr),
            "ssim": float(ssim)
        }
