/**
 * Dashboard Page
 */

import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

export default function Dashboard() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Portfolio Rebalancing',
      description:
        'Submit portfolio rebalance requests with AI-powered recommendations',
      icon: <AccountBalanceIcon sx={{ fontSize: 48 }} />,
      action: () => navigate('/rebalance'),
      buttonText: 'New Rebalance',
    },
    {
      title: 'Multi-Agent Analysis',
      description:
        'Research, compliance, memory, and execution agents working together',
      icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
      action: () => {},
      buttonText: 'Learn More',
    },
    {
      title: 'Compliance & Risk',
      description:
        'Automated mandate checking and risk metrics calculation',
      icon: <SecurityIcon sx={{ fontSize: 48 }} />,
      action: () => {},
      buttonText: 'View Policies',
    },
    {
      title: 'Audit Trail',
      description:
        'Complete audit logging with 7-year retention for compliance',
      icon: <SpeedIcon sx={{ fontSize: 48 }} />,
      action: () => navigate('/audit'),
      buttonText: 'View Audit Log',
    },
  ];

  return (
    <Box>
      <Typography variant="h3" gutterBottom>
        Welcome to Portfolio Platform
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Autonomous Portfolio Construction and Rebalancing powered by Amazon
        Bedrock Multi-Agent System
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <Box
                  sx={{
                    color: 'primary.main',
                    mb: 2,
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button
                  variant="contained"
                  onClick={feature.action}
                  size="small"
                >
                  {feature.buttonText}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h5" gutterBottom>
          System Architecture
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          The platform uses a Bedrock-native hierarchical multi-agent system
          with:
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Supervisor Agent</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Orchestrates workflow and consolidates outputs from collaborator
              agents
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Research Agent</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Retrieves market data and generates sentiment analysis
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Memory & Personalization Agent</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Manages client preferences and long-term memory
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Risk & Compliance Agent</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Evaluates portfolio drift and mandate compliance
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Execution Agent</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Generates trade proposals with cost and tax impact
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Bedrock Guardrails</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Content filtering, PII protection, and grounding checks
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
