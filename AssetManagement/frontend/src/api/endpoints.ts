/**
 * API Endpoints for Portfolio Platform
 */

import apiClient from './client';
import {
  PortfolioRebalanceRequest,
  SupervisorResponse,
  ApprovalArtifact,
  AuditEvent,
} from '@/types/schemas';

// Health Check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Supervisor Agent Invocation
export const invokeSupervisor = async (
  request: PortfolioRebalanceRequest
): Promise<SupervisorResponse> => {
  const response = await apiClient.post('/supervisor/invoke', request);
  return response.data;
};

// Approval Artifacts
export const createApprovalArtifact = async (
  artifactData: Partial<ApprovalArtifact>
): Promise<ApprovalArtifact> => {
  const response = await apiClient.post('/approval/artifacts', artifactData);
  return response.data;
};

export const getApprovalArtifact = async (
  approvalId: string
): Promise<ApprovalArtifact> => {
  const response = await apiClient.get(`/approval/artifacts/${approvalId}`);
  return response.data;
};

export const approveArtifact = async (
  approvalId: string,
  approvalData: {
    approved_by: string;
    session_id?: string;
  }
): Promise<ApprovalArtifact> => {
  const response = await apiClient.put(
    `/approval/artifacts/${approvalId}/approve`,
    approvalData
  );
  return response.data;
};

export const rejectArtifact = async (
  approvalId: string,
  rejectionData: {
    rejected_by: string;
    rejection_note: string;
    session_id?: string;
  }
): Promise<ApprovalArtifact> => {
  const response = await apiClient.put(
    `/approval/artifacts/${approvalId}/reject`,
    rejectionData
  );
  return response.data;
};

// Audit Events
export interface AuditEventsQuery {
  request_id?: string;
  trace_id?: string;
  start_time?: string;
  end_time?: string;
  event_type?: string;
  limit?: number;
}

export const queryAuditEvents = async (
  query: AuditEventsQuery
): Promise<{ events: AuditEvent[]; count: number; limit: number }> => {
  const response = await apiClient.get('/audit/events', { params: query });
  return response.data;
};

export const getAuditEvent = async (eventId: string): Promise<AuditEvent> => {
  const response = await apiClient.get(`/audit/events/${eventId}`);
  return response.data;
};

export const exportAuditEvents = async (
  query: AuditEventsQuery & { format?: 'json' | 'csv' }
): Promise<{ events: AuditEvent[]; count: number; exported_at: string }> => {
  const response = await apiClient.get('/audit/events/export', {
    params: query,
  });
  return response.data;
};
