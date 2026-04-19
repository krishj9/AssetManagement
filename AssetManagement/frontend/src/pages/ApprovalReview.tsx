/**
 * Approval Review Page
 * Review and approve/reject portfolio rebalance recommendations
 */

import { useParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';

export default function ApprovalReview() {
  const { approvalId } = useParams<{ approvalId: string }>();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Approval Review
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Review recommendation package and approve or reject
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Approval ID: {approvalId}
      </Alert>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recommendation Summary
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This page will display the complete recommendation package including:
        </Typography>
        <ul>
          <li>Trade proposals with rationale and evidence</li>
          <li>Compliance verdict and risk metrics</li>
          <li>Memory summary and client preferences</li>
          <li>Allocation comparison (current vs. target vs. proposed)</li>
          <li>Estimated costs and tax impacts</li>
        </ul>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Approval Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckCircleIcon />}
              size="large"
            >
              Approve
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              color="error"
              startIcon={<CancelIcon />}
              size="large"
            >
              Reject
            </Button>
          </Grid>
          <Grid item>
            <Button variant="outlined" size="large">
              Request Revision
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
