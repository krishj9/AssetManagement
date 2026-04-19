"""
Execution Agent

This module implements the Execution Agent logic for trade proposal generation.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
import uuid

from AssetManagement.schemas.execution_response import ExecutionResponse, TradeProposal

logger = logging.getLogger(__name__)


class ExecutionAgentLogic:
    """Business logic for Execution Agent."""
    
    AGENT_INSTRUCTIONS = """
You are the Execution Agent.

Your role is to:
1. Generate trade proposals from upstream analysis
2. Validate compliance verdict (block if NON_COMPLIANT or UNRESOLVED)
3. Calculate estimated portfolio impact
4. Calculate estimated costs and tax impact
5. Generate approval-artifact-ready package

Trade Proposal Requirements:
- trade_id, security_id, action (buy/sell), quantity
- estimated_price, rationale, evidence
- confidence_score, estimated_cost, tax_impact

Output Format: ExecutionResponse JSON schema

Never generate proposals if compliance verdict is NON_COMPLIANT or UNRESOLVED.
All proposals must have supporting evidence and rationale.
"""
    
    def __init__(self):
        logger.info("Execution Agent Logic initialized")
    
    def generate_trade_proposals(
        self,
        drift_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        compliance_verdict: str
    ) -> List[TradeProposal]:
        """Generate trade proposals based on drift analysis."""
        if compliance_verdict in ['NON_COMPLIANT', 'UNRESOLVED']:
            logger.warning(f"Blocking trade proposals due to compliance verdict: {compliance_verdict}")
            return []
        
        proposals = []
        
        for security, drift_info in drift_analysis.items():
            drift = drift_info.get('drift', 0.0)
            
            if abs(drift) > 0.05:  # 5% threshold
                action = 'sell' if drift > 0 else 'buy'
                quantity = abs(drift) * 100  # Placeholder calculation
                
                security_data = market_data.get(security, {})
                estimated_price = security_data.get('current_price', 0.0)
                
                proposal = TradeProposal(
                    trade_id=f"trade-{uuid.uuid4()}",
                    security_id=security,
                    action=action,
                    quantity=int(quantity),
                    estimated_price=estimated_price,
                    rationale=f"Rebalance {security} to target allocation",
                    evidence=[f"Current drift: {drift:.2%}"],
                    confidence_score=0.85,
                    estimated_cost=quantity * estimated_price * 0.001,  # 0.1% transaction cost
                    tax_impact=0.0  # Placeholder
                )
                
                proposals.append(proposal)
        
        return proposals
    
    def create_execution_response(
        self,
        request_id: str,
        session_id: str,
        trace_id: str,
        drift_analysis: Dict[str, Any],
        market_data: Dict[str, Any],
        compliance_verdict: str
    ) -> ExecutionResponse:
        """Create complete execution response."""
        trade_proposals = self.generate_trade_proposals(
            drift_analysis, market_data, compliance_verdict
        )
        
        return ExecutionResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            trade_proposals=trade_proposals,
            confidence_score=0.85,
            evidence=[f"Generated {len(trade_proposals)} trade proposals"],
            provenance_metadata={
                'generation_time': datetime.now(timezone.utc).isoformat()
            }
        )
