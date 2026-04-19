/**
 * TypeScript types generated from Pydantic schemas
 * These match the backend API contracts
 */

// Enums
export enum WorkflowState {
  NORMAL = 'NORMAL',
  DEGRADED = 'DEGRADED',
  LOW_CONFIDENCE = 'LOW_CONFIDENCE',
  BLOCKED = 'BLOCKED',
}

export enum ApprovalStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  REVISION_REQUESTED = 'REVISION_REQUESTED',
}

export enum ComplianceVerdict {
  COMPLIANT = 'COMPLIANT',
  NON_COMPLIANT = 'NON_COMPLIANT',
  UNRESOLVED = 'UNRESOLVED',
}

export enum TradeAction {
  BUY = 'BUY',
  SELL = 'SELL',
}

export enum EventType {
  REQUEST_RECEIVED = 'REQUEST_RECEIVED',
  AGENT_INVOKED = 'AGENT_INVOKED',
  AGENT_COMPLETED = 'AGENT_COMPLETED',
  STRUCTURED_ERROR = 'STRUCTURED_ERROR',
  COMPLIANCE_VERDICT = 'COMPLIANCE_VERDICT',
  GUARDRAIL_EVENT = 'GUARDRAIL_EVENT',
  MEMORY_READ = 'MEMORY_READ',
  MEMORY_WRITE = 'MEMORY_WRITE',
  MEMORY_CORRECTION = 'MEMORY_CORRECTION',
  APPROVAL_ACTION = 'APPROVAL_ACTION',
  RELEASE_PROMOTION = 'RELEASE_PROMOTION',
  ROLLBACK_EVENT = 'ROLLBACK_EVENT',
}

// Base metadata interface
export interface BaseMetadata {
  request_id: string;
  session_id: string;
  trace_id: string;
  timestamp: string;
  agent_version: string;
  schema_version: string;
}

// Portfolio Rebalance Request
export interface Holding {
  security_id: string;
  security_name: string;
  quantity: number;
  current_price: number;
  current_value: number;
}

export interface Allocation {
  security_id: string;
  percentage: number;
}

export interface MandateConstraint {
  constraint_type: string;
  constraint_value: string | number;
  description: string;
}

export interface PortfolioRebalanceRequest {
  client_id: string;
  account_id: string;
  current_holdings: Holding[];
  current_allocation: Allocation[];
  target_allocation: Allocation[];
  cash_position: number;
  investment_objective: string;
  risk_profile: string;
  mandate_constraints: MandateConstraint[];
  requested_action_context?: string;
  schema_version: string;
}

// Trade Proposal
export interface TradeProposal {
  trade_id: string;
  security_id: string;
  security_name: string;
  action: TradeAction;
  quantity: number;
  estimated_price: number;
  rationale: string;
  evidence: string[];
  confidence_score: number;
  estimated_cost: number;
  tax_impact?: number;
}

// Compliance Response
export interface DriftAnalysis {
  security_id: string;
  current_percentage: number;
  target_percentage: number;
  drift_percentage: number;
}

export interface RiskMetrics {
  concentration_risk: number;
  volatility_proxy: number;
  sector_exposure: Record<string, number>;
}

export interface ComplianceVerdictDetail {
  verdict: ComplianceVerdict;
  violations: string[];
  warnings: string[];
  evidence: string[];
}

export interface RiskComplianceResponse extends BaseMetadata {
  drift_analysis: DriftAnalysis[];
  risk_metrics: RiskMetrics;
  compliance_verdict: ComplianceVerdictDetail;
  confidence_score: number;
  policy_version: string;
}

// Research Response
export interface MarketData {
  security_id: string;
  current_price: number;
  volume: number;
  change_percent: number;
  data_timestamp: string;
}

export interface SentimentSummary {
  overall_sentiment: string;
  confidence: number;
  key_factors: string[];
}

export interface ResearchResponse extends BaseMetadata {
  market_data: MarketData[];
  sentiment_summary: SentimentSummary;
  confidence_score: number;
  evidence: string[];
  provenance_metadata: Record<string, string>;
  degraded_mode_reason?: string;
}

// Memory Response
export interface MemoryItem {
  memory_id: string;
  category: string;
  content: string;
  confidence_score: number;
  created_at: string;
  recency: string;
}

export interface MemoryConflict {
  conflict_type: string;
  description: string;
  affected_memory_ids: string[];
}

export interface MemoryPersonalizationResponse extends BaseMetadata {
  memory_items: MemoryItem[];
  conflicts: MemoryConflict[];
  confidence_score: number;
  memory_version: string;
}

// Execution Response
export interface ExecutionResponse extends BaseMetadata {
  trade_proposals: TradeProposal[];
  confidence_score: number;
  evidence: string[];
  provenance_metadata: Record<string, string>;
}

// Recommendation Package
export interface RecommendationPackage {
  research: ResearchResponse;
  memory: MemoryPersonalizationResponse;
  compliance: RiskComplianceResponse;
  execution: ExecutionResponse;
}

// Supervisor Response
export interface StructuredError {
  code: string;
  message: string;
  severity: string;
  retryable: boolean;
  source_agent?: string;
  request_id: string;
  trace_id: string;
  timestamp: string;
  related_context?: Record<string, unknown>;
}

export interface SupervisorResponse extends BaseMetadata {
  policy_version: string;
  workflow_state: WorkflowState;
  recommendation_package: RecommendationPackage;
  structured_error?: StructuredError;
}

// Approval Artifact
export interface ApprovalArtifact {
  approval_id: string;
  request_id: string;
  trace_id: string;
  timestamp: string;
  agent_version: string;
  schema_version: string;
  policy_version: string;
  trade_proposals: TradeProposal[];
  compliance_verdict: ComplianceVerdictDetail;
  rationale: string;
  evidence: string[];
  memory_summary: Record<string, unknown>;
  workflow_state: WorkflowState;
  approval_status: ApprovalStatus;
  approved_by?: string;
  approved_at?: string;
  rejected_by?: string;
  rejected_at?: string;
  rejection_note?: string;
  created_at: string;
  updated_at: string;
}

// Audit Event
export interface AuditEvent {
  event_id: string;
  event_type: EventType;
  request_id: string;
  session_id: string;
  trace_id: string;
  timestamp: string;
  actor_identity?: string;
  actor_role?: string;
  agent_identity?: string;
  agent_version?: string;
  action_details: Record<string, unknown>;
  outcome: string;
  policy_version: string;
  environment_alias: string;
}

// API Response wrappers
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
