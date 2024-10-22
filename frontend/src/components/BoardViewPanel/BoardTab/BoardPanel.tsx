import React from 'react';
import { Box, Typography } from '@mui/material';

type Wall = {
  id: string;
  name: string;
  // Include other wall properties as needed
};

type BoardPanelProps = {
  wall: Wall;
};

const BoardPanel: React.FC<BoardPanelProps> = ({ wall }) => {
  return (
    <Box>
      <Typography variant="h6">Board</Typography>
      {/* Include logic and data specific to the wall */}
      <Typography variant="body1">Wall Name: {wall.name}</Typography>
      {/* Add more content as needed */}
    </Box>
  );
};

export default BoardPanel;