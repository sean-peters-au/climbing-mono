import React, { useContext } from 'react';
import { Box, IconButton } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import ViewInArIcon from '@mui/icons-material/ViewInAr';
import VideocamIcon from '@mui/icons-material/Videocam';
import { BoardViewContext } from '../BoardViewContext';

const VisualModeButtons: React.FC = () => {
  const { visualMode, setVisualMode } = useContext(BoardViewContext)!;

  return (
    <Box
      position="absolute"
      top={8}
      right={8}
      zIndex={1}
      sx={{
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        borderRadius: 1,
        padding: 0.5,
      }}
    >
      <IconButton
        sx={{
          color: visualMode === '2D' ? 'primary.main' : 'white',
        }}
        onClick={() => setVisualMode('2D')}
      >
        <ImageIcon />
      </IconButton>
      <IconButton
        sx={{
          color: visualMode === '3D' ? 'primary.main' : 'white',
        }}
        onClick={() => setVisualMode('3D')}
      >
        <ViewInArIcon />
      </IconButton>
      <IconButton
        sx={{
          color: visualMode === 'Video' ? 'primary.main' : 'white',
        }}
        onClick={() => setVisualMode('Video')}
      >
        <VideocamIcon />
      </IconButton>
    </Box>
  );
};

export default VisualModeButtons;