import React from 'react';
import { Typography, Box } from '@mui/material';
import Layout from '../components/Layout';
import WallList from '../components/WallList';
import LoadingAnimation from '../components/LoadingAnimation';
import useWalls from '../hooks/useWalls';

const Home: React.FC = () => {
  const { loading } = useWalls();

  const leftColumn = (
    <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {loading ? (
        <LoadingAnimation message="Loading walls..." />
      ) : (
        <Typography variant="h5">Select a wall to view details</Typography>
      )}
    </Box>
  );

  const rightColumn = (
    <Box>
      <Typography variant="h4" gutterBottom>
        Climbing Walls
      </Typography>
      <WallList />
    </Box>
  );

  return (
    <Layout leftColumn={leftColumn} rightColumn={rightColumn} />
  );
};

export default Home;