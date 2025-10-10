import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Download, Info } from 'lucide-react';

const ImagePreview = ({ 
  image, 
  title = "Image Preview", 
  showInfo = true, 
  downloadable = false,
  onDownload = null,
  className = ""
}) => {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [showImageInfo, setShowImageInfo] = useState(false);
  
  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.25, 0.5));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else if (image) {
      const link = document.createElement('a');
      link.href = image;
      link.download = 'image.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };
  
  const getImageInfo = () => {
    if (!image) return null;
    
    const img = new Image();
    img.src = image;
    
    return {
      width: img.naturalWidth || 'Unknown',
      height: img.naturalHeight || 'Unknown',
      size: image.length ? `${Math.round(image.length / 1024)} KB` : 'Unknown'
    };
  };
  
  const imageInfo = getImageInfo();
  
  return (
    <div className={`card ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          {showInfo && imageInfo && (
            <button
              onClick={() => setShowImageInfo(!showImageInfo)}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200"
              title="Image Information"
            >
              <Info className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={handleZoomOut}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-600 min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleRotate}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200"
            title="Rotate"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          {downloadable && (
            <button
              onClick={handleDownload}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors duration-200"
              title="Download"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      {showImageInfo && imageInfo && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Width:</span>
              <span className="ml-2 font-medium">{imageInfo.width}px</span>
            </div>
            <div>
              <span className="text-gray-600">Height:</span>
              <span className="ml-2 font-medium">{imageInfo.height}px</span>
            </div>
            <div>
              <span className="text-gray-600">Size:</span>
              <span className="ml-2 font-medium">{imageInfo.size}</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="relative overflow-hidden rounded-lg bg-gray-100">
        {image ? (
          <div className="flex items-center justify-center min-h-[200px]">
            <img
              src={image}
              alt={title}
              className="max-w-full max-h-[400px] object-contain transition-transform duration-200"
              style={{
                transform: `scale(${zoom}) rotate(${rotation}deg)`
              }}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center min-h-[200px] text-gray-500">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-2 bg-gray-200 rounded-lg flex items-center justify-center">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-sm">No image selected</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImagePreview;
