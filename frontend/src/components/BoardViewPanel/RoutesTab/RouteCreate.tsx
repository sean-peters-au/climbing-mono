import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  DialogActions,
} from '@mui/material';
import { useCreateRoute } from '../../../hooks/useRoutes';

interface RouteCreateProps {
  open: boolean;
  onClose: () => void;
  wallId: string;
  selectedHolds: string[];
}

const RouteCreate: React.FC<RouteCreateProps> = ({
  open,
  onClose,
  wallId,
  selectedHolds,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    grade: 0,
    description: '',
  });
  const [message, setMessage] = useState<string>('');
  const { createRoute, loading, error } = useCreateRoute(wallId);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    if (selectedHolds.length === 0) {
      alert('Please select at least one hold for the route.');
      return;
    }

    try {
      await createRoute({
        ...formData,
        hold_ids: selectedHolds,
        date: new Date().toISOString(),
      });

      setMessage('Route created successfully!');
      setFormData({
        name: '',
        grade: 0,
        description: '',
      });
      onClose();
    } catch (error) {
      console.error('Error creating route:', error);
      setMessage('Failed to create route.');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth>
      <DialogTitle>Create New Route</DialogTitle>
      <DialogContent>
        <TextField
          label="Route Name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          fullWidth
          required
          margin="normal"
        />
        <TextField
          label="Grade"
          name="grade"
          value={formData.grade}
          type="number"
          onChange={handleChange}
          fullWidth
          required
          margin="normal"
          InputProps={{
            startAdornment: <InputAdornment position="start">V</InputAdornment>,
          }}
        />
        <TextField
          label="Description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          fullWidth
          multiline
          rows={4}
          margin="normal"
        />
        <Typography variant="body1" gutterBottom>
          Selected Holds: {selectedHolds.length}
        </Typography>
        {selectedHolds.length === 0 && (
          <Alert severity="warning">No holds selected.</Alert>
        )}
        {message && (
          <Alert severity="info" sx={{ mt: 2 }}>
            {message}
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? 'Creating...' : 'Create Route'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RouteCreate;