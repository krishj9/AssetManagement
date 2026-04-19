# Portfolio Platform - React Frontend

Modern React frontend for the Bedrock Multi-Agent Portfolio Platform with Material-UI dark mode theme.

## Features

- ✅ **React 18** with TypeScript
- ✅ **Material-UI (MUI)** with dark mode finance-style theme
- ✅ **Vite** for fast development and building
- ✅ **React Router** for navigation
- ✅ **TanStack Query** for API state management
- ✅ **Axios** for API client with interceptors
- ✅ **Recharts** for data visualization
- ✅ **TypeScript types** generated from Pydantic schemas
- ✅ **Responsive design** for desktop, tablet, and mobile

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # API client and endpoints
│   │   ├── client.ts           # Axios instance with interceptors
│   │   └── endpoints.ts        # API endpoint functions
│   ├── components/             # Reusable components
│   │   ├── Layout/             # Main layout with navigation
│   │   ├── RequestIntakeForm/  # Portfolio rebalance request form
│   │   └── WorkflowStatus/     # Workflow progress display
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx       # Dashboard page
│   │   ├── RebalanceRequest.tsx # Rebalance request page
│   │   ├── ApprovalReview.tsx  # Approval review page
│   │   └── AuditLog.tsx        # Audit log page
│   ├── theme/                  # MUI theme configuration
│   │   └── theme.ts            # Dark mode theme
│   ├── types/                  # TypeScript types
│   │   └── schemas.ts          # API schema types
│   ├── App.tsx                 # Main app component
│   └── main.tsx                # Entry point
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── vite.config.ts              # Vite config
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**

```bash
cd AssetManagement/frontend
npm install
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your API URL if different from default
```

3. **Start development server:**

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Features Overview

### 1. Dashboard

- Overview of platform features
- Quick access to key functions
- System architecture information

### 2. Portfolio Rebalance Request

- **Request Intake Form:**
  - Client and account information
  - Current holdings with auto-calculated values
  - Target allocation with percentage validation
  - Mandate constraints
  - Additional context

