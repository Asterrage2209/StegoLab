# StegoLab Architecture Documentation

## System Overview

StegoLab is a full-stack web application built with a microservices architecture, consisting of a React frontend and a FastAPI backend. The system implements LSB (Least Significant Bit) steganography for data hiding and statistical steganalysis for detection.

## Architecture Diagram

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend │ ◄─────────────► │  FastAPI Backend │
│   (Port 3000)    │                 │   (Port 8000)    │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                 ┌─────────────────┐
│   Static Assets │                 │  Steganography  │
│   (Images, CSS) │                 │     Engine      │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ Steganalysis    │
                                    │     Engine      │
                                    └─────────────────┘
```

## Frontend Architecture

### Technology Stack
- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing for SPA navigation
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: HTTP client for API communication
- **React Dropzone**: File upload handling
- **React Hot Toast**: User notification system

### Component Structure
```
src/
├── components/           # Reusable UI components
│   ├── Navbar.js        # Navigation component
│   ├── FileUploader.js  # File upload with drag & drop
│   ├── ImagePreview.js  # Image display with controls
│   ├── StepsWizard.js   # Multi-step process wizard
│   ├── OptionPanel.js   # Configuration options
│   └── ResultCard.js    # Results display
├── pages/               # Main application pages
│   ├── Home.js          # Landing page with overview
│   ├── Embed.js         # Data embedding interface
│   ├── Extract.js       # Data extraction interface
│   ├── Analyze.js       # Image analysis interface
│   └── Demo.js          # Demo and examples
├── utils/               # Utility functions
│   └── api.js          # API client and endpoints
└── styles/             # Styling and themes
    └── index.css       # Global styles and Tailwind
```

### State Management
- **Local State**: React hooks (useState, useEffect) for component state
- **Form State**: Controlled components with local state
- **API State**: Axios interceptors for request/response handling
- **Error Handling**: React Hot Toast for user notifications

## Backend Architecture

### Technology Stack
- **FastAPI**: Modern Python web framework with automatic API documentation
- **Pydantic**: Data validation and serialization
- **Pillow**: Python Imaging Library for image processing
- **NumPy**: Numerical computing for array operations
- **OpenCV**: Computer vision library for advanced image processing
- **scikit-image**: Image processing algorithms
- **cryptography**: Secure encryption and hashing

### Core Modules

#### 1. Steganography Engine (`steganography.py`)
```python
class SteganographyEngine:
    def embed(carrier_path, payload_data, bits, channels, password, encrypt)
    def extract(stego_path, bits, channels, password, encrypt)
    def _calculate_capacity(img, bits, num_channels)
    def _create_payload_with_header(payload_data, encrypt, password)
    def _generate_embedding_positions(img_shape, data_length, password)
    def _embed_data(img_array, data, positions, bits, channels)
    def _extract_data(img_array, positions, bits, channels, length)
    def _encrypt_payload(payload, password)
    def _decrypt_payload(encrypted_payload, password)
```

**Key Features:**
- Header-based payload management (16-byte header with magic, length, CRC32)
- Support for 1-2 LSBs per channel
- Password-based position permutation
- AES-GCM encryption for payload security
- Capacity calculation and validation
- PSNR and SSIM quality metrics

#### 2. Steganalysis Engine (`analysis.py`)
```python
class SteganalysisEngine:
    def analyze(image_path)
    def _chi_square_test(img_array)
    def _rs_analysis(img_array)
    def _bitplane_analysis(img_array)
    def _generate_visualizations(img_array)
    def _calculate_confidence(chi_square_results, rs_results, bitplane_results)
    def _generate_explanation(chi_square_results, rs_results, bitplane_results, confidence)
