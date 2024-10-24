import { createTheme } from '@mui/material/styles';
import '@mui/x-data-grid/themeAugmentation';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#111111',
    },
    secondary: {
      main: '#ffffff',
    },
    background: {
      default: '#fcfcfc',
      paper: '#fefefe',
    },
    text: {
      primary: '#111111',
      secondary: '#222222',
    },
  },
  typography: {
    fontSize: 18,
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '3rem' },
    h2: { fontSize: '2.5rem' },
    h3: { fontSize: '2.3rem' },
    h4: { fontSize: '2rem' },
    h5: { fontSize: '1.8rem' },
    h6: { fontSize: '1.5rem' },
    body1: { fontSize: '1.2rem' },
    body2: { fontSize: '1.1rem' },
    button: { fontSize: '1.1rem' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontSize: '1.1rem',
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
        },
      },
    },
    MuiAccordion: {
      styleOverrides: {
        root: {
          border: '3px solid #a2a2a2',
          '&:before': {
            display: 'none',
          },
          '&.Mui-expanded': {
            border: '3px solid #111111'
          },
        },
      },
    },
    MuiAccordionSummary: {
      styleOverrides: {
        root: {
          margin: '-2px',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          border: '3px solid #a2a2a2',
          '&:hover': {
            backgroundColor: '#eeeeee',
          },
          '&.Mui-expanded': {
            backgroundColor: '#e0e0e0',
            border: '3px solid #111111',
          },
        },
        content: {
          margin: '12px 0',
        },
      },
    },
    MuiAccordionDetails: {
      styleOverrides: {
        root: {
          padding: '16px 24px 24px',
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: '2px solid #111111',
          '& .MuiDataGrid-columnSeparator': {
            color: '#111111',
          },
          '& .MuiDataGrid-menuIcon': {
            '& .MuiSvgIcon-root': {
              color: '#111111',
            },
          },
          '& .MuiDataGrid-toolbarContainer': {
            borderBottom: '2px solid #111111',
            padding: '8px',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '3px solid #a2a2a2',
          '& .MuiTabs-indicator': {
            height: 3,
            backgroundColor: '#111111',
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontSize: '1.5rem',
          color: '#555555',
          borderRadius: '8px',
          border: '3px solid #a2a2a2',
          margin: '-2px',
          '&:hover': {
            backgroundColor: '#d5d5d5',
          },
          '&.Mui-selected': {
            color: '#ffffff',
            backgroundColor: '#111111',
            border: '3px solid #111111',
            borderBottom: 'none',
          },
        },
      },
    },
  },
});

export default theme;
