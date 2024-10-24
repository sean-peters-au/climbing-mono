import React, { useContext } from 'react';
import { Box, Button } from '@mui/material';
import { BoardViewContext } from './BoardViewContext';
import HoldOverlay from './HoldOverlay';

const WallImage: React.FC = () => {
  const {
    wall,
    showAllHolds,
    toggleShowAllHolds,
  } = useContext(BoardViewContext)!;

  return (
    <Box position="relative" width="100%" height="100%">
      <img
        src={wall.image_url}
        alt="Wall"
        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
      />
      {/* HoldOverlay now accesses data from context */}
      <HoldOverlay />
      <Button
        variant="contained"
        color="primary"
        onClick={toggleShowAllHolds}
        style={{ position: 'absolute', top: 16, right: 16 }}
      >
        {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
      </Button>
    </Box>
  );
};

export default WallImage;
