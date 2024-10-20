import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  InputAdornment,
} from '@mui/material';
import API from '../services/api';

type CreateRoutePanelProps = {
  wallId: string;
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
};

const CreateRoutePanel: React.FC<CreateRoutePanelProps> = ({
  wallId,
  selectedHolds,
  setSelectedHolds,
}) => {
  const [routeName, setRouteName] = useState('');
  const [grade, setGrade] = useState('');
  const [description, setDescription] = useState('');

  const handleCreateRoute = async () => {
    if (selectedHolds.length === 0) {
      alert('Please select at least one hold for the route.');
      return;
    }

    try {
      await API.post(`/wall/${wallId}/route`, {
        name: routeName,
        grade,
        description,
        hold_ids: selectedHolds,
        date: new Date().toISOString(),
      });
      alert('Route created successfully!');
      // Reset form and selections
      setRouteName('');
      setGrade('');
      setDescription('');
      setSelectedHolds([]);
    } catch (error) {
      console.error('Error creating route:', error);
      alert('Failed to create route.');
    }
  };

  return (
    <Box>
      <Typography variant="h6">Create New Route</Typography>
      <TextField
        label="Route Name"
        value={routeName}
        onChange={(e) => setRouteName(e.target.value)}
        fullWidth
        margin="normal"
      />
      <TextField
        label="Grade"
        value={grade}
        onChange={(e) => setGrade(e.target.value)}
        fullWidth
        margin="normal"
        InputProps={{
          startAdornment: <InputAdornment position="start">V</InputAdornment>,
        }}
      />
      <TextField
        label="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        fullWidth
        multiline
        rows={4}
        margin="normal"
      />
      <Typography variant="body1" gutterBottom>
        Selected Holds: {selectedHolds.length}
      </Typography>
      <Button variant="contained" color="primary" onClick={handleCreateRoute}>
        Create Route
      </Button>
    </Box>
  );
};

export default CreateRoutePanel;