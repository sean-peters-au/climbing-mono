import { Box, Typography } from '@mui/material';
import React from 'react';

interface ErrorMessageProps {
  error: unknown;
}

export const QueryError: React.FC<ErrorMessageProps> = ({ error }) => {
  if (!error) {
    return null;
  }

  return (
    <Box>
      <Typography color="error">
        Error loading analysis: {error instanceof Error ? error.message : 'Unknown error occurred'}
      </Typography>
    </Box>
  );
};
