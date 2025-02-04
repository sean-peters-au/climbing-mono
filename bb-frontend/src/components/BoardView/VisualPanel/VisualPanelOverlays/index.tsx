import React, { useContext } from 'react';
import HoldHighlights from './HoldHighlights';
import HoldVectors from './HoldVectors';
import { BoardViewContext } from '../../BoardViewContext';
import { HoldAnnotations } from './HoldAnnotations';
import KinematicsOverlay from './KinematicsOverlay';

const VisualPanelOverlays: React.FC = () => {
  const {
    wall,
  } = useContext(BoardViewContext)!;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        cursor: 'crosshair',
        pointerEvents: 'none',
      }}
    >
      <svg
        style={{
          width: '100%',
          height: '100%',
        }}
        viewBox={`0 0 ${wall.width} ${wall.height}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Render Hold Highlights */}
        <HoldHighlights/>

        <HoldVectors/>

        <HoldAnnotations/>

        <KinematicsOverlay/>
      </svg>
    </div>
  );
};

export default VisualPanelOverlays;
