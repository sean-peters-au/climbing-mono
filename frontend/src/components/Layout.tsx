import React from 'react';
import { Box, Grid } from '@mui/material';
import Header from './Header';

interface LayoutProps {
  leftColumn: React.ReactNode;
  rightColumn: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ leftColumn, rightColumn }) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
    <Header />
    <Box sx={{ flexGrow: 1, display: 'flex', width: '100%', margin: '0 auto' }}>
      <Grid container sx={{ flexGrow: 1 }}>
        <Grid item xs={12} md={6} lg={6} sx={{ height: '100%', padding: '1rem' }}>
          {leftColumn}
        </Grid>
        <Grid item xs={12} md={6} lg={6} sx={{ height: '100%', padding: '1rem' }}>
          {rightColumn}
        </Grid>
      </Grid>
    </Box>
  </Box>
);

export default Layout;