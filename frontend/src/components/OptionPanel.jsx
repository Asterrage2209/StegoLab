import React from 'react';
import { Settings, Lock, Shield, Palette } from 'lucide-react';

const OptionPanel = ({ 
  options, 
  onChange, 
  className = ""
}) => {
  const handleInputChange = (key, value) => {
    onChange({
      ...options,
      [key]: value
    });
  };
  
  return (
    <div className={`card ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="w-5 h-5 text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-900">Embedding Options</h3>
      </div>
      
      <div className="space-y-6">
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
                  checked={options.bits === bits}
                  onChange={(e) => handleInputChange('bits', parseInt(e.target.value))}
                  className="mr-2 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">{bits} LSB</span>
              </label>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Higher values provide more capacity but may be more detectable
          </p>
        </div>
        
        {/* Color channels */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Palette className="w-4 h-4 inline mr-1" />
            Color Channels
          </label>
          <select
            value={options.channels}
            onChange={(e) => handleInputChange('channels', e.target.value)}
            className="input-field"
          >
            <option value="auto">Auto (All channels)</option>
            <option value="red">Red channel only</option>
            <option value="green">Green channel only</option>
            <option value="blue">Blue channel only</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Choose which color channels to use for embedding
          </p>
        </div>
        
        {/* Password */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Lock className="w-4 h-4 inline mr-1" />
            Password (Optional)
          </label>
          <input
            type="password"
            value={options.password || ''}
            onChange={(e) => handleInputChange('password', e.target.value)}
            placeholder="Enter password for permutation"
            className="input-field"
          />
          <p className="text-xs text-gray-500 mt-1">
            Used to randomize embedding positions for better security
          </p>
        </div>
        
        {/* Encryption */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={options.encrypt || false}
              onChange={(e) => handleInputChange('encrypt', e.target.checked)}
              className="mr-2 text-primary-600 focus:ring-primary-500"
            />
            <Shield className="w-4 h-4 mr-1 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Encrypt payload</span>
          </label>
          <p className="text-xs text-gray-500 mt-1 ml-6">
            Encrypt the payload data before embedding (requires password)
          </p>
        </div>
        
        {/* Advanced options */}
        <div className="border-t border-gray-200 pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Advanced Options</h4>
          
          <div className="space-y-3">
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.sequential || false}
                  onChange={(e) => handleInputChange('sequential', e.target.checked)}
                  className="mr-2 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Sequential embedding</span>
              </label>
              <p className="text-xs text-gray-500 mt-1 ml-6">
                Embed data sequentially instead of using random positions
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Header format
              </label>
              <select
                value={options.headerFormat || 'standard'}
                onChange={(e) => handleInputChange('headerFormat', e.target.value)}
                className="input-field"
              >
                <option value="standard">Standard (16 bytes)</option>
                <option value="minimal">Minimal (8 bytes)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptionPanel;
