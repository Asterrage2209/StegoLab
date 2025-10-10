import React, { useState } from 'react';
import { Eye, Upload, Download, Key } from 'lucide-react';
import toast from 'react-hot-toast';
import FileUploader from '../components/FileUploader';
import ImagePreview from '../components/ImagePreview';
import ResultCard from '../components/ResultCard';
import { extractData } from '../utils/api';

const Extract = () => {
  const [stegoImage, setStegoImage] = useState(null);
  const [extractOptions, setExtractOptions] = useState({
    bits: 1,
    channels: 'auto',
    password: '',
    encrypt: false
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleImageSelect = (file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setStegoImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleExtract = async () => {
    if (!stegoImage) {
      toast.error('Please select a stego image');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      
      // Convert base64 image to blob
      const response = await fetch(stegoImage);
      const blob = await response.blob();
      formData.append('image', blob, 'stego.png');
      
      formData.append('bits', extractOptions.bits);
      formData.append('channels', extractOptions.channels);
      if (extractOptions.password) {
        formData.append('password', extractOptions.password);
      }
      formData.append('encrypt', extractOptions.encrypt);
      
      const result = await extractData(formData);
      setResult(result);
      toast.success('Data extracted successfully!');
    } catch (error) {
      toast.error(error.message || 'Failed to extract data');
      console.error('Extract error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownload = (data, filename = 'extracted_data') => {
    const link = document.createElement('a');
    link.href = `data:application/octet-stream;base64,${data}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Extract Data</h1>
        <p className="text-gray-600">
          Retrieve hidden data from stego images using the correct parameters
        </p>
      </div>
      
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Image Upload and Preview */}
        <div className="space-y-6">
          <div className="card">
            <div className="text-center mb-6">
              <Eye className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Stego Image</h2>
              <p className="text-gray-600">
                Select the image containing hidden data
              </p>
            </div>
            
            <FileUploader
              onFileSelect={handleImageSelect}
              acceptedTypes={['image/png', 'image/bmp', 'image/jpeg']}
              maxSize={5 * 1024 * 1024}
              placeholder="Drag & drop your stego image here, or click to select"
            />
            
            {stegoImage && (
              <ImagePreview
                image={stegoImage}
                title="Stego Image Preview"
                showInfo={true}
                className="mt-6"
              />
            )}
          </div>
        </div>
        
        {/* Right Column - Extraction Options and Results */}
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center space-x-2 mb-6">
              <Key className="w-5 h-5 text-gray-600" />
              <h2 className="text-xl font-bold text-gray-900">Extraction Parameters</h2>
            </div>
            
            <div className="space-y-4">
              {/* Bits per channel */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bits per Channel
                </label>
                <div className="flex space-x-4">
                  {[1, 2].map((bits) => (
                    <label key={bits} className="flex items-center">
                      <input
                        type="radio"
                        name="bits"
                        value={bits}
                        checked={extractOptions.bits === bits}
                        onChange={(e) => setExtractOptions({
                          ...extractOptions,
                          bits: parseInt(e.target.value)
                        })}
                        className="mr-2 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">{bits} LSB</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Color channels */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Color Channels
                </label>
                <select
                  value={extractOptions.channels}
                  onChange={(e) => setExtractOptions({
                    ...extractOptions,
                    channels: e.target.value
                  })}
                  className="input-field"
                >
                  <option value="auto">Auto (All channels)</option>
                  <option value="red">Red channel only</option>
                  <option value="green">Green channel only</option>
                  <option value="blue">Blue channel only</option>
                </select>
              </div>
              
              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password (if used during embedding)
                </label>
                <input
                  type="password"
                  value={extractOptions.password}
                  onChange={(e) => setExtractOptions({
                    ...extractOptions,
                    password: e.target.value
                  })}
                  placeholder="Enter password used during embedding"
                  className="input-field"
                />
              </div>
              
              {/* Encryption */}
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={extractOptions.encrypt}
                    onChange={(e) => setExtractOptions({
                      ...extractOptions,
                      encrypt: e.target.checked
                    })}
                    className="mr-2 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Payload was encrypted during embedding
                  </span>
                </label>
              </div>
              
              {/* Extract Button */}
              <button
                onClick={handleExtract}
                disabled={!stegoImage || loading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading && <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>}
                <span>{loading ? 'Extracting...' : 'Extract Data'}</span>
              </button>
            </div>
          </div>
          
          {/* Results */}
          {result && (
            <ResultCard
              result={result}
              type="extract"
              onDownload={handleDownload}
            />
          )}
        </div>
      </div>
      
      {/* Help Section */}
      <div className="card mt-8 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Extraction Tips</h3>
        <div className="text-blue-800 space-y-2">
          <p>• Make sure you have the correct parameters used during embedding</p>
          <p>• If a password was used, enter it exactly as it was during embedding</p>
          <p>• Check the "encrypt" option if the payload was encrypted</p>
          <p>• Try different channel combinations if extraction fails</p>
          <p>• The number of LSBs must match what was used during embedding</p>
        </div>
      </div>
    </div>
  );
};

export default Extract;
