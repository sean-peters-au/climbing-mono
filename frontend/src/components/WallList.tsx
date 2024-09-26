import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Grid, Card, CardContent, Typography, CardActionArea } from '@mui/material';
import API from '../services/api';
import { Wall } from '../types';

const WallList: React.FC = () => {
  const [walls, setWalls] = useState<Wall[]>([]);

  useEffect(() => {
    const fetchWalls = async () => {
      const response = await API.get('/wall');
      setWalls(response.data['walls']);
    };
    fetchWalls();
  }, []);

  return (
    <Grid container spacing={4}>
      {walls.map((wall) => (
        <Grid item xs={12} sm={6} md={4} key={wall.id}>
          <Card>
            <CardActionArea component={Link} to={`/walls/${wall.id}`}>
              <CardContent>
                <Typography variant="h4" component="div">
                  {wall.name}
                </Typography>
                {/* Include a preview image or description if available */}
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default WallList;