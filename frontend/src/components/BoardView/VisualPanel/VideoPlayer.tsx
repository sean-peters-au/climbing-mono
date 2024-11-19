import React from 'react';
import { Box } from '@mui/material';
import ReactPlayer from 'react-player';
import { STREAM_URL } from '../../../services/betaboard-camera/constants';

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
      <ReactPlayer
        url={STREAM_URL}
        playing
        controls
        width="100%"
        height="100%"
        config={{
          file: {
            forceVideo: true,
            attributes: {
              style: {
                width: '100%',
                height: '100%',
                objectFit: 'contain'
              }
            }
          }
        }}
        onError={(e) => console.error('Video player error:', e)}
      />
    </Box>
  );
};

export default VideoPlayer;