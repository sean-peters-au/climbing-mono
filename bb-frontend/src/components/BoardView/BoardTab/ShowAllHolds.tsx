import React, { useContext, useEffect } from 'react';
import { Button } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';

const ShowAllHolds: React.FC = () => {
  const { showAllHolds, setShowAllHolds } = useContext(BoardViewContext)!;

  // Reset showAllHolds when component unmounts
  useEffect(() => {
    return () => {
      setShowAllHolds(false);
    };
  }, [setShowAllHolds]);

  return (
    <Button
      variant="contained"
      onClick={() => setShowAllHolds(!showAllHolds)}
      sx={{ mb: 2 }}
    >
      {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
    </Button>
  );
};

export default ShowAllHolds;