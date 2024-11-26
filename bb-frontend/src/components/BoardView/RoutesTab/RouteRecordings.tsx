import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useRecordings, useStartRecording, useStopRecording } from '../../../hooks/useRecordings';
import { Route } from '../../../types';
import { QueryError } from '../../QueryError';

interface RouteRecordingsProps {
  route: Route;
  selectedRecordingIds: string[];
  setSelectedRecordingIds: (ids: string[]) => void;
}

const RouteRecordings: React.FC<RouteRecordingsProps> = ({
  route,
  selectedRecordingIds,
  setSelectedRecordingIds,
}) => {
  const [activeRecordingId, setActiveRecordingId] = useState<string | null>(null);
  const [recordingStartTime, setRecordingStartTime] = useState<Date | null>(null);
  const [recordingDuration, setRecordingDuration] = useState<number>(0);
  const [isStoppingRecording, setIsStoppingRecording] = useState(false);

  const { data: recordings, isLoading, error } = useRecordings(route.id);
  const { mutate: startRecording, isLoading: startingRecording } = useStartRecording();
  const { mutate: stopRecording, isLoading: stoppingRecording } = useStopRecording();

  // Recording duration timer
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (activeRecordingId && recordingStartTime && !isStoppingRecording) {
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
  }, [activeRecordingId, recordingStartTime, isStoppingRecording]);

  const handleStartRecording = () => {
    startRecording(route.id, {
      onSuccess: (recording) => {
        setActiveRecordingId(recording.id);
        setRecordingStartTime(new Date());
        setIsStoppingRecording(false);
      },
      onError: (error) => {
        console.error('Error starting recording:', error);
      }
    });
  };

  const handleStopRecording = () => {
    if (!activeRecordingId) return;
    setIsStoppingRecording(true);
    
    stopRecording(activeRecordingId, {
      onSuccess: () => {
        setActiveRecordingId(null);
        setRecordingStartTime(null);
        setIsStoppingRecording(false);
      },
      onError: (error) => {
        console.error('Error stopping recording:', error);
        setIsStoppingRecording(false);
      }
    });
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
      valueGetter: (params) => params ? new Date(params).toLocaleString() : 'Recording...',
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
    }
  ];

  if (isLoading) {
    return (
      <Box sx={{ mt: 2 }}>
        <CircularProgress />
        <Typography>Loading recordings...</Typography>
      </Box>
    );
  }

  if (error) {
    return <QueryError error={error} />;
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Recording Controls */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', height: 40 }}>
        <RecordingControls
          isStarting={startingRecording}
          activeRecordingId={activeRecordingId}
          isStopping={stoppingRecording || isStoppingRecording}
          recordingDuration={recordingDuration}
          onStart={handleStartRecording}
          onStop={handleStopRecording}
          disabled={!route}
        />
      </Box>

      {/* DataGrid for Recordings */}
      {recordings && recordings.length > 0 ? (
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

interface RecordingControlsProps {
  isStarting: boolean;
  activeRecordingId: string | null;
  isStopping: boolean;
  recordingDuration: number;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

const RecordingControls: React.FC<RecordingControlsProps> = ({
  isStarting,
  activeRecordingId,
  isStopping,
  recordingDuration,
  onStart,
  onStop,
  disabled,
}) => {
  if (isStarting) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <CircularProgress size={24} sx={{ mr: 2 }} />
        <Typography>Starting recording...</Typography>
      </Box>
    );
  }

  if (activeRecordingId) {
    return (
      <>
        <Button
          variant="contained"
          color="secondary"
          onClick={onStop}
          disabled={isStopping}
        >
          {isStopping ? 'Stopping...' : 'Stop Recording'}
        </Button>
        {!isStopping && (
          <Typography variant="body2" sx={{ ml: 2 }}>
            Recording Duration: {recordingDuration} seconds
          </Typography>
        )}
      </>
    );
  }

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={onStart}
      disabled={disabled}
    >
      Start Recording
    </Button>
  );
};

export default RouteRecordings;
