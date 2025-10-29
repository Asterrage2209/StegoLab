# StegoLab

Modern LSB steganography web app with a FastAPI backend and a React (Vite) frontend.

This updated version focuses on two core workflows:

- Embed data into lossless images (PNG/BMP)
- Extract embedded data from stego images

The previous Analyze and Demo pages have been removed from the UI to keep the experience simple and reliable.

## Tech stack

- Backend: FastAPI, Pillow, NumPy, Cryptography
- Frontend: React, Vite, Tailwind CSS, Axios

## Project structure

```
Assignment/StegoLab/
	backend/
		main.py           # FastAPI app and routes
		steganography.py  # LSB embed/extract engine
		analysis.py       # Steganalysis utilities (kept for experimentation)
		requirements.txt
	frontend/
		src/
			pages/
				Home.jsx      # Landing page
				Embed.jsx      # Embed workflow
				Extract.jsx    # Extract workflow
			utils/api.jsx    # Axios client
		vite.config.js     # Dev server proxy for /api
		package.json
	README.md
```

## Prerequisites

- Python 3.10+ recommended
- Node.js 18+ and npm

## Backend setup (Windows PowerShell)

```powershell
cd "D:\Programs\EHVA\Assignment\StegoLab\backend"

# Optional: create & activate venv
python -m venv venv
./venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Optional: allow custom CORS origins (comma-separated)
# $env:ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:5173"

# Run the API
python main.py
```

Backend runs on http://localhost:8000.

### API endpoints

- POST /api/embed
	- multipart/form-data: carrier_image (file), payload_text (string) OR payload_file (file), bits (1 or 2), channels (auto/red/green/blue), password (optional), encrypt (boolean)
	- returns base64 stego image and metrics

- POST /api/extract
	- multipart/form-data: image (file), bits, channels, password (optional), encrypt (boolean)
	- returns payload_text or payload_file (base64)

- GET /api/demo-images
	- simple list of demo image metadata (kept for compatibility; demo page was removed)

Note: There is also a POST /api/analyze endpoint left available for experimentation, but it is not exposed in the UI.

## Frontend setup (Windows PowerShell)

```powershell
cd "D:\Programs\EHVA\Assignment\StegoLab\frontend"

npm install

# Development server
npm run dev
```

By default, the frontend uses a relative base URL and Vite’s dev proxy (configured in `vite.config.js`) to forward `/api` requests to `http://localhost:8000`. This avoids CORS in development.

If you need to bypass the proxy and call the backend directly, set `VITE_API_BASE_URL` in `frontend/.env`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Usage

1) Embed
- Go to Embed page
- Upload a PNG/BMP image (carrier)
- Enter text or upload a file to hide
- Choose bits (1 or 2), channels (auto/red/green/blue)
- Optionally set a password and enable encryption
- Click “Embed Data” and download the stego image

2) Extract
- Go to Extract page
- Upload the stego image
- Use the exact same parameters used for embedding (bits, channels, password, encrypt)
- Click “Extract Data” to retrieve the payload

Tips:
- Use lossless formats (PNG, BMP)
- Bits and channels must match exactly for extraction
- If encryption was enabled, the same password must be provided for extraction

## Notes

- The Analyze and Demo pages were removed from the UI for a cleaner experience. The `analysis.py` module and `/api/analyze` endpoint remain for advanced users but are not part of the typical workflow.
- In development, prefer the Vite proxy (relative API base) to avoid CORS. If you do set `VITE_API_BASE_URL`, ensure the backend CORS list includes your frontend origin or set `ALLOWED_ORIGINS` on the backend.

## License

This project is for educational and research purposes. Use responsibly and according to applicable laws and regulations.
