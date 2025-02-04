import React, { useContext, useRef } from 'react';
import { Box } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import HoldOverlay from './VisualPanelOverlays';
import Drawing from './Drawing';
import ThreeDView from './ThreeDView';
import VideoPlayer from './VideoPlayer';
import TwoDView from './TwoDView';
import { CAMERA_STREAM_URL } from '../../../services/betaboard-camera/api';
import VisualPanelOverlays from './VisualPanelOverlays';


const VisualPanel: React.FC = () => {
  const { visualMode } = useContext(BoardViewContext)!;
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <Box
      ref={containerRef}
      position="relative"
      width="100%"
      height="100%"
      sx={{ overflow: 'hidden' }}
    >
      {visualMode === '2D' && <TwoDView />}

      {visualMode === '3D' && <ThreeDView />}

      {visualMode === 'Video' && <VideoPlayer videoUrl={CAMERA_STREAM_URL} format='jpg'/>}

      <VisualPanelOverlays />
      <Drawing />
    </Box>
  );
};

export default VisualPanel;
