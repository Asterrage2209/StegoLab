import React from 'react';
import { Download, CheckCircle, XCircle, Info, BarChart3 } from 'lucide-react';

const ResultCard = ({ 
  result, 
  type = 'embed', // 'embed', 'extract', 'analyze'
  onDownload = null,
  className = ""
}) => {
  const getStatusIcon = () => {
    if (result.success) {
      return <CheckCircle className="w-6 h-6 text-green-500" />;
    }
    return <XCircle className="w-6 h-6 text-red-500" />;
  };
  
  const getStatusText = () => {
    if (result.success) {
      switch (type) {
        case 'embed':
          return 'Data embedded successfully';
        case 'extract':
          return 'Data extracted successfully';
        case 'analyze':
          return 'Analysis completed';
        default:
          return 'Operation completed successfully';
      }
    }
    return result.message || 'Operation failed';
  };
  
  const getStatusColor = () => {
    if (result.success) {
      return 'text-green-600 bg-green-50 border-green-200';
    }
    return 'text-red-600 bg-red-50 border-red-200';
  };
  
  const renderEmbedResult = () => (
    <div className="space-y-4">
      {result.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-primary-600">
              {result.metrics.payload_size || 0}
            </div>
            <div className="text-xs text-gray-600">Bytes Embedded</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {result.metrics.psnr ? result.metrics.psnr.toFixed(2) : 'N/A'}
            </div>
            <div className="text-xs text-gray-600">PSNR (dB)</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {result.metrics.ssim ? result.metrics.ssim.toFixed(3) : 'N/A'}
            </div>
            <div className="text-xs text-gray-600">SSIM</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {result.metrics.embedding_efficiency ? 
                (result.metrics.embedding_efficiency * 100).toFixed(1) + '%' : 'N/A'}
            </div>
            <div className="text-xs text-gray-600">Efficiency</div>
          </div>
        </div>
      )}
      
      {result.stego_image && (
        <div className="flex justify-center">
          <button
            onClick={() => onDownload && onDownload(result.stego_image)}
            className="btn-primary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Stego Image</span>
          </button>
        </div>
      )}
    </div>
  );
  
  const renderExtractResult = () => (
    <div className="space-y-4">
      {result.payload_text && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Extracted Text:</h4>
          <div className="p-3 bg-gray-50 rounded-lg border">
            <pre className="text-sm text-gray-900 whitespace-pre-wrap font-mono">
              {result.payload_text}
            </pre>
          </div>
        </div>
      )}
      
      {result.payload_file && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Extracted File:</h4>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
            <div className="flex items-center space-x-2">
              <Info className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">Binary file extracted</span>
            </div>
            <button
              onClick={() => onDownload && onDownload(result.payload_file)}
              className="btn-primary text-sm"
            >
              Download File
            </button>
          </div>
        </div>
      )}
    </div>
  );
  
  const renderAnalyzeResult = () => (
    <div className="space-y-4">
      {/* Confidence Score */}
      <div className="text-center p-4 bg-gray-50 rounded-lg">
        <div className="text-3xl font-bold mb-2">
          <span className={result.confidence > 0.7 ? 'text-red-600' : 
                          result.confidence > 0.4 ? 'text-yellow-600' : 'text-green-600'}>
            {result.confidence ? (result.confidence * 100).toFixed(1) : 0}%
          </span>
        </div>
        <div className="text-sm text-gray-600">Steganography Confidence</div>
        <div className={`text-xs mt-1 px-2 py-1 rounded-full inline-block ${
          result.confidence > 0.7 ? 'bg-red-100 text-red-700' :
          result.confidence > 0.4 ? 'bg-yellow-100 text-yellow-700' :
          'bg-green-100 text-green-700'
        }`}>
          {result.confidence > 0.7 ? 'High Risk' :
           result.confidence > 0.4 ? 'Medium Risk' : 'Low Risk'}
        </div>
      </div>
      
      {/* Analysis Details */}
      {result.chi_square && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <BarChart3 className="w-4 h-4 mr-1" />
            Chi-Square Analysis
          </h4>
          <div className="grid grid-cols-3 gap-2 text-xs">
            {Object.entries(result.chi_square).map(([channel, data]) => (
              <div key={channel} className="p-2 bg-gray-50 rounded text-center">
                <div className="font-medium text-gray-900">{channel.toUpperCase()}</div>
                <div className="text-gray-600">p: {data.p_value?.toFixed(3) || 'N/A'}</div>
                <div className={`text-xs ${data.suspicious ? 'text-red-600' : 'text-green-600'}`}>
                  {data.suspicious ? 'Suspicious' : 'Normal'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Explanation */}
      {result.explanation && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis Summary:</h4>
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            {result.explanation}
          </p>
        </div>
      )}
    </div>
  );
  
  const renderContent = () => {
    switch (type) {
      case 'embed':
        return renderEmbedResult();
      case 'extract':
        return renderExtractResult();
      case 'analyze':
        return renderAnalyzeResult();
      default:
        return null;
    }
  };
  
  return (
    <div className={`card ${className}`}>
      <div className={`flex items-center space-x-3 p-4 rounded-lg border ${getStatusColor()}`}>
        {getStatusIcon()}
        <div>
          <h3 className="font-medium">{getStatusText()}</h3>
          {result.message && !result.success && (
            <p className="text-sm opacity-75 mt-1">{result.message}</p>
          )}
        </div>
      </div>
      
      {result.success && (
        <div className="mt-4">
          {renderContent()}
        </div>
      )}
    </div>
  );
};

export default ResultCard;
