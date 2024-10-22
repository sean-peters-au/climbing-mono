import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const Header: React.FC = () => (
  <AppBar position="static">
    <Toolbar>
      <Typography
        variant="h4"
        component="div"
        sx={{
          flexGrow: 1,
          fontSize: '2.5rem',
          padding: '0.75rem',
        }}
      >
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
          Beta Board
        </Link>
      </Typography>
      <Button color="inherit" component={Link} to="/walls">
        Walls
      </Button>
      <Button color="inherit" component={Link} to="/walls/new">
        Create Wall
      </Button>
    </Toolbar>
  </AppBar>
);

export default Header;
