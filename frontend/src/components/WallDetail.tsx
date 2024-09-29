import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Button, Paper, Tabs, Tab, Box } from '@mui/material';
import Layout from '../components/Layout';
import useWall from '../hooks/useWall';
import useClimbs from '../hooks/useClimbs';
import ClimbList from '../components/ClimbList';
import ClimbCreate from '../components/ClimbCreate';
import HoldOverlay from '../components/HoldOverlay';
import ErrorMessage from '../components/ErrorMessage';
import LoadingAnimation from '../components/LoadingAnimation';
import { Point } from '../types';
import API from '../services/api';

const WallDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { wall, loading: wallLoading, error: wallError } = useWall(id!);
  const { climbs, loading: climbsLoading, error: climbsError } = useClimbs(id!);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [showAllHolds, setShowAllHolds] = useState<boolean>(false);
  const [selectedClimbId, setSelectedClimbId] = useState<string | null>(null);
  const [tabIndex, setTabIndex] = useState(0);
  const [identifyMissingHoldMode, setIdentifyMissingHoldMode] = useState(false);

  if (wallLoading || climbsLoading) {
    return <LoadingAnimation message="Loading wall details..." />;
  }

  if (wallError || !wall) {
    return <ErrorMessage message={wallError || 'Wall not found.'} />;
  }

  const handleHoldClick = (holdId: string) => {
    setSelectedHolds((prevSelected) =>
      prevSelected.includes(holdId)
        ? prevSelected.filter((id) => id !== holdId)
        : [...prevSelected, holdId]
    );
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabIndex(newValue);
  };

  const handleMissingHoldClick = (coords: Point) => {
    // Send POST request to backend API
    API.post(`/wall/${wall.id}/hold`, { x: coords.x, y: coords.y })
      .then((response) => {
        // Refresh wall data or update holds
        setIdentifyMissingHoldMode(false);
        // Optionally fetch updated holds
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const selectedClimb = climbs.find((climb) => climb.id === selectedClimbId);

  const leftColumn = (
    <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
      <Button
        variant="contained"
        color="primary"
        onClick={() => setShowAllHolds(!showAllHolds)}
        sx={{ mb: 2 }}
      >
        {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
      </Button>
      <HoldOverlay
        wall={wall}
        holds={wall.holds}
        selectedHolds={selectedHolds}
        showAllHolds={showAllHolds}
        climbHoldIds={selectedClimb?.hold_ids || []}
        onHoldClick={handleHoldClick}
        onMissingHoldClick={handleMissingHoldClick}
        missingHoldMode={identifyMissingHoldMode}
      />
      <Button variant="outlined" onClick={() => setSelectedHolds([])} sx={{ mt: 2 }}>
        Reset Hold Selection
      </Button>
    </Paper>
  );

  const rightColumn = (
    <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
      <Tabs value={tabIndex} onChange={handleTabChange}>
        <Tab label="Routes" />
        <Tab label="Create Route" />
        <Tab label="Board" />
      </Tabs>

      {tabIndex === 0 && (
        <Box>
          <Typography variant="h4" gutterBottom>
            Climbs
          </Typography>
          {climbsError ? (
            <ErrorMessage message={climbsError} />
          ) : (
            <ClimbList
              climbs={climbs}
              selectedClimbId={selectedClimbId}
              onSelectClimb={setSelectedClimbId}
            />
          )}
        </Box>
      )}

      {tabIndex === 1 && (
        <Box>
          <ClimbCreate wallId={wall.id} selectedHolds={selectedHolds} />
        </Box>
      )}

      {tabIndex === 2 && (
        <Box>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setIdentifyMissingHoldMode(true)}
            sx={{ mb: 2 }}
          >
            Identify Missing Hold
          </Button>

          {identifyMissingHoldMode && (
            <Typography variant="body1" sx={{ mb: 2 }}>
              Please click where the missing hold is on the wall image.
            </Typography>
          )}
        </Box>
      )}
    </Paper>
  );

  return <Layout leftColumn={leftColumn} rightColumn={rightColumn} />;
};

export default WallDetail;