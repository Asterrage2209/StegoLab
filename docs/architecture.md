# StegoLab Architecture Documentation

## System Overview

StegoLab is a full-stack web application with a React (Vite) frontend and a FastAPI backend. It implements LSB (Least Significant Bit) steganography for data hiding and extraction. The previous Analyze and Demo pages have been removed from the UI to streamline the experience. A steganalysis module remains in the backend for experimentation but is not exposed in the UI.

## Architecture Diagram

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   React Frontend │ ◄─────────────► │  FastAPI Backend │
│   (Port 3000)    │                 │   (Port 8000)    │
┌─────────────────┐                 └─────────────────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │ Steganalysis    │
                                   │     Engine      │
                                   └─────────────────┘
                                    (backend only; experimental)
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
- React 18 (functional components with hooks)
- React Router
- Tailwind CSS
- Axios
- React Dropzone
- React Hot Toast
- Vite (dev server and build)

### Component Structure
```
src/
├── components/             # Reusable UI components
│   ├── Navbar.jsx         # Navigation component
│   ├── FileUploader.jsx   # File upload with drag & drop
│   ├── ImagePreview.jsx   # Image display with controls
│   ├── StepsWizard.jsx    # Multi-step process wizard (used in Embed)
│   ├── OptionPanel.jsx    # Configuration options
│   └── ResultCard.jsx     # Results display
├── pages/                  # Main application pages
│   ├── Home.jsx           # Landing page
│   ├── Embed.jsx          # Data embedding interface
│   └── Extract.jsx        # Data extraction interface
├── utils/
│   └── api.jsx            # Axios client and endpoints
└── styles/
  └── index.css          # Global styles and Tailwind
```

### State Management
- **Local State**: React hooks (useState, useEffect) for component state
- **Form State**: Controlled components with local state
- **API State**: Axios interceptors for request/response handling
- **Error Handling**: React Hot Toast for user notifications

## Backend Architecture

### Technology Stack
- FastAPI
- Pydantic
- Pillow, NumPy
- OpenCV, scikit-image (for analysis utilities)
- cryptography (Fernet encryption; PBKDF2 key derivation)

### Core Modules

#### 1. Steganography Engine (`steganography.py`)
```python
class SteganographyEngine:
  def embed(carrier_path, payload_data, bits, channels, password, encrypt)
  def extract(stego_path, bits, channels, password, encrypt)
  def _calculate_capacity(img, bits, num_channels)
  def _create_payload_with_header(payload_data, plaintext_crc32=None)
  def _generate_embedding_positions(img_shape, positions_needed, password, selected_channels, start_index)
  def _embed_data(img_array, data, positions, bits)
  def _extract_data(img_array, positions, bits, length_bytes)
  def _encrypt_payload(payload, password)
  def _decrypt_payload(encrypted_payload, password)
```

**Key Features:**
- 16-byte header (magic, length, CRC32, reserved)
- 1–2 LSBs per selected channel (R/G/B)
- Optional password-based position permutation (deterministic shuffle)
- Encryption via Fernet (AES + HMAC with PBKDF2-derived key); header remains plaintext
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

Note: The steganalysis module is retained for experimentation and is not used in the current UI.

**Detection Methods (experimental):**
- Chi-Square Test
- RS Analysis
- Bit-plane Analysis and visualization

#### 3. API Layer (`main.py`)
```python
# REST API Endpoints
POST /api/embed      # Embed data into image
POST /api/extract    # Extract data from image
GET  /api/demo-images # Get demo image list
POST /api/analyze    # Experimental: analyze image (not used by UI)
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

### Analysis Process (experimental, backend only)
1. API receives image
2. Engine runs detectors and builds visualizations
3. Response returns stats and base64 images (not displayed in UI)

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
allowed_origins = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost:5173",
  "http://127.0.0.1:5173",
]

env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
  allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
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

### Docker Configuration (example)
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
      - VITE_API_BASE_URL=http://localhost:8000
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
