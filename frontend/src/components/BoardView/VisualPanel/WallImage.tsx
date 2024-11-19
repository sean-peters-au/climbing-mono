import React, { useContext, useRef } from 'react';
import { Box } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import HoldOverlay from './HoldOverlay';
import Drawing from './Drawing';
import ThreeDView from './ThreeDView';
import VideoPlayer from './VideoPlayer';

const WallImage: React.FC = () => {
  const { wall, visualMode } = useContext(BoardViewContext)!;
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <Box
      ref={containerRef}
      position="relative"
      width="100%"
      height="100%"
      sx={{ overflow: 'hidden' }}
    >
      {visualMode === '2D' && (
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
      )}

      {visualMode === '3D' && <ThreeDView />}

      {visualMode === 'Video' && <VideoPlayer />}

      <HoldOverlay />
      <Drawing />
    </Box>
  );
};

export default WallImage;
