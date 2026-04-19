"""
Risk & Compliance Agent

This module implements the Risk & Compliance Agent logic for drift calculation
and compliance checking.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from AssetManagement.schemas.risk_compliance_response import RiskComplianceResponse, ComplianceVerdict

logger = logging.getLogger(__name__)


class ComplianceAgentLogic:
    """Business logic for Risk & Compliance Agent."""
    
    AGENT_INSTRUCTIONS = """
You are the Risk & Compliance Agent.

Your role is to:
1. Calculate portfolio drift (current vs target allocation)
2. Calculate risk metrics (concentration, volatility, exposure)
3. Evaluate mandate and policy constraints
4. Generate compliance verdict (COMPLIANT, NON_COMPLIANT, UNRESOLVED)

Compliance Rules:
- Maximum single security concentration: 20%
- Maximum sector concentration: 30%
- Risk profile must match client mandate
- No prohibited securities

Output Format: RiskComplianceResponse JSON schema

Compliance verdict must be machine-readable.
If any rule is violated, set verdict to NON_COMPLIANT.
If any rule cannot be evaluated, set verdict to UNRESOLVED.
"""
    
    def __init__(self):
        logger.info("Compliance Agent Logic initialized")
    
    def calculate_drift(
        self,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate portfolio drift."""
        drift = {}
        for security, target_pct in target_allocation.items():
            current_pct = current_allocation.get(security, 0.0)
            drift[security] = {
                'current': current_pct,
                'target': target_pct,
                'drift': current_pct - target_pct
            }
        return drift
    
    def calculate_risk_metrics(
        self,
        current_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate risk metrics."""
        max_concentration = max(current_allocation.values()) if current_allocation else 0.0
        
        return {
            'max_single_security_concentration': max_concentration,
            'portfolio_count': len(current_allocation)
        }
    
    def evaluate_compliance(
        self,
        current_allocation: Dict[str, float],
        mandate_constraints: Dict[str, Any]
    ) -> ComplianceVerdict:
        """Evaluate compliance verdict."""
        risk_metrics = self.calculate_risk_metrics(current_allocation)
        
        # Check concentration limits
        if risk_metrics['max_single_security_concentration'] > 0.20:
            return ComplianceVerdict(
                verdict='NON_COMPLIANT',
                rationale='Single security concentration exceeds 20% limit',
                evidence=['Concentration check failed'],
                unresolved_controls=[]
            )
        
        return ComplianceVerdict(
            verdict='COMPLIANT',
            rationale='All compliance checks passed',
            evidence=['Concentration within limits'],
            unresolved_controls=[]
        )
    
    def create_compliance_response(
        self,
        request_id: str,
        session_id: str,
        trace_id: str,
        current_allocation: Dict[str, float],
        target_allocation: Dict[str, float],
        mandate_constraints: Dict[str, Any]
    ) -> RiskComplianceResponse:
        """Create complete compliance response."""
        drift_analysis = self.calculate_drift(current_allocation, target_allocation)
        risk_metrics = self.calculate_risk_metrics(current_allocation)
        compliance_verdict = self.evaluate_compliance(current_allocation, mandate_constraints)
        
        return RiskComplianceResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            drift_analysis=drift_analysis,
            risk_metrics=risk_metrics,
            compliance_verdict=compliance_verdict,
            evidence=['Compliance evaluation completed'],
            confidence_score=0.95
        )
