import React, { useState } from 'react';
import {
  TextField,
  Button,
  Typography,
  Alert,
  Box,
  InputAdornment,
} from '@mui/material';
import API from '../services/api';

interface Props {
  wallId: string;
  selectedHolds: string[];
}

const ClimbCreate: React.FC<Props> = ({ wallId, selectedHolds }) => {
  const [formData, setFormData] = useState({
    name: '',
    grade: '',
    description: '',
  });
  const [message, setMessage] = useState<string>('');

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedHolds.length === 0) {
      alert('Please select at least one hold for the climb.');
      return;
    }

    try {
      await API.post(`/wall/${wallId}/climb`, {
        ...formData,
        hold_ids: selectedHolds,
        date: new Date().toISOString(),
      });

      setMessage('Climb created successfully!');
      setFormData({
        name: '',
        grade: '',
        description: '',
      });
    } catch (error) {
      console.error('Error creating climb:', error);
      setMessage('Failed to create climb.');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Create New Climb
      </Typography>
      <TextField
        label="Climb Name"
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
      <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
        Create Climb
      </Button>
      {message && (
        <Alert severity="info" sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
    </Box>
  );
};

export default ClimbCreate;