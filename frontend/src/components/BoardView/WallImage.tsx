import React, { useContext, useRef } from 'react';
import { Box } from '@mui/material';
import { BoardViewContext } from './BoardViewContext';
import HoldOverlay from './HoldOverlay';
import Drawing from './Drawing';

const WallImage: React.FC = () => {
  const { wall } = useContext(BoardViewContext)!;
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <Box
      ref={containerRef}
      position="relative"
      width="100%"
      height="100%"
      sx={{ overflow: 'hidden' }}
    >
      <img
        src={wall.image_url}
        alt="Wall"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          display: 'block',
        }}
      />
      <HoldOverlay />
      <Drawing />
    </Box>
  );
};

export default WallImage;
