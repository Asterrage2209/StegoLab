"""
Data models for StegoLab API.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64

class EmbedRequest(BaseModel):
    """Request model for embedding data."""
    carrier_image: str  # base64 encoded image
    payload_text: Optional[str] = None
    payload_file: Optional[str] = None  # base64 encoded file
    bits: int = 1
    channels: str = "auto"
    password: Optional[str] = None
    encrypt: bool = False

class ExtractRequest(BaseModel):
    """Request model for extracting data."""
    image: str  # base64 encoded image
    password: Optional[str] = None
    bits: int = 1
    channels: str = "auto"
    encrypt: bool = False

class EmbedResult(BaseModel):
    """Result model for embedding operation."""
    success: bool
    stego_image: str  # base64 encoded stego image
    metrics: Dict[str, Any]
    message: Optional[str] = None

class ExtractResult(BaseModel):
    """Result model for extraction operation."""
    success: bool
    payload_text: Optional[str] = None
    payload_file: Optional[str] = None  # base64 encoded file
    message: Optional[str] = None

class AnalysisResult(BaseModel):
    """Result model for steganalysis."""
    confidence: float  # 0-1 confidence score
    chi_square: float
    rs_score: float
    bitplane_stats: Dict[str, Any]
    visualizations: Dict[str, str]  # base64 encoded images
    explanation: str
