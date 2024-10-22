import React from "react";
import { Box, Tabs, Tab } from "@mui/material";
import RoutesPanel from "./RoutesTab/RoutesPanel";
import BoardPanel from "./BoardTab/BoardPanel";
import { SensorReadingFrame, Wall } from "../../types";

interface BoardViewPanelProps {
  selectedTab: number;
  handleTabChange: (event: React.SyntheticEvent, newValue: number) => void;
  selectedHolds: string[];
  setSelectedHolds: React.Dispatch<React.SetStateAction<string[]>>;
  setPlaybackData: React.Dispatch<React.SetStateAction<SensorReadingFrame[] | null>>;
  wall: Wall;
}

const BoardViewPanel: React.FC<BoardViewPanelProps> = ({
  selectedTab,
  handleTabChange,
  selectedHolds,
  setSelectedHolds,
  setPlaybackData,
  wall,
}) => {
  return (
    <Box
      sx={{
        borderLeft: 1,
        borderColor: "divider",
        height: "100%",
        overflowY: "hidden",
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
        <Tab label="Routes" sx={{ fontSize: "1.5rem" }} />
        <Tab label="Board" sx={{ fontSize: "1.5rem" }} />
      </Tabs>

      {/* Tab Panels */}
      <Box p={2} sx={{ height: "calc(100% - 48px)", overflowY: "auto" }}>
        {selectedTab === 0 && (
          <RoutesPanel
            wallId={wall.id}
            holds={wall.holds}
            setSelectedHolds={setSelectedHolds}
            selectedHolds={selectedHolds}
            setPlaybackData={setPlaybackData}
          />
        )}
        {selectedTab === 1 && <BoardPanel wall={wall} />}
      </Box>
    </Box>
  );
};

export default BoardViewPanel;