import React from 'react';
import { Check } from 'lucide-react';

const StepsWizard = ({ 
  steps, 
  currentStep, 
  onStepClick = null,
  className = ""
}) => {
  const getStepStatus = (stepIndex) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) return 'active';
    return 'pending';
  };
  
  const getStepClasses = (status) => {
    const baseClasses = "step-indicator";
    switch (status) {
      case 'completed':
        return `${baseClasses} step-completed`;
      case 'active':
        return `${baseClasses} step-active`;
      default:
        return `${baseClasses} step-pending`;
    }
  };
  
  return (
    <div className={`${className}`}>
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(index);
          const isClickable = onStepClick && (status === 'completed' || status === 'active');
          
          return (
            <React.Fragment key={index}>
              <div className="flex flex-col items-center">
                <button
                  onClick={() => isClickable && onStepClick(index)}
                  disabled={!isClickable}
                  className={`${getStepClasses(status)} ${
                    isClickable ? 'cursor-pointer' : 'cursor-default'
                  } transition-all duration-200`}
                >
                  {status === 'completed' ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </button>
                <div className="mt-2 text-center">
                  <p className={`text-xs font-medium ${
                    status === 'active' ? 'text-primary-600' : 
                    status === 'completed' ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                  {step.description && (
                    <p className="text-xs text-gray-400 mt-1 max-w-24">
                      {step.description}
                    </p>
                  )}
                </div>
              </div>
              
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="flex-1 mx-4">
                  <div className="h-0.5 bg-gray-200 relative">
                    <div 
                      className={`h-full transition-all duration-300 ${
                        index < currentStep ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                      style={{ width: index < currentStep ? '100%' : '0%' }}
                    />
                  </div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default StepsWizard;
