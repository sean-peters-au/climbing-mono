import React from 'react';
import { Box } from '@mui/material';
import { Wall, Hold } from '../types';
import HoldOverlay from './HoldOverlay';

type WallImageProps = {
  wall: Wall;
  holds: Hold[];
  selectedHolds: string[];
  showAllHolds: boolean;
  onHoldClick: (holdId: string) => void;
  climbHoldIds: string[];
};

const WallImage: React.FC<WallImageProps> = ({
  wall,
  holds,
  selectedHolds,
  showAllHolds,
  onHoldClick,
  climbHoldIds,
}) => {
  return (
    <Box
      sx={{
        position: 'relative',
        height: '100vh',
        overflow: 'hidden',
      }}
    >
      <img
        src={wall.image_url}
        alt={wall.name}
        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
      />
      {/* Hold Overlay */}
      <HoldOverlay
        wall={wall}
        holds={holds}
        selectedHolds={selectedHolds}
        showAllHolds={showAllHolds}
        onHoldClick={onHoldClick}
        climbHoldIds={climbHoldIds}
      />
    </Box>
  );
};

export default WallImage;