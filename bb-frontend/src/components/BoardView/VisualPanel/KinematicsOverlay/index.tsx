import React, { useContext, useMemo } from 'react';
import { BoardViewContext } from '../../BoardViewContext';
import { PoseLandmark } from '../../../../types';

// Define connections between landmarks for skeleton visualization
const POSE_CONNECTIONS = [
  // Torso
  ['left_shoulder', 'right_shoulder'],
  ['left_shoulder', 'left_hip'],
  ['right_shoulder', 'right_hip'],
  ['left_hip', 'right_hip'],
  
  // Arms
  ['left_shoulder', 'left_elbow'],
  ['left_elbow', 'left_wrist'],
  ['right_shoulder', 'right_elbow'],
  ['right_elbow', 'right_wrist'],
  
  // Legs
  ['left_hip', 'left_knee'],
  ['left_knee', 'left_ankle'],
  ['right_hip', 'right_knee'],
  ['right_knee', 'right_ankle'],
];

const KinematicsOverlay: React.FC = () => {
  const { 
    isPlaying,
    currentFrame,
    playbackKinematics
  } = useContext(BoardViewContext)!;

  const skeleton = useMemo(() => {
    if (!isPlaying || !playbackKinematics?.frames) return null;

    const frame = playbackKinematics.frames[currentFrame];
    if (!frame) return null;

    const landmarks = frame.landmarks;
    
    return (
      <g>
        {/* Draw connections (skeleton lines) */}
        {POSE_CONNECTIONS.map(([start, end], index) => {
          const startPoint = landmarks[start];
          const endPoint = landmarks[end];
          
          if (!startPoint || !endPoint) return null;
          
          // Only draw if both points are reasonably visible
          if (startPoint.visibility < 0.5 || endPoint.visibility < 0.5) return null;

          return (
            <line
              key={`connection-${index}`}
              x1={startPoint.x * 100 + '%'}
              y1={startPoint.y * 100 + '%'}
              x2={endPoint.x * 100 + '%'}
              y2={endPoint.y * 100 + '%'}
              stroke="yellow"
              strokeWidth={4}
              opacity={0.8}
            />
          );
        })}

        {/* Draw landmarks (joints) */}
        {Object.entries(landmarks).map(([name, point]) => {
          if (point.visibility < 0.5) return null;

          return (
            <circle
              key={`landmark-${name}`}
              cx={point.x * 100 + '%'}
              cy={point.y * 100 + '%'}
              r={4}
              fill="yellow"
              opacity={0.8}
            />
          );
        })}
      </g>
    );
  }, [isPlaying, currentFrame, playbackKinematics]);

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    >
      {skeleton}
    </svg>
  );
};

export default KinematicsOverlay; 