/* eslint-disable jsx-a11y/iframe-has-title */
import React from 'react';
import { CAMERA_STREAM_URL } from '../../../services/betaboard-camera/constants';

const VideoPlayer: React.FC = () => {
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden' }}>
      <div style={{ position: 'relative', width: '100%', height: '0', paddingBottom: '56.25%' }}>
        <iframe
          src={CAMERA_STREAM_URL}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 5 }}
          allow="autoplay"
        />
      </div>
    </div>
  );
};

export default VideoPlayer;