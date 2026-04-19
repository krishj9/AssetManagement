/**
 * Rebalance Request Page
 * Portfolio rebalance request form with validation
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { invokeSupervisor } from '@/api/endpoints';
import { PortfolioRebalanceRequest } from '@/types/schemas';
import RequestIntakeForm from '@/components/RequestIntakeForm/RequestIntakeForm';
import WorkflowStatus from '@/components/WorkflowStatus/WorkflowStatus';

export default function RebalanceRequest() {
  const navigate = useNavigate();
  const [showWorkflow, setShowWorkflow] = useState(false);

  const mutation = useMutation({
    mutationFn: invokeSupervisor,
    onSuccess: (data) => {
      console.log('Supervisor response:', data);
      setShowWorkflow(true);
      // Navigate to approval review after workflow completes
      setTimeout(() => {
        if (data.recommendation_package) {
          // In real implementation, get approval_id from created artifact
          navigate('/approval/mock-approval-id');
        }
      }, 2000);
    },
    onError: (error) => {
      console.error('Supervisor invocation failed:', error);
    },
  });

  const handleSubmit = (request: PortfolioRebalanceRequest) => {
    mutation.mutate(request);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Portfolio Rebalance Request
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Submit a portfolio rebalance request for AI-powered analysis and
        recommendations
      </Typography>

      {mutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to submit request. Please try again.
        </Alert>
      )}

      {!showWorkflow ? (
        <RequestIntakeForm
          onSubmit={handleSubmit}
          isLoading={mutation.isPending}
        />
      ) : (
        <WorkflowStatus response={mutation.data} />
      )}
    </Box>
  );
}
