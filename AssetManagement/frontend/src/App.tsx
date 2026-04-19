/**
 * Main App Component
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import theme from './theme/theme';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import RebalanceRequest from './pages/RebalanceRequest';
import ApprovalReview from './pages/ApprovalReview';
import AuditLog from './pages/AuditLog';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/rebalance" element={<RebalanceRequest />} />
              <Route path="/approval/:approvalId" element={<ApprovalReview />} />
              <Route path="/audit" element={<AuditLog />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
