import React from 'react';
import { Grid, Box } from '@mui/material';
import WallImage from '../components/BoardView/WallImage';
import { useParams } from 'react-router-dom';
import { useWall } from '../hooks/useWall';
import Header from '../components/Header';
import { BoardViewProvider } from '../components/BoardView/BoardViewContext';
import BoardViewPanel from '../components/BoardView';

const BoardView: React.FC = () => {
  const { wallId } = useParams<{ wallId: string }>();
  const { data: wall, isLoading } = useWall(wallId!);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!wall) {
    return <div>Wall not found</div>;
  }

  return (
    <BoardViewProvider wall={wall}>
      <Box>
        <Header />
        <Grid container sx={{ height: '90vh' }}>
          {/* Left Section: Wall Image with Border */}
          <Grid item xs={12} md={8}>
            <Box
              position="relative"
              sx={{
                height: '100%',
                border: 10,
                borderRadius: 5,
                borderColor: 'black',
                margin: 2,
              }}
            >
              <WallImage />
            </Box>
          </Grid>

          {/* Right Section: BoardViewPanel with Border */}
          <Grid item xs={12} md={4}>
            <Box
              sx={{
                borderColor: 'black',
                height: '100%',
                overflowY: 'hidden',
                borderRadius: 5,
                border: 10,
                margin: 2,
              }}
            >
              <BoardViewPanel />
            </Box>
          </Grid>
        </Grid>
      </Box>
    </BoardViewProvider>
  );
};

export default BoardView;