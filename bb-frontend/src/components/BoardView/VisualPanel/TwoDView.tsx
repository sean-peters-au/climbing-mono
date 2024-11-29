import React, { useContext } from 'react';
import { Box } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';

const TwoDView: React.FC = () => {
  const { wall } = useContext(BoardViewContext)!;

  return (
    <Box 
      sx={{ 
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',  // Center vertically
        justifyContent: 'center',  // Center horizontally
      }}
    >
      <img
        src={wall.image_url}
        alt="Wall"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          position: 'relative',
        }}
      />
    </Box>
  );
};

export default TwoDView;
