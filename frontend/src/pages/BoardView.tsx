import React, { useState } from "react";
import { Grid, Box, Button } from "@mui/material";
import WallImage from "../components/WallImage";
import BoardViewPanel from "../components/BoardViewPanel/BoardViewPanel";
import { useParams } from "react-router-dom";
import useWall from "../hooks/useWall";
import { SensorReadingFrame } from "../types";
import Header from "../components/Header";

const BoardView: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [showAllHolds, setShowAllHolds] = useState(false);
  const [selectedHolds, setSelectedHolds] = useState<string[]>([]);
  const [playbackData, setPlaybackData] = useState<SensorReadingFrame[] | null>(
    null
  );
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
    return <div>Error: {error || "Wall not found"}</div>;
  }

  return (
    <Box>
      <Header />
      <Grid container sx={{ height: "90vh" }}>
        {/* Left Section: Wall Image with Border */}
        <Grid item xs={12} md={8}>
          <Box
            position="relative"
            sx={{
              height: "100%",
              border: 10,
              borderRadius: 5,
              borderColor: "black",
              margin: 2,
            }}
          >
            <WallImage
              wall={wall}
              holds={wall.holds}
              selectedHolds={selectedHolds}
              showAllHolds={showAllHolds}
              onHoldClick={handleHoldClick}
              climbHoldIds={[]} // Pass climb hold IDs if needed
              playbackData={playbackData || []}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={toggleShowAllHolds}
              style={{ position: "absolute", top: 16, right: 16 }}
            >
              {showAllHolds ? "Hide All Holds" : "Show All Holds"}
            </Button>
          </Box>
        </Grid>

        {/* Right Section: BoardViewPanel with Border */}
        <Grid item xs={12} md={4}>
          <Box
            sx={{
              borderColor: "black",
              height: "100%",
              overflowY: "hidden",
              borderRadius: 5,
              border: 10,
              margin: 2,
            }}
          >
            <BoardViewPanel
              selectedTab={selectedTab}
              handleTabChange={handleTabChange}
              selectedHolds={selectedHolds}
              setSelectedHolds={setSelectedHolds}
              setPlaybackData={setPlaybackData}
              wall={wall}
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BoardView;
