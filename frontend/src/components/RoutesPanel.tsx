import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridPaginationModel,
  GridFilterModel,
  GridToolbar,
} from '@mui/x-data-grid';
import { useRoutes } from '../hooks/useRoutes';

interface RoutesPanelProps {
  wallId: string;
  holds: any[]; // Replace 'any' with your actual Hold type
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
}

const RoutesPanel: React.FC<RoutesPanelProps> = ({
  wallId,
  holds,
  selectedHolds,
  setSelectedHolds,
}) => {
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    pageSize: 5,
    page: 0,
  });
  const [filterModel, setFilterModel] = useState<GridFilterModel>({
    items: [],
  });

  const { routes, loading, error } = useRoutes(wallId);

  const handleRouteSelect = (routeId: string | null) => {
    setSelectedRouteId(routeId);
    if (routeId) {
      const selectedRoute = routes.find((route) => route.id === routeId);
      if (selectedRoute) {
        setSelectedHolds(selectedRoute.holds.map((hold) => hold.id));
        // Fetch recordings or any other data as needed
        console.log('selected route', selectedRoute);
        console.log(
          'selected route holds',
          selectedRoute.holds.map((hold) => hold.id),
        );
        console.log('selected holds', selectedHolds);
      }
    } else {
      setSelectedHolds([]);
    }
  };

  const handleClearSelection = () => {
    handleRouteSelect(null);
  };

  if (loading) {
    return <Typography>Loading routes...</Typography>;
  }

  if (error) {
    return <Typography>Error loading routes: {error}</Typography>;
  }

  if (!routes || routes.length === 0) {
    return <Typography>No routes available for this wall.</Typography>;
  }

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', flex: 1 },
    { field: 'description', headerName: 'Description', flex: 2 },
    {
      field: 'grade',
      headerName: 'Grade',
      width: 120,
      valueGetter: (params) => `V${params}`,
    },
    {
      field: 'date',
      headerName: 'Date',
      width: 120,
      valueGetter: (params) =>
        params ? new Date(params).toLocaleDateString() : '',
    },
  ];

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Routes</Typography>
        <Button
          variant="outlined"
          onClick={handleClearSelection}
          disabled={!selectedRouteId}
        >
          Clear Selection
        </Button>
      </Box>
      <DataGrid
        rows={routes}
        columns={columns}
        pagination
        paginationModel={paginationModel}
        onPaginationModelChange={(model) => setPaginationModel(model)}
        pageSizeOptions={[5, 10, 20]}
        filterModel={filterModel}
        onFilterModelChange={(model) => setFilterModel(model)}
        slots={{ toolbar: GridToolbar }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
          },
        }}
        onRowClick={(params: GridRowParams) => {
          const routeId = params.id as string;
          if (routeId === selectedRouteId) {
            handleRouteSelect(null); // Deselect if clicking the already selected route
          } else {
            handleRouteSelect(routeId);
          }
        }}
        rowSelectionModel={selectedRouteId ? [selectedRouteId] : []}
      />

      {/* Selected Route Details */}
      {selectedRouteId && (
        <Box mt={2}>
          <Typography variant="h6">Route Details</Typography>
          {routes
            .filter((route) => route.id === selectedRouteId)
            .map((route) => (
              <Box key={route.id}>
                <Typography variant="body1">
                  <strong>Name:</strong> {route.name}
                </Typography>
                <Typography variant="body1">
                  <strong>Grade:</strong> {route.grade}
                </Typography>
                <Typography variant="body1">
                  <strong>Description:</strong> {route.description}
                </Typography>
                {/* Include additional route details as needed */}
              </Box>
            ))}
        </Box>
      )}
    </Box>
  );
};

export default RoutesPanel;