import React, { useContext } from 'react';
import { BoardViewContext } from './BoardViewContext';
import { Tabs, Tab, Box } from '@mui/material';
import RoutesTab from './RoutesTab';
import BoardTab from './BoardTab';

const BoardViewPanel: React.FC = () => {
  const { selectedTab, setSelectedTab } = useContext(BoardViewContext)!;

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Box sx={{ 
      width: '100%',
      height: '90vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Tabs value={selectedTab} onChange={handleTabChange} variant="fullWidth">
        <Tab label="Routes" />
        <Tab label="Board" />
      </Tabs>
      <Box sx={{ 
        flexGrow: 1,
        overflow: 'auto',
        padding: 2
      }}>
        {selectedTab === 0 && <RoutesTab />}
        {selectedTab === 1 && <BoardTab />}
      </Box>
    </Box>
  );
};

export default BoardViewPanel;
