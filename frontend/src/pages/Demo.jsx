import React, { useState, useEffect } from 'react';
import { Play, Download, Eye, Search, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import ImagePreview from '../components/ImagePreview';
import ResultCard from '../components/ResultCard';
import { getDemoImages, extractData, analyzeImage } from '../utils/api';

const Demo = () => {
  const [demoImages, setDemoImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [extractResult, setExtractResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  useEffect(() => {
    loadDemoImages();
  }, []);
  
  const loadDemoImages = async () => {
    try {
      const response = await getDemoImages();
      setDemoImages(response.demo_images || []);
    } catch (error) {
      console.error('Failed to load demo images:', error);
      toast.error('Failed to load demo images');
    }
  };
  
  const handleExtractDemo = async (imageName) => {
    setLoading(true);
    try {
      // For demo purposes, we'll use default parameters
      const formData = new FormData();
      
      // In a real implementation, you would load the actual demo image file
      // For now, we'll simulate the extraction
      const mockResult = {
        success: true,
        payload_text: "This is a demo message hidden in the image using LSB steganography!",
        payload_type: "text"
      };
      
      setExtractResult(mockResult);
      toast.success('Demo extraction completed!');
    } catch (error) {
      toast.error('Demo extraction failed');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAnalyzeDemo = async (imageName) => {
    setLoading(true);
    try {
      // For demo purposes, we'll simulate the analysis
      const mockResult = {
        confidence: 0.85,
        chi_square: {
          red: { p_value: 0.001, chi2_statistic: 45.2, suspicious: true },
          green: { p_value: 0.003, chi2_statistic: 38.7, suspicious: true },
          blue: { p_value: 0.012, chi2_statistic: 28.4, suspicious: true }
        },
        rs_score: {
          red: { rs_score: 0.15, suspicious: true },
          green: { rs_score: 0.12, suspicious: true },
          blue: { rs_score: 0.18, suspicious: true }
        },
        bitplane_stats: {
          red: { lsb_variance: 0.45, variance_ratio: 2.8, suspicious: true },
          green: { lsb_variance: 0.42, variance_ratio: 2.6, suspicious: true },
          blue: { lsb_variance: 0.48, variance_ratio: 3.1, suspicious: true }
        },
        explanation: "Strong evidence of steganographic content detected. Chi-square tests show significant deviation from expected LSB distribution across all color channels. RS analysis indicates potential LSB manipulation. Bit-plane analysis shows unusual noise patterns in the LSB plane. Most suspicious channels: RED, GREEN, BLUE."
      };
      
      setAnalysisResult(mockResult);
      toast.success('Demo analysis completed!');
    } catch (error) {
      toast.error('Demo analysis failed');
    } finally {
      setLoading(false);
    }
  };
  
  const demoSteps = [
    {
      title: 'Upload Cover Image',
      description: 'Select a PNG or BMP image',
      icon: Shield,
      color: 'text-blue-600 bg-blue-100'
    },
    {
      title: 'Add Payload',
      description: 'Enter text or upload file',
      icon: Download,
      color: 'text-green-600 bg-green-100'
    },
    {
      title: 'Configure Options',
      description: 'Set embedding parameters',
      icon: Play,
      color: 'text-purple-600 bg-purple-100'
    },
    {
      title: 'Download Result',
      description: 'Get your stego image',
      icon: Eye,
      color: 'text-orange-600 bg-orange-100'
    }
  ];
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Demo & Examples</h1>
        <p className="text-gray-600">
          Explore sample images and test the application features with pre-loaded examples
        </p>
      </div>
      
      {/* Demo Overview */}
      <div className="card mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">How StegoLab Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {demoSteps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="text-center">
                <div className={`w-16 h-16 rounded-2xl ${step.color} flex items-center justify-center mx-auto mb-4`}>
                  <Icon className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-600 text-sm">{step.description}</p>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Demo Images */}
      <div className="card mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Sample Images</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {demoImages.map((image, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{image.name}</h3>
                  <p className="text-gray-600 text-sm">{image.description}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  image.type === 'cover' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {image.type}
                </div>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={() => setSelectedImage(image)}
                  className="w-full btn-secondary flex items-center justify-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>Preview Image</span>
                </button>
                
                {image.type === 'stego' && (
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleExtractDemo(image.name)}
                      disabled={loading}
                      className="btn-primary text-sm disabled:opacity-50"
                    >
                      Extract Data
                    </button>
                    <button
                      onClick={() => handleAnalyzeDemo(image.name)}
                      disabled={loading}
                      className="btn-secondary text-sm disabled:opacity-50"
                    >
                      Analyze
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Demo Results */}
      {(extractResult || analysisResult) && (
        <div className="card">
          <div className="flex space-x-1 mb-6">
            <button
              onClick={() => setActiveTab('extract')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                activeTab === 'extract' 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Extraction Results
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                activeTab === 'analysis' 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Analysis Results
            </button>
          </div>
          
          {activeTab === 'extract' && extractResult && (
            <ResultCard
              result={extractResult}
              type="extract"
            />
          )}
          
          {activeTab === 'analysis' && analysisResult && (
            <ResultCard
              result={analysisResult}
              type="analyze"
            />
          )}
        </div>
      )}
      
      {/* Try It Yourself */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Try It Yourself?</h3>
          <p className="text-gray-600 mb-6">
            Now that you've seen how StegoLab works, try embedding your own data or analyzing your own images.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/embed"
              className="btn-primary flex items-center justify-center space-x-2"
            >
              <Shield className="w-4 h-4" />
              <span>Embed Data</span>
            </a>
            <a
              href="/extract"
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <Eye className="w-4 h-4" />
              <span>Extract Data</span>
            </a>
            <a
              href="/analyze"
              className="btn-secondary flex items-center justify-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Analyze Image</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Demo;
