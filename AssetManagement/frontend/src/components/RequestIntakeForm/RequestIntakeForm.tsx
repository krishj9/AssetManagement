/**
 * Request Intake Form Component
 * Form for submitting portfolio rebalance requests
 */

import { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Typography,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import {
  PortfolioRebalanceRequest,
  Holding,
  Allocation,
  MandateConstraint,
} from '@/types/schemas';

interface RequestIntakeFormProps {
  onSubmit: (request: PortfolioRebalanceRequest) => void;
  isLoading: boolean;
}

export default function RequestIntakeForm({
  onSubmit,
  isLoading,
}: RequestIntakeFormProps) {
  const [clientId, setClientId] = useState('');
  const [accountId, setAccountId] = useState('');
  const [cashPosition, setCashPosition] = useState('100000');
  const [investmentObjective, setInvestmentObjective] = useState('Growth');
  const [riskProfile, setRiskProfile] = useState('Moderate');
  const [actionContext, setActionContext] = useState('');

  const [holdings, setHoldings] = useState<Holding[]>([
    {
      security_id: 'AAPL',
      security_name: 'Apple Inc.',
      quantity: 100,
      current_price: 150.0,
      current_value: 15000.0,
    },
  ]);

  const [targetAllocation, setTargetAllocation] = useState<Allocation[]>([
    { security_id: 'AAPL', percentage: 30.0 },
    { security_id: 'MSFT', percentage: 30.0 },
    { security_id: 'GOOGL', percentage: 20.0 },
    { security_id: 'AMZN', percentage: 20.0 },
  ]);

  const [constraints, setConstraints] = useState<MandateConstraint[]>([
    {
      constraint_type: 'max_single_position',
      constraint_value: 35.0,
      description: 'Maximum 35% in any single position',
    },
  ]);

  const addHolding = () => {
    setHoldings([
      ...holdings,
      {
        security_id: '',
        security_name: '',
        quantity: 0,
        current_price: 0,
        current_value: 0,
      },
    ]);
  };

  const removeHolding = (index: number) => {
    setHoldings(holdings.filter((_, i) => i !== index));
  };

  const updateHolding = (index: number, field: keyof Holding, value: string | number) => {
    const updated = [...holdings];
    updated[index] = { ...updated[index], [field]: value };
    // Auto-calculate current_value
    if (field === 'quantity' || field === 'current_price') {
      updated[index].current_value =
        updated[index].quantity * updated[index].current_price;
    }
    setHoldings(updated);
  };

  const addAllocation = () => {
    setTargetAllocation([
      ...targetAllocation,
      { security_id: '', percentage: 0 },
    ]);
  };

  const removeAllocation = (index: number) => {
    setTargetAllocation(targetAllocation.filter((_, i) => i !== index));
  };

  const updateAllocation = (
    index: number,
    field: keyof Allocation,
    value: string | number
  ) => {
    const updated = [...targetAllocation];
    updated[index] = { ...updated[index], [field]: value };
    setTargetAllocation(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Calculate current allocation
    const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
    const currentAllocation: Allocation[] = holdings.map((h) => ({
      security_id: h.security_id,
      percentage: (h.current_value / totalValue) * 100,
    }));

    const request: PortfolioRebalanceRequest = {
      client_id: clientId,
      account_id: accountId,
      current_holdings: holdings,
      current_allocation: currentAllocation,
      target_allocation: targetAllocation,
      cash_position: parseFloat(cashPosition),
      investment_objective: investmentObjective,
      risk_profile: riskProfile,
      mandate_constraints: constraints,
      requested_action_context: actionContext || undefined,
      schema_version: '1.0.0',
    };

    onSubmit(request);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Client Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Client Information
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label="Client ID"
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label="Account ID"
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              required
              label="Cash Position"
              type="number"
              value={cashPosition}
              onChange={(e) => setCashPosition(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              required
              label="Investment Objective"
              value={investmentObjective}
              onChange={(e) => setInvestmentObjective(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              required
              label="Risk Profile"
              value={riskProfile}
              onChange={(e) => setRiskProfile(e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          {/* Current Holdings */}
          <Grid item xs={12}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Typography variant="h6">Current Holdings</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={addHolding}
                size="small"
              >
                Add Holding
              </Button>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Security ID</TableCell>
                    <TableCell>Security Name</TableCell>
                    <TableCell>Quantity</TableCell>
                    <TableCell>Current Price</TableCell>
                    <TableCell>Current Value</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {holdings.map((holding, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <TextField
                          size="small"
                          value={holding.security_id}
                          onChange={(e) =>
                            updateHolding(index, 'security_id', e.target.value)
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          value={holding.security_name}
                          onChange={(e) =>
                            updateHolding(index, 'security_name', e.target.value)
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          type="number"
                          value={holding.quantity}
                          onChange={(e) =>
                            updateHolding(
                              index,
                              'quantity',
                              parseFloat(e.target.value)
                            )
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          type="number"
                          value={holding.current_price}
                          onChange={(e) =>
                            updateHolding(
                              index,
                              'current_price',
                              parseFloat(e.target.value)
                            )
                          }
                        />
                      </TableCell>
                      <TableCell>${holding.current_value.toFixed(2)}</TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => removeHolding(index)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          {/* Target Allocation */}
          <Grid item xs={12}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Typography variant="h6">Target Allocation</Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={addAllocation}
                size="small"
              >
                Add Allocation
              </Button>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Security ID</TableCell>
                    <TableCell>Target Percentage</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {targetAllocation.map((allocation, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <TextField
                          size="small"
                          value={allocation.security_id}
                          onChange={(e) =>
                            updateAllocation(index, 'security_id', e.target.value)
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          type="number"
                          value={allocation.percentage}
                          onChange={(e) =>
                            updateAllocation(
                              index,
                              'percentage',
                              parseFloat(e.target.value)
                            )
                          }
                          InputProps={{ endAdornment: '%' }}
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => removeAllocation(index)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Additional Context (Optional)"
              value={actionContext}
              onChange={(e) => setActionContext(e.target.value)}
              placeholder="Provide any additional context for this rebalance request..."
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button variant="outlined" disabled={isLoading}>
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading}
                size="large"
              >
                {isLoading ? 'Submitting...' : 'Submit Request'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
}
