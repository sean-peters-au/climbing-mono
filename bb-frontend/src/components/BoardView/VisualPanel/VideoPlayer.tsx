import React, { useEffect, useRef } from 'react';
import mpegts from 'mpegts.js';
import { CAMERA_STREAM_URL } from '../../../services/betaboard-camera/api';

const VideoPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<mpegts.Player | null>(null);

  useEffect(() => {
    if (mpegts.getFeatureList().mseLivePlayback && videoRef.current && !playerRef.current) {
      const player = mpegts.createPlayer({
        type: 'mse',
        isLive: true,
        url: CAMERA_STREAM_URL,
      });

      player.attachMediaElement(videoRef.current);

      player.on(mpegts.Events.LOADING_COMPLETE, () => {
        const playPromise = player.play();
        if (playPromise !== undefined) {
          playPromise.catch(() => {
            // Ignore play interruption errors
          });
        }
      });

      player.load();
      playerRef.current = player;
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.destroy();
        playerRef.current = null;
      }
    };
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden' }}>
      <div style={{ position: 'relative', width: '100%', height: '0', paddingBottom: '56.25%' }}>
        <video 
          ref={videoRef}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
          controls={false}
          muted
          playsInline
        />
      </div>
    </div>
  );
};

export default VideoPlayer;