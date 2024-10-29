import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import BoardCreate from './pages/BoardCreate';
import BoardView from './pages/BoardView';
import { QueryClient, QueryClientProvider } from 'react-query';

const queryClient = new QueryClient();

const App: React.FC = () => (
  <QueryClientProvider client={queryClient}>
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/walls/new" element={<BoardCreate />} />
        <Route path="/walls/:wallId" element={<BoardView />} />
      </Routes>
    </Router>
  </QueryClientProvider>
);

export default App;
