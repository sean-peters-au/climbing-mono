// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import WallList from './components/WallList';
import WallCreate from './components/WallCreate';
import WallDetail from './components/WallDetail';

const App: React.FC = () => (
  <Router>
    <Layout>
      <Routes>
        <Route path="/" element={<WallList />} />
        <Route path="/walls/new" element={<WallCreate />} />
        <Route path="/walls/:id" element={<WallDetail />} />
      </Routes>
    </Layout>
  </Router>
);

export default App;