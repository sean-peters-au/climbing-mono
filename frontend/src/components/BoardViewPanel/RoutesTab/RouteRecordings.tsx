// frontend/src/components/BoardViewPanel/RoutesTab/RouteRecordings.tsx

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useRecordings, useCreateRecording } from '../../../hooks/useRecordings';
import { Route, Recording, Hold, SensorReadingFrame } from '../../../types';

interface RouteRecordingsProps {
  route: Route;
  holds: Hold[];
  setPlaybackData: (data: SensorReadingFrame[] | null) => void;
  selectedRecordingIds: string[];
  setSelectedRecordingIds: (ids: string[]) => void;
}

const RouteRecordings: React.FC<RouteRecordingsProps> = ({
  route,
  holds,
  setPlaybackData,
  selectedRecordingIds,
  setSelectedRecordingIds,
}) => {
  const [recordings, setRecordings] = useState<Recording[]>([]);
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

  const handleRowSelection = (ids: string[]) => {
    setSelectedRecordingIds(ids);
  };

  const columns: GridColDef[] = [
    {
      field: 'start_time',
      headerName: 'Start Time',
      width: 200,
      valueGetter: (params) => new Date(params).toLocaleString(),
    },
    {
      field: 'end_time',
      headerName: 'End Time',
      width: 200,
      valueGetter: (params) => new Date(params).toLocaleString(),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Button
          variant="outlined"
          size="small"
          onClick={() => handlePlayRecording(params.row as Recording)}
        >
          Play
        </Button>
      ),
    },
  ];

  const handlePlayRecording = (recording: Recording) => {
    if (recording.sensor_readings) {
      // Interpolate sensor readings to 100 Hz
      const interpolatedData = interpolateSensorReadings(recording.sensor_readings);
      setPlaybackData(interpolatedData); // Pass interpolated data to BoardView
    } else {
      setPlaybackData(null);
    }
  };

  // Interpolation function (same as your existing code)
  const interpolateSensorReadings = (originalReadings: SensorReadingFrame[]): SensorReadingFrame[] => {
    // ... your existing interpolation logic ...
    return []; // Return interpolated readings
  };

  if (loadingRecordings) {
    return (
      <Box sx={{ mt: 2 }}>
        <CircularProgress />
        <Typography>Loading recordings...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography color="error">Error loading recordings: {error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Recording Controls */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
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

      {/* DataGrid for Recordings */}
      {recordings.length > 0 ? (
        <DataGrid
          rows={recordings}
          columns={columns}
          getRowId={(row) => row.id}
          checkboxSelection
          onRowSelectionModelChange={(ids) => handleRowSelection(ids as string[])}
          rowSelectionModel={selectedRecordingIds}
          disableRowSelectionOnClick
          autoHeight
        />
      ) : (
        <Typography variant="body2">No recordings available.</Typography>
      )}
    </Box>
  );
};

export default RouteRecordings;