/**
 * Audit Log Page
 * Query and view audit events
 */

import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';

export default function AuditLog() {
  const [requestId, setRequestId] = useState('');
  const [traceId, setTraceId] = useState('');

  const handleSearch = () => {
    console.log('Searching audit events:', { requestId, traceId });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Log
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Query and review audit events with 7-year retention
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Request ID"
              value={requestId}
              onChange={(e) => setRequestId(e.target.value)}
              placeholder="Enter request ID"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Trace ID"
              value={traceId}
              onChange={(e) => setTraceId(e.target.value)}
              placeholder="Enter trace ID"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              sx={{ height: '56px' }}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Audit Events
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Event Type</TableCell>
                <TableCell>Request ID</TableCell>
                <TableCell>Actor</TableCell>
                <TableCell>Outcome</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No audit events found. Use the search filters above to query
                    events.
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
