import { createTheme } from '@mui/material/styles';

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
  },
});

export default theme;