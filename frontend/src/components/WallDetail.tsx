import React, { useState } from 'react';
import { Grid, Tabs, Tab, Box, Button } from '@mui/material';
import WallImage from './WallImage';
import RoutesPanel from './RoutesPanel';
import CreateRoutePanel from './CreateRoutePanel';
import BoardPanel from './BoardPanel';
import { useParams } from 'react-router-dom';
import useWall from '../hooks/useWall';

const WallDetail: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [showAllHolds, setShowAllHolds] = useState(false);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const { wallId } = useParams<{ wallId: string }>();
  const { wall, loading, error } = useWall(wallId!);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const toggleShowAllHolds = () => {
    setShowAllHolds((prev) => !prev);
  };

  const handleHoldClick = (holdId: string) => {
    if (selectedHolds.includes(holdId)) {
      setSelectedHolds(selectedHolds.filter((id) => id !== holdId));
    } else {
      setSelectedHolds([...selectedHolds, holdId]);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error || !wall) {
    return <div>Error: {error || 'Wall not found'}</div>;
  }

  return (
    <Grid container>
      {/* Left Section: Wall Image */}
      <Grid item xs={12} md={8}>
        <Box position="relative">
          <WallImage
            wall={wall}
            holds={wall.holds}
            selectedHolds={selectedHolds}
            showAllHolds={showAllHolds}
            onHoldClick={handleHoldClick}
            climbHoldIds={[]} // Pass climb hold IDs if needed
          />
          <Button
            variant="contained"
            color="primary"
            onClick={toggleShowAllHolds}
            style={{ position: 'absolute', top: 16, right: 16 }}
          >
            {showAllHolds ? 'Hide All Holds' : 'Show All Holds'}
          </Button>
        </Box>
      </Grid>

      {/* Right Section: Panel with Tabs */}
      <Grid item xs={12} md={4}>
        <Box
          sx={{
            borderLeft: 1,
            borderColor: 'divider',
            height: '100vh',
            overflowY: 'auto',
          }}
        >
          {/* Tabs */}
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Routes" />
            <Tab label="Create Route" />
            <Tab label="Board" />
          </Tabs>

          {/* Tab Panels */}
          <Box p={2}>
            {selectedTab === 0 && (
              <RoutesPanel
                wallId={wall.id}
                holds={wall.holds}
                setSelectedHolds={setSelectedHolds}
                selectedHolds={selectedHolds}
              />
            )}
            {selectedTab === 1 && (
              <CreateRoutePanel
                wallId={wall.id}
                selectedHolds={selectedHolds}
                setSelectedHolds={setSelectedHolds}
              />
            )}
            {selectedTab === 2 && <BoardPanel wall={wall} />}
          </Box>
        </Box>
      </Grid>
    </Grid>
  );
};

export default WallDetail;