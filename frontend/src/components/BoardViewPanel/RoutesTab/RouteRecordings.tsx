import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { useRecordings, useCreateRecording } from '../../../hooks/useRecordings';
import { Route, Recording, Hold, SensorReadingFrame, SensorReading } from '../../../types';

interface RouteRecordingsProps {
  route: Route | null;
  recordings: Recording[];
  setRecordings: (recordings: Recording[]) => void;
  holds: Hold[];
  setPlaybackData: (data: SensorReadingFrame[] | null) => void; // Updated prop
}

const RouteRecordings: React.FC<RouteRecordingsProps> = ({
  route,
  recordings,
  setRecordings,
  holds,
  setPlaybackData,
}) => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingStartTime, setRecordingStartTime] = useState<Date | null>(null);
  const [recordingDuration, setRecordingDuration] = useState<number>(0);

  const { getRecordings, loading: loadingRecordings, error } = useRecordings();
  const { mutate: createRecording, loading: creatingRecording } = useCreateRecording();

  useEffect(() => {
    if (route) {
      fetchRecordings(route.id);
    } else {
      setRecordings([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route]);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isRecording && recordingStartTime) {
      timer = setInterval(() => {
        setRecordingDuration(
          Math.floor((Date.now() - recordingStartTime.getTime()) / 1000)
        );
      }, 1000);
    } else {
      setRecordingDuration(0);
    }

    return () => {
      clearInterval(timer);
    };
  }, [isRecording, recordingStartTime]);

  const fetchRecordings = async (routeId: string) => {
    try {
      const recs = await getRecordings(routeId);
      setRecordings(recs);
    } catch (err) {
      console.error('Error fetching recordings:', err);
    }
  };

  const handleStartRecording = () => {
    if (!route) return;
    setIsRecording(true);
    setRecordingStartTime(new Date());
  };

  const handleEndRecording = async () => {
    setIsRecording(false);
    const recordingEndTime = new Date();

    if (!route || !recordingStartTime) return;

    try {
      const newRecordingData = {
        route_id: route.id,
        start_time: recordingStartTime.toISOString(),
        end_time: recordingEndTime.toISOString(),
      };

      // Use the mutation hook to create the recording
      const newRecording: Recording = await createRecording(newRecordingData);

      // Update recordings list
      setRecordings([...recordings, newRecording]);

      // Reset recording start time
      setRecordingStartTime(null);
    } catch (error) {
      console.error('Error creating recording:', error);
    }
  };

  const handlePlayRecording = (recording: Recording) => {
    if (recording.sensor_readings) {
      // Interpolate sensor readings to 100 Hz
      const interpolatedData = interpolateSensorReadings(recording.sensor_readings);
      setPlaybackData(interpolatedData); // Pass interpolated data to BoardView
    } else {
      setPlaybackData(null);
    }
  };

  // Interpolation function
  const interpolateSensorReadings = (originalReadings: SensorReadingFrame[]): SensorReadingFrame[] => {
    const interpolatedReadings: SensorReadingFrame[] = [];

    for (let i = 0; i < originalReadings.length - 1; i++) {
      const frameA = originalReadings[i];
      const frameB = originalReadings[i + 1];

      // Map hold IDs to readings for quick lookup
      const holdIds = new Set<string>();
      frameA.forEach((reading) => holdIds.add(reading.hold_id));
      frameB.forEach((reading) => holdIds.add(reading.hold_id));

      const steps = 10; // Number of interpolated frames between frameA and frameB

      for (let step = 0; step < steps; step++) {
        const t = step / steps; // Interpolation factor between 0 and 1
        const interpolatedFrame: SensorReading[] = [];

        holdIds.forEach((hold_id) => {
          const readingA = frameA.find((r) => r.hold_id === hold_id);
          const readingB = frameB.find((r) => r.hold_id === hold_id);

          // If reading is missing in a frame, assume zero
          const xA = readingA ? readingA.x : 0;
          const yA = readingA ? readingA.y : 0;
          const xB = readingB ? readingB.x : 0;
          const yB = readingB ? readingB.y : 0;

          const x = xA + (xB - xA) * t;
          const y = yA + (yB - yA) * t;

          interpolatedFrame.push({ hold_id, x, y });
        });

        interpolatedReadings.push(interpolatedFrame);
      }
    }

    // Add the last original frame to the interpolated readings
    interpolatedReadings.push(originalReadings[originalReadings.length - 1]);

    return interpolatedReadings;
  };

  if (!route) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">Select a route to view recordings.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
      <Typography variant="h6">Recordings</Typography>

      {/* Recording Controls */}
      <Box sx={{ my: 2, display: 'flex', alignItems: 'center' }}>
        {isRecording ? (
          <>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleEndRecording}
              disabled={creatingRecording}
            >
              {creatingRecording ? 'Saving...' : 'End Recording'}
            </Button>
            <Typography variant="body2" sx={{ ml: 2 }}>
              Recording Duration: {recordingDuration} seconds
            </Typography>
          </>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={handleStartRecording}
            disabled={!route}
          >
            Start Recording
          </Button>
        )}
      </Box>

      {loadingRecordings && <Typography>Loading recordings...</Typography>}
      {error && <Typography>Error loading recordings: {error}</Typography>}

      {recordings.length > 0 ? (
        <List>
          {recordings.map((recording) => (
            <ListItem key={recording.id} disableGutters>
              <ListItemText
                primary={`Recording from ${new Date(
                  recording.start_time
                ).toLocaleString()}`}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={() => handlePlayRecording(recording)}
              >
                Play
              </Button>
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2">No recordings available.</Typography>
      )}
    </Box>
  );
};

export default RouteRecordings;