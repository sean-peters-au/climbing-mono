import React, { useContext } from 'react';
import { Button, Typography } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import { useAddHold } from '../../../hooks/useWall';

const AddHold: React.FC = () => {
  const {
    setIsDrawing,
    drawnData,
    setDrawnData,
    wall,
  } = useContext(BoardViewContext)!;

  const addHoldMutation = useAddHold();

  const handleStartDrawing = () => {
    setDrawnData(null); // Clear any existing drawn hold
    setIsDrawing(true);
  };

  const handleAddHold = async () => {
    if (!drawnData) return;

    try {
      await addHoldMutation.mutateAsync({
        wallId: wall.id,
        bbox: drawnData.bbox,
        mask: drawnData.mask,
      });
      setIsDrawing(false);
      setDrawnData(null);
    } catch (error) {
      console.error('Error adding hold:', error);
      // Handle error (e.g., show a notification)
    }
  };

  return (
    <>
      <Button variant="contained" onClick={handleStartDrawing} sx={{ mb: 2 }}>
        Draw Hold
      </Button>
      {drawnData && (
        <>
          <Typography variant="body1">Hold drawn. Ready to add.</Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleAddHold}
            sx={{ mt: 1 }}
          >
            Add Drawn Hold
          </Button>
          <Button
            variant="outlined"
            onClick={() => {
              setDrawnData(null);
              setIsDrawing(false);
            }}
            sx={{ mt: 1, ml: 1 }}
          >
            Cancel
          </Button>
        </>
      )}
    </>
  );
};

export default AddHold;