- **Workflow Status:**
  - Real-time progress tracking
  - Agent completion status
  - Workflow state indicators (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
  - Metadata display (request_id, trace_id, versions)

### 3. Approval Review

- Trade proposal review with rationale and evidence
- Compliance verdict and risk metrics
- Memory summary and client preferences
- Allocation comparison charts
- Approval/rejection controls with notes

### 4. Audit Log

- Query audit events by request_id, trace_id, timestamp
- Event type filtering
- Export functionality for compliance review
- 7-year retention support

## Theme and Styling

The application uses a custom dark mode theme optimized for financial applications:

### Color Palette

- **Primary:** Blue (#1976d2) - Main actions and highlights
- **Secondary:** Purple (#9c27b0) - Secondary actions
- **Success:** Green (#2e7d32) - Positive states (NORMAL, COMPLIANT, APPROVED)
- **Error:** Red (#d32f2f) - Negative states (BLOCKED, NON_COMPLIANT, REJECTED)
- **Warning:** Orange (#ed6c02) - Warning states (DEGRADED, PENDING)
- **Info:** Light Blue (#0288d1) - Informational states (LOW_CONFIDENCE)

### Workflow State Colors

- **NORMAL:** Green - All controls satisfied
- **DEGRADED:** Orange - Non-critical issues
- **LOW_CONFIDENCE:** Blue - Quality below threshold
- **BLOCKED:** Red - Critical controls unresolved

### Typography

- Font family: System fonts (-apple-system, Segoe UI, Roboto)
- Headings: 600 weight
- Body text: 400 weight
- Buttons: 500 weight, uppercase

## API Integration

### API Client Configuration

The API client (`src/api/client.ts`) includes:

- **Base URL:** Configurable via `VITE_API_BASE_URL` environment variable
- **Timeout:** 30 seconds
- **Request Interceptors:**
  - Auto-generate `X-Request-ID` for correlation
  - Add `X-Trace-ID` from session storage
- **Response Interceptors:**
  - Store `X-Trace-ID` for correlation
  - Handle structured errors from backend

### Available Endpoints

- `POST /supervisor/invoke` - Invoke supervisor agent
- `POST /approval/artifacts` - Create approval artifact
- `GET /approval/artifacts/:id` - Get approval artifact
- `PUT /approval/artifacts/:id/approve` - Approve artifact
- `PUT /approval/artifacts/:id/reject` - Reject artifact
- `GET /audit/events` - Query audit events
- `GET /audit/events/:id` - Get audit event
- `GET /audit/events/export` - Export audit events

## TypeScript Types

All TypeScript types are generated from the backend Pydantic schemas:

- `PortfolioRebalanceRequest` - Request payload
- `SupervisorResponse` - Supervisor agent response
- `ApprovalArtifact` - Approval artifact
- `AuditEvent` - Audit event
- `WorkflowState` - Workflow state enum
- `ApprovalStatus` - Approval status enum
- `ComplianceVerdict` - Compliance verdict enum

## State Management

The application uses **TanStack Query** (React Query) for server state management:

- Automatic caching and background refetching
- Optimistic updates
- Request deduplication
- Loading and error states
- Retry logic with exponential backoff

## Responsive Design

The application is fully responsive:

- **Desktop:** Full sidebar navigation, multi-column layouts
- **Tablet:** Collapsible sidebar, responsive grids
- **Mobile:** Drawer navigation, single-column layouts

## Best Practices

### Code Organization

- **Components:** Reusable UI components in `src/components/`
- **Pages:** Route-level components in `src/pages/`
- **API:** Centralized API logic in `src/api/`
- **Types:** Shared TypeScript types in `src/types/`
- **Theme:** Centralized theme configuration in `src/theme/`

### TypeScript

- Strict mode enabled
- No implicit any
- Unused locals and parameters flagged
- Path aliases configured (`@/*` → `src/*`)

### Performance

- Code splitting with React Router
- Lazy loading for heavy components
- Memoization for expensive computations
- Optimized re-renders with React.memo

### Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast compliance

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR for fast development. Changes to components will reflect immediately without full page reload.

### API Proxy

The Vite dev server proxies `/api` requests to `http://localhost:8000` to avoid CORS issues during development.

### Type Checking

Run type checking separately from the build:

```bash
npm run type-check
```

### Linting

Run ESLint to catch common issues:

```bash
npm run lint
```

## Deployment

### Build

```bash
npm run build
```

### Deploy to AWS

The frontend can be deployed to:

- **AWS Amplify** - Automatic CI/CD from Git
- **AWS S3 + CloudFront** - Static hosting with CDN
- **AWS ECS/Fargate** - Containerized deployment

### Environment Variables

Set the following environment variables for production:

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_ENV` - Environment name (production)

## Troubleshooting

### API Connection Issues

1. Verify backend is running on `http://localhost:8000`
2. Check `.env` file has correct `VITE_API_BASE_URL`
3. Check browser console for CORS errors
4. Verify API proxy configuration in `vite.config.ts`

### Build Errors

1. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Check TypeScript errors: `npm run type-check`

### Type Errors

1. Ensure types in `src/types/schemas.ts` match backend schemas
2. Run `npm run type-check` to see all type errors
3. Check for missing imports or incorrect type usage

## Contributing

1. Follow the existing code structure and naming conventions
2. Use TypeScript strict mode
3. Add proper type annotations
4. Write meaningful component and function names
5. Keep components small and focused
6. Use Material-UI components consistently
7. Follow the dark mode theme guidelines

## License

This project is part of the Bedrock Multi-Agent Portfolio Platform.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the design document: `../docs/design.md`
3. Check the backend API documentation
4. Review the tasks document: `../.kiro/specs/bedrock-multi-agent-portfolio-platform/tasks.md`
