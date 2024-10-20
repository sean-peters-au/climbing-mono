import React, { useState, useEffect } from 'react';
import API from '../services/api';
import { Box, Button, CircularProgress, Typography, MenuItem, Select, FormControl, InputLabel, List, ListItem, ListItemText, SelectChangeEvent } from '@mui/material';
import SVGVisualization from './SVGVisualisation';
import { Hold, Recording } from '../types';

type Climb = {
  id: string;
  name: string;
};

const RecordingManager: React.FC = () => {
  const [climbs, setClimbs] = useState<Climb[]>([]);
  const [selectedClimb, setSelectedClimb] = useState<string>('');
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [currentPlayback, setCurrentPlayback] = useState<Recording | null>(null);
  const [holds, setHolds] = useState<Hold[]>([]);

  useEffect(() => {
    fetchClimbs();
  }, []);

  const fetchClimbs = async () => {
    try {
      const response = await API.get('/climbs');
      setClimbs(response.data.climbs);
    } catch (error) {
      console.error('Error fetching climbs:', error);
    }
  };

  const handleClimbSelect = async (event: SelectChangeEvent<string>) => {
    const climbId = event.target.value;
    setSelectedClimb(climbId);
    await fetchRecordings(climbId);
    await fetchHolds(climbId);
  };

  const fetchRecordings = async (climbId: string) => {
    try {
      const response = await API.get(`/climbs/${climbId}/recordings`);
      setRecordings(response.data.recordings);
    } catch (error) {
      console.error('Error fetching recordings:', error);
    }
  };

  const fetchHolds = async (climbId: string) => {
    try {
      const response = await API.get(`/climbs/${climbId}/holds`);
      setHolds(response.data.holds);
    } catch (error) {
      console.error('Error fetching holds:', error);
    }
  };

  const createRecording = async () => {
    if (!selectedClimb) return;

    const startTime = new Date();
    const endTime = new Date(startTime.getTime() + 5000); // Simulate a 5-second recording

    setIsRecording(true);

    try {
      const response = await API.post('/recording', {
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        route_id: selectedClimb,
      });
      setRecordings([...recordings, response.data]);
    } catch (error) {
      console.error('Error creating recording:', error);
    } finally {
      setIsRecording(false);
    }
  };

  const playRecording = (recording: Recording) => {
    setCurrentPlayback(recording);
  };

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        Recording Manager
      </Typography>

      <FormControl fullWidth margin="normal">
        <InputLabel id="climb-select-label">Select a Climb</InputLabel>
        <Select
          labelId="climb-select-label"
          value={selectedClimb}
          onChange={handleClimbSelect}
          label="Select a Climb"
        >
          {climbs.map((climb) => (
            <MenuItem key={climb.id} value={climb.id}>
              {climb.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedClimb && (
        <Box my={2}>
          <Button variant="contained" color="primary" onClick={createRecording} disabled={isRecording}>
            {isRecording ? <CircularProgress size={24} /> : 'Create Recording'}
          </Button>
        </Box>
      )}

      {recordings.length > 0 && (
        <Box my={2}>
          <Typography variant="h5">Recordings</Typography>
          <List>
            {recordings.map((recording) => (
              <ListItem key={recording.id} onClick={() => playRecording(recording)}>
                <ListItemText
                  primary={`Recording from ${new Date(recording.start_time).toLocaleString()}`}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {currentPlayback && holds.length > 0 && (
        <Box my={2}>
          <Typography variant="h5">Playback Visualization</Typography>
          <SVGVisualization
            sensorData={currentPlayback.sensor_readings}
            holds={holds}
          />
        </Box>
      )}
    </Box>
  );
};

export default RecordingManager;
