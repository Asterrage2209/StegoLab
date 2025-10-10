import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Eye, Search, Play, ArrowRight, AlertTriangle } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: Shield,
      title: 'Embed Data',
      description: 'Hide text or files inside images using LSB steganography',
      link: '/embed',
      color: 'text-blue-600 bg-blue-100'
    },
    {
      icon: Eye,
      title: 'Extract Data',
      description: 'Retrieve hidden data from stego images with correct parameters',
      link: '/extract',
      color: 'text-green-600 bg-green-100'
    },
    {
      icon: Search,
      title: 'Analyze Images',
      description: 'Detect potential steganographic content using statistical analysis',
      link: '/analyze',
      color: 'text-purple-600 bg-purple-100'
    },
    {
      icon: Play,
      title: 'Try Demo',
      description: 'Explore sample images and test the application features',
      link: '/demo',
      color: 'text-orange-600 bg-orange-100'
    }
  ];
  
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-6">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center">
            <Shield className="w-8 h-8 text-white" />
          </div>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          StegoLab
        </h1>
        <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto">
          Advanced LSB Steganography & Anti-Steganography Web Application
        </p>
        <p className="text-gray-500 max-w-2xl mx-auto">
          Hide data in images, extract hidden content, and analyze images for steganographic artifacts 
          using cutting-edge statistical detection methods.
        </p>
      </div>
      
      {/* Features Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Link
              key={index}
              to={feature.link}
              className="card hover:shadow-lg transition-shadow duration-200 group"
            >
              <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 text-sm mb-4">
                {feature.description}
              </p>
              <div className="flex items-center text-primary-600 text-sm font-medium group-hover:translate-x-1 transition-transform duration-200">
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </div>
            </Link>
          );
        })}
      </div>
      
      {/* What is LSB Steganography */}
      <div className="card mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">What is LSB Steganography?</h2>
        <div className="prose max-w-none">
          <p className="text-gray-600 mb-4">
            LSB (Least Significant Bit) steganography is a technique for hiding information within digital images 
            by modifying the least significant bits of pixel values. This method allows data to be embedded 
            in a way that is visually imperceptible to human observers.
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">How it Works:</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Replace least significant bits of pixel values with data bits
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Changes are typically invisible to the human eye
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Data can be extracted by reading the LSBs in the correct order
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-primary-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Works best with lossless image formats (PNG, BMP)
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Applications:</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Digital watermarking and copyright protection
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Covert communication and data hiding
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Information security research and education
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Digital forensics and steganalysis
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      {/* Ethics Disclaimer */}
      <div className="card border-amber-200 bg-amber-50">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-amber-800 mb-2">
              Ethics & Legal Disclaimer
            </h3>
            <div className="text-amber-700 space-y-2">
              <p>
                <strong>Important:</strong> This application is designed for educational and research purposes only. 
                Steganography techniques should be used responsibly and in accordance with applicable laws and regulations.
              </p>
              <p>
                <strong>Legal Notice:</strong> Users are solely responsible for ensuring their use of this software 
                complies with all applicable laws in their jurisdiction. The developers disclaim any liability for 
                misuse of this application.
              </p>
              <p>
                <strong>Ethical Guidelines:</strong> Only use steganography for legitimate purposes such as:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Educational and research activities</li>
                <li>Digital watermarking for copyright protection</li>
                <li>Information security testing and validation</li>
                <li>Digital forensics and incident response</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
