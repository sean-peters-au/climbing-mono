import React from 'react';
import {
  DataGrid,
  GridColDef,
  GridRowParams,
  GridPaginationModel,
  GridFilterModel,
  GridToolbar,
} from '@mui/x-data-grid';
import { Typography, Box } from '@mui/material';
import { Climb } from '../types';

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
  const [paginationModel, setPaginationModel] = React.useState<GridPaginationModel>({
    pageSize: 10,
    page: 0,
  });

  // Add this new state for filtering
  const [filterModel, setFilterModel] = React.useState<GridFilterModel>({
    items: [],
  });

  if (!climbs || climbs.length === 0) {
    return <Typography>No climbs available for this wall.</Typography>;
  }

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', flex: 1, filterable: true },
    { field: 'description', headerName: 'Description', flex: 2, filterable: true },
    {
      field: 'grade',
      headerName: 'Grade',
      type: 'number',
      width: 120,
      filterable: true,
      valueGetter: (params) => {
        return `V${params}`;
      },
    },
    {
      field: 'date',
      headerName: 'Date',
      type: 'date',
      width: 120,
      filterable: true,
      valueGetter: (params) =>
        params ? new Date(params) : new Date(),
    },
  ];

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <DataGrid
        rows={climbs}
        columns={columns}
        pagination
        paginationModel={paginationModel}
        onPaginationModelChange={(model) => setPaginationModel(model)}
        pageSizeOptions={[5, 10, 20]}
        disableRowSelectionOnClick
        onRowClick={(params: GridRowParams) => onSelectClimb(params.row.id)}
        rowSelectionModel={selectedClimbId ? [selectedClimbId] : []}
        filterModel={filterModel}
        onFilterModelChange={(model) => setFilterModel(model)}
        slots={{ toolbar: GridToolbar }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
          },
        }}
      />
    </Box>
  );
};

export default ClimbList;