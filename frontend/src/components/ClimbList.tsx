import React from 'react';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridPaginationModel,
  GridFilterModel,
  GridToolbar,
} from '@mui/x-data-grid';
import { Typography, Box, Button } from '@mui/material';
import { Climb } from '../types';
import { useTheme } from '@mui/material/styles';

interface ClimbListProps {
  climbs: Climb[];
  selectedClimbId: string | null;
  onSelectClimb: (climbId: string | null) => void;
}

const ClimbList: React.FC<ClimbListProps> = ({
  climbs,
  selectedClimbId,
  onSelectClimb,
}) => {
  const theme = useTheme();
  const [paginationModel, setPaginationModel] = React.useState<GridPaginationModel>({
    pageSize: 5,
    page: 0,
  });

  const [filterModel, setFilterModel] = React.useState<GridFilterModel>({
    items: [],
  });

  if (!climbs || climbs.length === 0) {
    return <Typography>No climbs available for this wall.</Typography>;
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

  const handleClearSelection = () => {
    onSelectClimb(null);
  };

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Climbs</Typography>
        <Button 
          variant="outlined" 
          onClick={handleClearSelection}
          disabled={!selectedClimbId}
        >
          Clear Selection
        </Button>
      </Box>
      <DataGrid
        rows={climbs}
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
          if (params.id === selectedClimbId) {
            onSelectClimb(null);  // Deselect if clicking the already selected climb
          } else {
            onSelectClimb(params.id as string);
          }
        }}
        rowSelectionModel={selectedClimbId ? [selectedClimbId] : []}
      />
    </Box>
  );
};

export default ClimbList;