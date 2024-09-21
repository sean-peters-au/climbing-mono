import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

console.log('Environment variables:');
console.log('PORT:', process.env.PORT);
console.log('REACT_APP_PORT:', process.env.REACT_APP_PORT);

const port = process.env.PORT || process.env.REACT_APP_PORT || 3000;
console.log(`App is configured to run on port: ${port}`);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

reportWebVitals();
