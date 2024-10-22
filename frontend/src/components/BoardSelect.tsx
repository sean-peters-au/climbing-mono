import React, { useEffect, useState } from 'react';
import { TextField, Autocomplete } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import { Wall } from '../types'; // Corrected import

const BoardSelect: React.FC = () => {
  const [walls, setWalls] = useState<Wall[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBoards = async () => {
      const response = await API.get('/wall');
      setWalls(response.data['walls']);
    };
    fetchBoards();
  }, []);

  return (
    <Autocomplete
      options={walls}
      getOptionLabel={(option) => option.name}
      onChange={(event, value) => {
        if (value) {
          navigate(`/walls/${value.id}`);
        }
      }}
      slotProps={{
        paper: {
          sx: {
            '& .MuiAutocomplete-listbox': {
              '& .MuiAutocomplete-option': {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                fontSize: '1.75rem',
              },
            },
          },
        },
      }}
      sx={{
        width: 500, // Increase width
        '& .MuiInputBase-root': {
          border: '1px solid #ccc', // Light border
          borderRadius: '10px',
          padding: '8px', // Add padding for better appearance
        },
        '& .MuiInputBase-input': {
          fontSize: '2rem', // Larger font size
          textAlign: 'center', // Center text
        },
        '& .MuiInputLabel-root': {
          fontSize: '2rem', // Larger font size for label
          textAlign: 'center', // Center label
        },
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Select Board..."
          variant="outlined"
          InputLabelProps={{
            shrink: false
          }}
        />
      )}
    />
  );
};

export default BoardSelect;