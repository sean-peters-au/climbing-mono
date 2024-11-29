import React from 'react';

interface VideoPlayerProps {
  videoUrl: string;
  format: 'jpg' | 'mp4';
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, format }) => {
  let player: React.ReactNode;
  if (format === 'jpg') {
    player = <JPGVideoPlayer videoUrl={videoUrl} />;
  } else if (format === 'mp4') {
    player = <MP4VideoPlayer videoUrl={videoUrl} />;
  }
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden' }}>
      <div style={{ position: 'relative', width: '100%', height: '0', paddingBottom: '56.25%' }}>
        {player}
      </div>
    </div>
  );
};

interface JPGVideoPlayerProps {
  videoUrl: string;
}

const JPGVideoPlayer: React.FC<JPGVideoPlayerProps> = ({ videoUrl }) => {
  return (
    <img
      src={videoUrl}
      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      alt="Camera stream"
    />
  );
};

interface MP4VideoPlayerProps {
  videoUrl: string;
}

const MP4VideoPlayer: React.FC<MP4VideoPlayerProps> = ({ videoUrl }) => {
  return (
    <video
      controls
      src={videoUrl}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: '#000',
      }}
    />
  );
};

export default VideoPlayer;