```

**Detection Methods:**
- **Chi-Square Test**: Analyzes LSB distribution for statistical anomalies
- **RS Analysis**: Examines sample pairs for LSB manipulation patterns
- **Bit-plane Analysis**: Compares noise variance across bit-planes
- **Visual Analysis**: Generates histograms and bit-plane visualizations

#### 3. API Layer (`main.py`)
```python
# REST API Endpoints
POST /api/embed      # Embed data into image
POST /api/extract    # Extract data from image
POST /api/analyze    # Analyze image for steganography
GET  /api/demo-images # Get demo image list
```

**Request/Response Flow:**
1. **File Upload**: Multipart form data with image and parameters
2. **Validation**: Input validation and file type checking
3. **Processing**: Core algorithm execution
4. **Response**: JSON with results and base64-encoded images
5. **Cleanup**: Temporary file removal

## Data Flow

### Embedding Process
1. **Frontend**: User uploads carrier image and payload
2. **API**: Validates inputs and creates FormData
3. **Engine**: Calculates capacity and validates payload size
4. **Processing**: Creates header, encrypts if needed, embeds data
5. **Response**: Returns stego image and quality metrics
6. **Frontend**: Displays results and download link

### Extraction Process
1. **Frontend**: User uploads stego image with parameters
2. **API**: Validates inputs and extracts parameters
3. **Engine**: Reads header, validates magic bytes and CRC32
4. **Processing**: Extracts data, decrypts if needed
5. **Response**: Returns extracted payload (text or binary)
6. **Frontend**: Displays extracted content or download link

### Analysis Process
1. **Frontend**: User uploads image for analysis
2. **API**: Validates image format and size
3. **Engine**: Runs statistical detectors (chi-square, RS, bit-plane)
4. **Processing**: Generates visualizations and confidence score
5. **Response**: Returns analysis results and visualization images
6. **Frontend**: Displays confidence score and detailed analysis

## Security Architecture

### Input Validation
- **File Type Validation**: Only PNG/BMP for embedding, JPEG allowed for analysis
- **File Size Limits**: 5MB maximum for uploaded files
- **Parameter Validation**: Pydantic models for request validation
- **Path Traversal Protection**: Secure file handling and temporary directories

### Data Protection
- **Temporary Files**: Automatic cleanup after processing
- **Password Security**: PBKDF2 key derivation with salt
- **Encryption**: AES-GCM for payload encryption
- **Error Handling**: Secure error messages without information leakage

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Considerations

### Image Processing
- **Memory Management**: Efficient NumPy array operations
- **Batch Processing**: Process multiple channels simultaneously
- **Optimization**: Vectorized operations for large images
- **Caching**: Temporary file management for large uploads

### API Performance
- **Async Operations**: FastAPI async/await for I/O operations
- **Timeout Handling**: 30-second timeout for file operations
- **Error Recovery**: Graceful handling of processing failures
- **Resource Cleanup**: Automatic cleanup of temporary resources

## Deployment Architecture

### Docker Configuration
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

### Container Strategy
- **Multi-stage Builds**: Optimized Docker images
- **Layer Caching**: Efficient dependency installation
- **Health Checks**: Container health monitoring
- **Volume Mounting**: Development-friendly volume mounts

## Scalability Considerations

### Horizontal Scaling
- **Stateless Backend**: No session state, supports multiple instances
- **Load Balancing**: Can be deployed behind reverse proxy
- **Database**: Currently file-based, can be extended to database storage
- **Caching**: Can add Redis for session and result caching

### Performance Optimization
- **Image Compression**: Optimize image sizes for web delivery
- **CDN Integration**: Static asset delivery through CDN
- **API Rate Limiting**: Implement rate limiting for production
- **Monitoring**: Add application performance monitoring

## Error Handling Strategy

### Frontend Error Handling
- **API Errors**: Axios interceptors for consistent error handling
- **User Feedback**: Toast notifications for user-friendly messages
- **Validation**: Client-side validation before API calls
- **Fallbacks**: Graceful degradation for failed operations

### Backend Error Handling
- **HTTP Exceptions**: FastAPI HTTPException for API errors
- **Validation Errors**: Pydantic validation with detailed error messages
- **Processing Errors**: Try-catch blocks with specific error types
- **Logging**: Structured logging for debugging and monitoring

## Testing Strategy

### Unit Tests
- **Steganography Engine**: Embed/extract roundtrip tests
- **Analysis Engine**: Statistical detector validation
- **API Endpoints**: Request/response validation
- **Error Cases**: Edge cases and error conditions

### Integration Tests
- **End-to-End**: Complete user workflows
- **API Integration**: Frontend-backend communication
- **File Processing**: Image upload and processing
- **Security**: Input validation and error handling

### Test Data
- **Sample Images**: Various sizes and formats for testing
- **Test Payloads**: Text and binary data for embedding
- **Edge Cases**: Large files, invalid inputs, error conditions
- **Performance**: Load testing with multiple concurrent requests

## Future Enhancements

### Algorithm Improvements
- **DCT Steganography**: JPEG-compatible steganography
- **Advanced Encryption**: Additional encryption algorithms
- **Steganalysis**: Machine learning-based detection
- **Compression**: Payload compression before embedding

### Feature Additions
- **Batch Processing**: Multiple file processing
- **User Accounts**: Authentication and user management
- **History**: Processing history and result storage
- **API Keys**: Rate limiting and usage tracking

### Performance Optimizations
- **GPU Acceleration**: CUDA support for image processing
- **Distributed Processing**: Multi-node processing for large files
- **Caching**: Result caching and optimization
- **CDN**: Global content delivery network
