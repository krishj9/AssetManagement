/**
 * Workflow Status Component
 * Displays real-time workflow progress and agent status
 */

import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Chip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { SupervisorResponse, WorkflowState } from '@/types/schemas';
import { workflowStateColors } from '@/theme/theme';

interface WorkflowStatusProps {
  response?: SupervisorResponse;
}

const steps = [
  'Request Received',
  'Research Analysis',
  'Memory Retrieval',
  'Compliance Check',
  'Trade Proposal',
  'Recommendation Ready',
];

export default function WorkflowStatus({ response }: WorkflowStatusProps) {
  if (!response) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Processing Request...
        </Typography>
        <LinearProgress sx={{ mt: 2 }} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          The supervisor agent is coordinating with collaborator agents to
          analyze your portfolio rebalance request.
        </Typography>
      </Paper>
    );
  }

  const getWorkflowStateIcon = (state: WorkflowState) => {
    switch (state) {
      case WorkflowState.NORMAL:
        return <CheckCircleIcon color="success" />;
      case WorkflowState.DEGRADED:
        return <WarningIcon color="warning" />;
      case WorkflowState.LOW_CONFIDENCE:
        return <WarningIcon color="info" />;
      case WorkflowState.BLOCKED:
        return <ErrorIcon color="error" />;
      default:
        return null;
    }
  };

  const getWorkflowStateMessage = (state: WorkflowState) => {
    switch (state) {
      case WorkflowState.NORMAL:
        return 'All agents completed successfully. Recommendation is ready for review.';
      case WorkflowState.DEGRADED:
        return 'Some non-critical information is missing or stale, but recommendation is available for review.';
      case WorkflowState.LOW_CONFIDENCE:
        return 'Recommendation quality is below preferred thresholds. Review with caution.';
      case WorkflowState.BLOCKED:
        return 'Critical controls are unresolved. Approval is not allowed.';
      default:
        return '';
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography variant="h6">Workflow Status</Typography>
          <Chip
            icon={getWorkflowStateIcon(response.workflow_state)}
            label={response.workflow_state}
            sx={{
              backgroundColor: workflowStateColors[response.workflow_state],
              color: 'white',
              fontWeight: 600,
            }}
          />
        </Box>

        <Stepper activeStep={steps.length} alternativeLabel>
          {steps.map((label) => (
            <Step key={label} completed>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Alert
          severity={
            response.workflow_state === WorkflowState.NORMAL
              ? 'success'
              : response.workflow_state === WorkflowState.BLOCKED
              ? 'error'
              : 'warning'
          }
          sx={{ mt: 3 }}
        >
          {getWorkflowStateMessage(response.workflow_state)}
        </Alert>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Metadata
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Request ID
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              {response.request_id}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Trace ID
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              {response.trace_id}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Agent Version
            </Typography>
            <Typography variant="body2">{response.agent_version}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Policy Version
            </Typography>
            <Typography variant="body2">{response.policy_version}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Schema Version
            </Typography>
            <Typography variant="body2">{response.schema_version}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Timestamp
            </Typography>
            <Typography variant="body2">
              {new Date(response.timestamp).toLocaleString()}
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
