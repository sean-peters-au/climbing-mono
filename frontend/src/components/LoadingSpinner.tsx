// src/components/LoadingSpinner.tsx
import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message }) => (
  <div className="loading-spinner">
    <div className="spinner" />
    {message && <p>{message}</p>}
  </div>
);

export default LoadingSpinner;