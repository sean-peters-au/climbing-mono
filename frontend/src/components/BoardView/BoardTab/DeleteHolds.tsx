import React, { useContext, useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import { useDeleteHold } from '../../../hooks/useWall';

const DeleteHolds: React.FC = () => {
  const { wall, selectedHolds, setSelectedHolds } = useContext(BoardViewContext)!;

  const deleteHoldMutation = useDeleteHold();
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const handleStartDeletion = () => {
    // Clear selected holds to avoid accidental deletion
    setSelectedHolds([]);
    setIsDeleting(true);
  };

  const handleCancelDeletion = () => {
    setIsDeleting(false);
    setSelectedHolds([]);
  };

  const handleConfirmDeletion = async () => {
    try {
      await Promise.all(
          selectedHolds.map((holdId) =>
            deleteHoldMutation.mutateAsync({ wallId: wall.id, holdId })
          )
      );
      setSelectedHolds([]);
      setIsDeleting(false);
    } catch (error) {
      console.error('Error deleting holds:', error);
      // Handle error (e.g., show a notification)
    }
  };

  // Calculate number of affected routes
  const routesAffected = wall.routes.filter((route) =>
    route.holds.some((hold) => selectedHolds.includes(hold.id))
  );

  return (
    <Box>
      {!isDeleting ? (
        <Button variant="contained" color="error" onClick={handleStartDeletion}>
          Select and Delete Holds
        </Button>
      ) : (
        <Box>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Select holds on the wall to delete.
          </Typography>
          {selectedHolds.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">
                You have selected {selectedHolds.length} hold(s) to delete.
              </Typography>
              <Typography variant="body1">
                This will affect {routesAffected.length} route(s).
              </Typography>
              <Button
                variant="contained"
                color="error"
                onClick={handleConfirmDeletion}
                sx={{ mt: 1, mr: 1 }}
              >
                Confirm Deletion
              </Button>
              <Button variant="outlined" onClick={handleCancelDeletion} sx={{ mt: 1 }}>
                Cancel
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default DeleteHolds;