import React, { useState } from 'react';
import { Shield, Upload, Settings, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import FileUploader from '../components/FileUploader';
import ImagePreview from '../components/ImagePreview';
import StepsWizard from '../components/StepsWizard';
import OptionPanel from '../components/OptionPanel';
import ResultCard from '../components/ResultCard';
import { embedData } from '../utils/api';

const Embed = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [carrierImage, setCarrierImage] = useState(null);
  const [payloadText, setPayloadText] = useState('');
  const [payloadFile, setPayloadFile] = useState(null);
  const [options, setOptions] = useState({
    bits: 1,
    channels: 'auto',
    password: '',
    encrypt: false,
    sequential: false,
    headerFormat: 'standard'
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const steps = [
    { title: 'Upload Image', description: 'Select carrier image' },
    { title: 'Add Payload', description: 'Text or file to hide' },
    { title: 'Configure', description: 'Set options' },
    { title: 'Embed', description: 'Process & download' }
  ];
  
  const handleCarrierImageSelect = (file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCarrierImage(e.target.result);
        setCurrentStep(1);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handlePayloadFileSelect = (file) => {
    setPayloadFile(file);
  };
  
  const handleEmbed = async () => {
    if (!carrierImage) {
      toast.error('Please select a carrier image');
      return;
    }
    
    if (!payloadText && !payloadFile) {
      toast.error('Please provide text or file to embed');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      
      // Convert base64 image to blob
      const response = await fetch(carrierImage);
      const blob = await response.blob();
      formData.append('carrier_image', blob, 'carrier.png');
      
      if (payloadText) {
        formData.append('payload_text', payloadText);
      }
      
      if (payloadFile) {
        formData.append('payload_file', payloadFile);
      }
      
      formData.append('bits', options.bits);
      formData.append('channels', options.channels);
      if (options.password) {
        formData.append('password', options.password);
      }
      formData.append('encrypt', options.encrypt);
      
      const result = await embedData(formData);
      setResult(result);
      setCurrentStep(3);
      toast.success('Data embedded successfully!');
    } catch (error) {
      toast.error(error.message || 'Failed to embed data');
      console.error('Embed error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownload = (imageData) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${imageData}`;
    link.download = 'stego_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  const canProceedToStep = (step) => {
    switch (step) {
      case 1:
        return carrierImage !== null;
      case 2:
        return carrierImage !== null && (payloadText || payloadFile);
      case 3:
        return carrierImage !== null && (payloadText || payloadFile);
      default:
        return true;
    }
  };
  
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Shield className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Carrier Image</h2>
              <p className="text-gray-600">
                Select a PNG or BMP image to use as the carrier for hiding your data
              </p>
            </div>
            
            <FileUploader
              onFileSelect={handleCarrierImageSelect}
              acceptedTypes={['image/png', 'image/bmp']}
              maxSize={5 * 1024 * 1024}
              placeholder="Drag & drop your carrier image here, or click to select"
            />
            
            {carrierImage && (
              <ImagePreview
                image={carrierImage}
                title="Carrier Image Preview"
                showInfo={true}
              />
            )}
          </div>
        );
        
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Upload className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Add Payload Data</h2>
              <p className="text-gray-600">
                Enter text or upload a file to hide in the carrier image
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Text Payload</h3>
                <textarea
                  value={payloadText}
                  onChange={(e) => setPayloadText(e.target.value)}
                  placeholder="Enter text to hide..."
                  className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                />
                <p className="text-sm text-gray-500 mt-2">
                  {payloadText.length} characters ({new Blob([payloadText]).size} bytes)
                </p>
              </div>
              
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">File Payload</h3>
                <FileUploader
                  onFileSelect={handlePayloadFileSelect}
                  acceptedTypes={['*/*']}
                  maxSize={1024 * 1024} // 1MB for files
                  placeholder="Drag & drop a file here, or click to select"
                />
                {payloadFile && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-900">{payloadFile.name}</p>
                    <p className="text-xs text-gray-500">
                      {(payloadFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Settings className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Configure Options</h2>
              <p className="text-gray-600">
                Adjust embedding parameters for optimal results
              </p>
            </div>
            
            <OptionPanel
              options={options}
              onChange={setOptions}
            />
          </div>
        );
        
      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Embedding Complete</h2>
              <p className="text-gray-600">
                Your data has been successfully hidden in the image
              </p>
            </div>
            
            {result && (
              <ResultCard
                result={result}
                type="embed"
                onDownload={handleDownload}
              />
            )}
          </div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Embed Data</h1>
        <p className="text-gray-600">
          Hide text or files inside images using LSB steganography
        </p>
      </div>
      
      <StepsWizard
        steps={steps}
        currentStep={currentStep}
        onStepClick={(step) => {
          if (canProceedToStep(step)) {
            setCurrentStep(step);
          }
        }}
        className="mb-8"
      />
      
      <div className="card">
        {renderStepContent()}
      </div>
      
      {/* Navigation Buttons */}
      <div className="flex justify-between mt-8">
        <button
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        {currentStep < 2 && (
          <button
            onClick={() => setCurrentStep(currentStep + 1)}
            disabled={!canProceedToStep(currentStep + 1)}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        )}
        
        {currentStep === 2 && (
          <button
            onClick={handleEmbed}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>}
            <span>{loading ? 'Embedding...' : 'Embed Data'}</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default Embed;
