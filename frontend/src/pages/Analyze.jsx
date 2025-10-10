import React, { useState } from 'react';
import { Search, Upload, BarChart3, Eye, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import FileUploader from '../components/FileUploader';
import ImagePreview from '../components/ImagePreview';
import ResultCard from '../components/ResultCard';
import { analyzeImage } from '../utils/api';

const Analyze = () => {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleImageSelect = (file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleAnalyze = async () => {
    if (!image) {
      toast.error('Please select an image to analyze');
      return;
    }
    
    setLoading(true);
    try {
      const formData = new FormData();
      
      // Convert base64 image to blob
      const response = await fetch(image);
      const blob = await response.blob();
      formData.append('image', blob, 'analyze.png');
      
      const result = await analyzeImage(formData);
      setResult(result);
      toast.success('Analysis completed successfully!');
    } catch (error) {
      toast.error(error.message || 'Failed to analyze image');
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const getConfidenceColor = (confidence) => {
    if (confidence > 0.7) return 'text-red-600';
    if (confidence > 0.4) return 'text-yellow-600';
    return 'text-green-600';
  };
  
  const getConfidenceText = (confidence) => {
    if (confidence > 0.7) return 'High Risk - Likely contains steganographic content';
    if (confidence > 0.4) return 'Medium Risk - Possible steganographic content';
    return 'Low Risk - No significant steganographic indicators';
  };
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analyze Image</h1>
        <p className="text-gray-600">
          Detect potential steganographic content using statistical analysis and visual inspection
        </p>
      </div>
      
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Image Upload and Preview */}
        <div className="space-y-6">
          <div className="card">
            <div className="text-center mb-6">
              <Search className="w-12 h-12 text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Image to Analyze</h2>
              <p className="text-gray-600">
                Select an image to check for steganographic content
              </p>
            </div>
            
            <FileUploader
              onFileSelect={handleImageSelect}
              acceptedTypes={['image/png', 'image/bmp', 'image/jpeg']}
              maxSize={5 * 1024 * 1024}
              placeholder="Drag & drop your image here, or click to select"
            />
            
            {image && (
              <ImagePreview
                image={image}
                title="Image Preview"
                showInfo={true}
                className="mt-6"
              />
            )}
            
            <button
              onClick={handleAnalyze}
              disabled={!image || loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 mt-6"
            >
              {loading && <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>}
              <span>{loading ? 'Analyzing...' : 'Analyze Image'}</span>
            </button>
          </div>
        </div>
        
        {/* Right Column - Analysis Results */}
        <div className="space-y-6">
          {result ? (
            <>
              {/* Main Result Card */}
              <ResultCard
                result={result}
                type="analyze"
              />
              
              {/* Detailed Analysis */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Detailed Analysis
                </h3>
                
                {/* Chi-Square Results */}
                {result.chi_square && (
                  <div className="mb-6">
                    <h4 className="text-md font-medium text-gray-700 mb-3">Chi-Square Test Results</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {Object.entries(result.chi_square).map(([channel, data]) => (
                        <div key={channel} className={`p-3 rounded-lg border ${
                          data.suspicious ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
                        }`}>
                          <div className="text-center">
                            <div className="font-semibold text-gray-900 mb-1">
                              {channel.toUpperCase()}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              p-value: {data.p_value?.toFixed(4) || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              χ²: {data.chi2_statistic?.toFixed(2) || 'N/A'}
                            </div>
                            <div className={`text-xs font-medium ${
                              data.suspicious ? 'text-red-700' : 'text-green-700'
                            }`}>
                              {data.suspicious ? 'Suspicious' : 'Normal'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* RS Analysis Results */}
                {result.rs_score && (
                  <div className="mb-6">
                    <h4 className="text-md font-medium text-gray-700 mb-3">RS Analysis Results</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {Object.entries(result.rs_score).map(([channel, data]) => (
                        <div key={channel} className={`p-3 rounded-lg border ${
                          data.suspicious ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
                        }`}>
                          <div className="text-center">
                            <div className="font-semibold text-gray-900 mb-1">
                              {channel.toUpperCase()}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              RS Score: {data.rs_score?.toFixed(3) || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              Regular: {data.regular_pairs || 'N/A'}
                            </div>
                            <div className={`text-xs font-medium ${
                              data.suspicious ? 'text-red-700' : 'text-green-700'
                            }`}>
                              {data.suspicious ? 'Suspicious' : 'Normal'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Bit-plane Analysis */}
                {result.bitplane_stats && (
                  <div className="mb-6">
                    <h4 className="text-md font-medium text-gray-700 mb-3">Bit-plane Analysis</h4>
                    <div className="grid grid-cols-3 gap-3">
                      {Object.entries(result.bitplane_stats).map(([channel, data]) => (
                        <div key={channel} className={`p-3 rounded-lg border ${
                          data.suspicious ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
                        }`}>
                          <div className="text-center">
                            <div className="font-semibold text-gray-900 mb-1">
                              {channel.toUpperCase()}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              LSB Var: {data.lsb_variance?.toFixed(4) || 'N/A'}
                            </div>
                            <div className="text-sm text-gray-600 mb-1">
                              Ratio: {data.variance_ratio?.toFixed(2) || 'N/A'}
                            </div>
                            <div className={`text-xs font-medium ${
                              data.suspicious ? 'text-red-700' : 'text-green-700'
                            }`}>
                              {data.suspicious ? 'Suspicious' : 'Normal'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Visualizations */}
              {result.visualizations && (
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Eye className="w-5 h-5 mr-2" />
                    Visual Analysis
                  </h3>
                  
                  <div className="space-y-4">
                    {/* LSB Histogram */}
                    {result.visualizations.lsb_histogram && (
                      <div>
                        <h4 className="text-md font-medium text-gray-700 mb-2">LSB Distribution</h4>
                        <img
                          src={`data:image/png;base64,${result.visualizations.lsb_histogram}`}
                          alt="LSB Histogram"
                          className="w-full rounded-lg border"
                        />
                      </div>
                    )}
                    
                    {/* Bit-plane Visualizations */}
                    {Object.entries(result.visualizations)
                      .filter(([key]) => key.includes('bitplanes'))
                      .map(([channel, data]) => (
                        <div key={channel}>
                          <h4 className="text-md font-medium text-gray-700 mb-2">
                            {channel.replace('_bitplanes', '').toUpperCase()} Channel Bit-planes
                          </h4>
                          <img
                            src={`data:image/png;base64,${data}`}
                            alt={`${channel} Bit-planes`}
                            className="w-full rounded-lg border"
                          />
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="card text-center py-12">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Results</h3>
              <p className="text-gray-500">
                Upload an image and click "Analyze Image" to see steganalysis results
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Analysis Methods Info */}
      <div className="card mt-8 bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Methods</h3>
        <div className="grid md:grid-cols-3 gap-6 text-sm">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Chi-Square Test</h4>
            <p className="text-gray-600">
              Analyzes the distribution of LSB values. Natural images should have roughly equal 
              numbers of 0s and 1s in the LSB plane.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">RS Analysis</h4>
            <p className="text-gray-600">
              Examines sample pairs and their relationships. LSB steganography can create 
              detectable patterns in pixel pair statistics.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Bit-plane Analysis</h4>
            <p className="text-gray-600">
              Compares noise patterns across different bit-planes. The LSB plane should 
              have different statistical properties than higher bit-planes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analyze;
