import React from 'react';
import { CAMERA_STREAM_URL } from '../../../services/betaboard-camera/api';

const VideoPlayer: React.FC = () => {
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden' }}>
      <div style={{ position: 'relative', width: '100%', height: '0', paddingBottom: '56.25%' }}>
        <img
          src={CAMERA_STREAM_URL}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
          alt="Camera stream"
        />
      </div>
    </div>
  );
};

export default VideoPlayer;