import React, { useContext } from 'react';
import { Button } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';

const ShowAllHolds: React.FC = () => {
  const { showAllHolds, toggleShowAllHolds } = useContext(BoardViewContext)!;

  return (
    <Button
      variant="contained"
      onClick={toggleShowAllHolds}
      sx={{ mb: 2 }}
    >
      {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
    </Button>
  );
};

export default ShowAllHolds;