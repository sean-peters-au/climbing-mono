import React, { useState } from 'react';
import { Box, Typography, Button } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridPaginationModel,
  GridFilterModel,
  GridToolbar,
} from '@mui/x-data-grid';
import { useRoutes } from '../../hooks/useRoutes';
import { Route } from '../../types';

interface RoutesListProps {
  wallId: string;
  selectedRoute: Route | null;
  onRouteSelect: (route: Route | null) => void;
}

const RoutesList: React.FC<RoutesListProps> = ({
  wallId,
  selectedRoute,
  onRouteSelect,
}) => {
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    pageSize: 5,
    page: 0,
  });
  const [filterModel, setFilterModel] = useState<GridFilterModel>({
    items: [],
  });

  const { routes, loading, error } = useRoutes(wallId);

  const handleRowClick = (params: GridRowParams) => {
    const routeId = params.id as string;
    if (selectedRoute && routeId === selectedRoute.id) {
      onRouteSelect(null); // Deselect if clicking the already selected route
    } else {
      const route = routes.find((route) => route.id === routeId);
      if (route) {
        onRouteSelect(route);
      }
    }
  };

  const handleClearSelection = () => {
    onRouteSelect(null);
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
    <Box sx={{ width: '100%', height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="h6">Routes</Typography>
        <Button
          variant="outlined"
          onClick={handleClearSelection}
          disabled={!selectedRoute}
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
        onRowClick={handleRowClick}
        rowSelectionModel={selectedRoute ? [selectedRoute.id] : []}
      />
    </Box>
  );
};

export default RoutesList;