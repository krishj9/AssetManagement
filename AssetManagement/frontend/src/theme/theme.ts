/**
 * Material-UI Theme Configuration
 * Dark mode finance-style theme
 */

import { createTheme, ThemeOptions } from '@mui/material/styles';

// Color palette for financial application
const colors = {
  primary: {
    main: '#1976d2', // Blue
    light: '#42a5f5',
    dark: '#1565c0',
  },
  secondary: {
    main: '#9c27b0', // Purple
    light: '#ba68c8',
    dark: '#7b1fa2',
  },
  success: {
    main: '#2e7d32', // Green
    light: '#4caf50',
    dark: '#1b5e20',
  },
  error: {
    main: '#d32f2f', // Red
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02', // Orange
    light: '#ff9800',
    dark: '#e65100',
  },
  info: {
    main: '#0288d1', // Light Blue
    light: '#03a9f4',
    dark: '#01579b',
  },
  background: {
    default: '#0a1929', // Dark blue-grey
    paper: '#132f4c', // Slightly lighter blue-grey
  },
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.7)',
    disabled: 'rgba(255, 255, 255, 0.5)',
  },
};

// Workflow state colors
export const workflowStateColors = {
  NORMAL: colors.success.main,
  DEGRADED: colors.warning.main,
  LOW_CONFIDENCE: colors.info.main,
  BLOCKED: colors.error.main,
};

// Approval status colors
export const approvalStatusColors = {
  PENDING: colors.warning.main,
  APPROVED: colors.success.main,
  REJECTED: colors.error.main,
  REVISION_REQUESTED: colors.info.main,
};

// Compliance verdict colors
export const complianceVerdictColors = {
  COMPLIANT: colors.success.main,
  NON_COMPLIANT: colors.error.main,
  UNRESOLVED: colors.warning.main,
};

const themeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    ...colors,
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01562em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.00833em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '0em',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '0.00735em',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      letterSpacing: '0em',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      letterSpacing: '0.0075em',
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 400,
      letterSpacing: '0.00938em',
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      letterSpacing: '0.00714em',
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      letterSpacing: '0.00938em',
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      letterSpacing: '0.01071em',
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      letterSpacing: '0.02857em',
      textTransform: 'uppercase',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      letterSpacing: '0.03333em',
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 400,
      letterSpacing: '0.08333em',
      textTransform: 'uppercase',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.2)',
        },
        elevation2: {
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)',
        },
        elevation3: {
          boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
        },
        head: {
          fontWeight: 600,
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
        },
      },
    },
  },
};

const theme = createTheme(themeOptions);

export default theme;
