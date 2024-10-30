import React, { useState } from 'react';
import { Box, Typography, Button, Stack, CircularProgress } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridPaginationModel,
  GridFilterModel,
  GridToolbarQuickFilter,
  GridToolbarFilterButton,
  GridToolbarContainer,
} from '@mui/x-data-grid';
import { useRoutes } from '../../../hooks/useRoutes';
import { Route } from '../../../types';
import RouteCreate from './RouteCreate';
import { QueryError } from '../../QueryError';

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
  const [openCreateDialog, setOpenCreateDialog] = useState(false);

  const { data: routes, isLoading, error } = useRoutes(wallId);

  if (isLoading) {
    return <CircularProgress />;
  }

  if (!routes) {
    return <Typography>No routes found.</Typography>;
  }

  if (error) {
    return <QueryError error={error} />;
  }

  const handleRowClick = (params: GridRowParams) => {
    const routeId = params.id as string;
    if (selectedRoute && routeId === selectedRoute.id) {
      onRouteSelect(null); // Deselect if clicking the already selected route
    } else {
      const route = routes?.find((route) => route.id === routeId);
      if (route) {
        onRouteSelect(route);
      }
    }
  };

  const handleClearSelection = () => {
    onRouteSelect(null);
  };

  const handleCreateRoute = () => {
    setOpenCreateDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenCreateDialog(false);
  };

  const isRouteSelected = Boolean(selectedRoute);

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', flex: 2 },
    { field: 'description', headerName: 'Description', flex: 2 },
    {
      field: 'grade',
      headerName: 'Grade',
      type: 'number',
      width: 120,
      valueGetter: (param) => `V${param}`,
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
      <Stack direction="row" justifyContent="space-between" mb={1}>
        <Typography variant="h6">Routes</Typography>
        <Stack direction="row" spacing={1}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleCreateRoute}
            disabled={isRouteSelected}
            sx={{
              '&.Mui-disabled': {
                backgroundColor: '#bdbdbd',
                color: '#757575',
              },
            }}
          >
            Create Route
          </Button>
          <Button
            variant="outlined"
            onClick={handleClearSelection}
            disabled={!isRouteSelected}
            sx={{
              '&.Mui-disabled': {
                borderColor: '#bdbdbd',
                color: '#757575',
              },
            }}
          >
            Clear Selection
          </Button>
        </Stack>
      </Stack>
      <DataGrid
        rows={routes}
        columns={columns}
        pagination
        paginationModel={paginationModel}
        onPaginationModelChange={(model) => setPaginationModel(model)}
        pageSizeOptions={[5, 10, 20]}
        filterModel={filterModel}
        onFilterModelChange={(model) => setFilterModel(model)}
        slots={{ toolbar: RoutesListToolbar }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
          },
        }}
        onRowClick={handleRowClick}
        rowSelectionModel={selectedRoute ? [selectedRoute.id] : []}
        // compact

      />
      <RouteCreate
        open={openCreateDialog}
        onClose={handleCloseDialog}
      />
    </Box>
  );
};

const RoutesListToolbar = () => {
  // Just the quick filter and the filter button
  return (
    <GridToolbarContainer>
      <GridToolbarFilterButton />
      <GridToolbarQuickFilter />
    </GridToolbarContainer>
  );
};

export default RoutesList;
