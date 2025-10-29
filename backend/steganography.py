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
        
        # Prepare payload (optionally encrypted) with header
        if encrypt and password:
            encrypted_payload = self._encrypt_payload(payload_data, password)
            crc_plain = zlib.crc32(payload_data) & 0xffffffff
            payload_with_header = self._create_payload_with_header(encrypted_payload, plaintext_crc32=crc_plain)
        else:
            payload_with_header = self._create_payload_with_header(payload_data)
        
        # Convert image to numpy array
        img_array = np.array(carrier_img)
        original_array = img_array.copy()
        
        # Determine channel indices
        selected_channels = self._get_channel_indices(channels)

        # Calculate how many positions are needed (each position carries `bits` bits)
        total_bits = len(payload_with_header) * 8
        positions_needed = (total_bits + bits - 1) // bits

        # Generate embedding positions
        positions = self._generate_embedding_positions(
            img_array.shape, positions_needed, password, selected_channels, start_index=0
        )
        
        # Embed data
        self._embed_data(img_array, payload_with_header, positions, bits)
        
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
        selected_channels = self._get_channel_indices(channels)
        
        # Load stego image
        stego_img = Image.open(stego_path)
        if stego_img.mode not in ['RGB', 'RGBA']:
            stego_img = stego_img.convert('RGB')
        
        img_array = np.array(stego_img)
        
        # Extract header first
        header_bits = self.HEADER_SIZE * 8
        header_positions_needed = (header_bits + bits - 1) // bits
        header_positions = self._generate_embedding_positions(
            img_array.shape, header_positions_needed, password, selected_channels, start_index=0
        )
        
        header_data = self._extract_data(img_array, header_positions, bits, self.HEADER_SIZE)
        
        # Validate header
        if not self._validate_header(header_data):
            raise ValueError("Invalid stego image: header not found or corrupted")
        
        # Parse header
        magic, payload_length, crc32, _ = struct.unpack('>4sIII', header_data)
        
        # Extract payload
        payload_bits = payload_length * 8
        payload_positions_needed = (payload_bits + bits - 1) // bits
        payload_positions = self._generate_embedding_positions(
            img_array.shape, payload_positions_needed, password, selected_channels, start_index=header_positions_needed
        )
        
        payload_data = self._extract_data(img_array, payload_positions, bits, payload_length)
        
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
    
    def _create_payload_with_header(self, payload_data: bytes, plaintext_crc32: Optional[int] = None) -> bytes:
        """Create payload with header containing length and checksum.
        If plaintext_crc32 is provided, it will be used; otherwise CRC is computed over payload_data.
        """
        crc32 = (plaintext_crc32 if plaintext_crc32 is not None else (zlib.crc32(payload_data) & 0xffffffff))
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
                                      positions_needed: int,
                                      password: Optional[str] = None,
                                      selected_channels: Optional[List[int]] = None,
                                      start_index: int = 0) -> List[Tuple[int, int, int]]:
        """Generate positions for embedding/extracting. Each position corresponds to one (row,col,channel)."""
        height, width, num_channels = img_shape
        if selected_channels is None:
            selected_channels = [0, 1, 2]

        # Build list of all candidate positions
        all_positions: List[Tuple[int, int, int]] = []
        for r in range(height):
            for c in range(width):
                for ch in selected_channels:
                    all_positions.append((r, c, ch))

        # Optionally shuffle with password-derived seed
        if password:
            seed = int(hashlib.sha256(password.encode()).hexdigest()[:8], 16)
            rng = random.Random(seed)
            rng.shuffle(all_positions)

        end_index = start_index + positions_needed
        return all_positions[start_index:end_index]
    
    def _embed_data(self,
                    img_array: np.ndarray,
                    data: bytes,
                    positions: List[Tuple[int, int, int]],
                    bits: int) -> None:
        """Embed data bits into image array at specified positions. Supports 1 or 2 bits per position."""
        bit_mask = (1 << bits) - 1

        total_bits = len(data) * 8
        bit_ptr = 0

        for (row, col, channel_idx) in positions:
            if bit_ptr >= total_bits:
                break

            # Assemble up to `bits` bits from the data stream (MSB first)
            val = 0
            read = 0
            while read < bits and bit_ptr < total_bits:
                byte_idx = bit_ptr // 8
                bit_in_byte = 7 - (bit_ptr % 8)
                bit = (data[byte_idx] >> bit_in_byte) & 1
                val = (val << 1) | bit
                bit_ptr += 1
                read += 1

            # Pad remaining bits with zeros if we ran out
            if read < bits:
                val <<= (bits - read)

            # Clear LSBs and embed new bits
            img_array[row, col, channel_idx] &= ~bit_mask
            img_array[row, col, channel_idx] |= val & bit_mask
    
    def _extract_data(self,
                      img_array: np.ndarray,
                      positions: List[Tuple[int, int, int]],
                      bits: int,
                      length_bytes: int) -> bytes:
        """Extract data of given byte length from positions. Supports 1 or 2 bits per position."""
        bit_mask = (1 << bits) - 1
        total_bits_needed = length_bytes * 8
        bits_collected: List[int] = []

        for (row, col, channel_idx) in positions:
            if len(bits_collected) >= total_bits_needed:
                break
            pixel_value = img_array[row, col, channel_idx]
            val = pixel_value & bit_mask
            # Append `bits` bits (MSB first)
            for j in range(bits - 1, -1, -1):
                bits_collected.append((val >> j) & 1)
                if len(bits_collected) >= total_bits_needed:
                    break

        # Convert bits to bytes
        result = bytearray()
        for i in range(0, total_bits_needed, 8):
            byte_val = 0
            for j in range(8):
                bit = bits_collected[i + j]
                byte_val = (byte_val << 1) | bit
            result.append(byte_val)
        return bytes(result)

    def _get_channel_indices(self, channels: List[str]) -> List[int]:
        """Map channel names to indices."""
        channel_map = {'red': 0, 'green': 1, 'blue': 2}
        if not channels:
            return [0, 1, 2]
        return [channel_map[ch] for ch in channels if ch in channel_map]
    
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
