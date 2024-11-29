import React, { useContext } from 'react';
import { Box } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';

const TwoDView: React.FC = () => {
  const { wall } = useContext(BoardViewContext)!;

  return (
    <Box>
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
    </Box>
  );
};

export default TwoDView;
