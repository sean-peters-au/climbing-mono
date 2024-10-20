import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import BoardCreate from './pages/BoardCreate';
import BoardView from './pages/BoardView';

const App: React.FC = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/walls/new" element={<BoardCreate />} />
      <Route path="/walls/:wallId" element={<BoardView />} />
    </Routes>
  </Router>
);

export default App;