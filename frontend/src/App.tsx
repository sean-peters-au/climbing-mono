import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import WallCreate from './components/WallCreate';
import WallDetail from './components/WallDetail';
import WallList from './components/WallList';

const App: React.FC = () => (
  <Router>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/walls/" element={<WallList />} />
      <Route path="/walls/new" element={<WallCreate />} />
      <Route path="/walls/:wallId" element={<WallDetail />} />
    </Routes>
  </Router>
);

export default App;