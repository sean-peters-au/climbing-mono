import React, { useState, useContext } from 'react';
import {
  Box,
  Typography,
  Button,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridToolbarQuickFilter,
  GridToolbarFilterButton,
  GridToolbarContainer,
  GridActionsCellItem,
} from '@mui/x-data-grid';
import { useRoutes, useUpdateRoute } from '../../../hooks/useRoutes';
import { Route } from '../../../types';
import RouteCreate from './RouteCreate';
import { QueryError } from '../../QueryError';
import { BoardViewContext } from '../BoardViewContext';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';

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
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [isEditingHolds, setIsEditingHolds] = useState(false);

  const { data: routes, isLoading, error } = useRoutes(wallId);
  const updateRouteMutation = useUpdateRoute();

  const {
    setSelectedHolds,
    selectedHolds,
    setSelectedRoute,
  } = useContext(BoardViewContext)!;

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
    setIsEditingHolds(false);
  };

  const handleCreateRoute = () => {
    setOpenCreateDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenCreateDialog(false);
  };

  const handleEditHolds = () => {
    if (selectedRoute) {
      // Set the selected holds to the route's holds
      setSelectedHolds(selectedRoute.holds.map((hold) => hold.id));
      setIsEditingHolds(true);
    }
  };

  const handleSaveHolds = async () => {
    if (selectedRoute) {
      // Prepare updated route data
      const updatedRoute = {
        name: selectedRoute.name,
        description: selectedRoute.description,
        grade: selectedRoute.grade,
        date: selectedRoute.date,
        hold_ids: selectedHolds,
      };

      await updateRouteMutation.mutateAsync({
        wallId,
        routeId: selectedRoute.id,
        routeData: updatedRoute,
      });

      setIsEditingHolds(false);
      // Refresh the selected route with updated holds
      setSelectedRoute({
        ...selectedRoute,
        ...updatedRoute,
      });
    }
  };

  const isRouteSelected = Boolean(selectedRoute);

  const handleProcessRowUpdate = async (newRow: Route) => {
    // Find the existing route data
    const existingRoute = routes.find((route) => route.id === newRow.id);
    if (!existingRoute) {
      console.error('Existing route not found');
      return newRow;
    }

    // Prepare the updated route data
    const updatedRouteData = {
      name: newRow.name,
      description: newRow.description,
      grade: newRow.grade,
      date: newRow.date,
      hold_ids: existingRoute.holds.map((hold) => hold.id),
    };

    // Send the update request
    try {
      await updateRouteMutation.mutateAsync({
        wallId: wallId,
        routeId: newRow.id,
        routeData: updatedRouteData,
      });
    } catch (error) {
      console.error('Error updating route:', error);
    }

    return newRow;
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      flex: 2,
      editable: true,
    },
    {
      field: 'description',
      headerName: 'Description',
      flex: 2,
      editable: true,
    },
    {
      field: 'grade',
      headerName: 'Grade',
      type: 'number',
      width: 120,
      editable: true,
      valueFormatter: (params) => `V${params}`,
    },
    {
      field: 'date',
      headerName: 'Date',
      width: 150,
      editable: true,
      type: 'date',
      valueGetter: (params) =>
        params ? new Date(params) : null,
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 120,
      getActions: (params) => {
        if (selectedRoute?.id === params.id) {
          return isEditingHolds ? [
            <GridActionsCellItem
              icon={<SaveIcon />}
              label="Save Holds"
              onClick={handleSaveHolds}
            />
          ] : [
            <GridActionsCellItem
              icon={<EditIcon />}
              label="Edit Holds"
              onClick={handleEditHolds}
            />
          ];
        }
        return [];
      },
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
        initialState={{
          sorting: {
            sortModel: [{ field: 'date', sort: 'desc' }],
          },
        }}
        autoHeight={false}
        slots={{ toolbar: RoutesListToolbar }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
          },
        }}
        onRowClick={handleRowClick}
        rowSelectionModel={selectedRoute ? [selectedRoute.id] : []}
        editMode="cell"
        processRowUpdate={handleProcessRowUpdate}
        onProcessRowUpdateError={(error) => {
          console.error('Error updating row:', error);
        }}
      />
      <RouteCreate open={openCreateDialog} onClose={handleCloseDialog} />
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
