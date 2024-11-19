import React, { useRef } from 'react';
import { Box, Typography } from '@mui/material';

const ThreeDView: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <Box
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: '#ddd',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Typography variant="h4">3D View Coming Soon!</Typography>
    </Box>
  );
};

export default ThreeDView;