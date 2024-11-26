import React from 'react';
import { Box } from '@mui/material';
import { CAMERA_STREAM_URL } from '../../../services/betaboard-camera/constants';

const VideoPlayer: React.FC = () => {
  return (
    <Box
      width="100%"
      height="100%"
      display="flex"
      justifyContent="center"
      alignItems="center"
      bgcolor="black"
    >
      <img
        src={CAMERA_STREAM_URL}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
        }}
        alt="Live camera feed"
      />
    </Box>
  );
};

export default VideoPlayer;