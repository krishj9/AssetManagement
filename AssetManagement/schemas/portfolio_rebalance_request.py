"""
Portfolio Rebalance Request Schema

This module defines the Pydantic model for portfolio rebalance requests.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class SecurityType(str, Enum):
    """Type of security"""
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    CASH = "cash"
    OTHER = "other"


class InvestmentObjective(str, Enum):
    """Client's investment objective"""
    GROWTH = "growth"
    INCOME = "income"
    BALANCED = "balanced"
    CAPITAL_PRESERVATION = "capital_preservation"
    AGGRESSIVE_GROWTH = "aggressive_growth"


class RiskProfile(str, Enum):
    """Client's risk tolerance profile"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class CreditRating(str, Enum):
    """Credit rating for fixed income securities"""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"


class ActionType(str, Enum):
    """Type of rebalance action requested"""
    PERIODIC_REBALANCE = "periodic_rebalance"
    DRIFT_CORRECTION = "drift_correction"
    MANDATE_CHANGE = "mandate_change"
    MARKET_EVENT_RESPONSE = "market_event_response"
    CLIENT_REQUEST = "client_request"


class Urgency(str, Enum):
    """Urgency level of the request"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ConstraintType(str, Enum):
    """Type of constraint"""
    ALLOCATION = "allocation"
    CONCENTRATION = "concentration"
    EXCLUSION = "exclusion"
    INCLUSION = "inclusion"
    OTHER = "other"


class Holding(BaseModel):
    """Individual portfolio holding"""
    security_id: str = Field(..., min_length=1, description="Unique identifier for the security (e.g., ticker symbol, ISIN)")
    security_name: str = Field(..., description="Human-readable name of the security")
    security_type: Optional[SecurityType] = Field(None, description="Type of security")
    quantity: float = Field(..., ge=0, description="Number of shares or units held")
    current_price: float = Field(..., ge=0, description="Current price per share or unit")
    market_value: float = Field(..., ge=0, description="Total market value of the holding (quantity * current_price)")

    @field_validator('market_value')
    @classmethod
    def validate_market_value(cls, v: float, info) -> float:
        """Validate that market_value matches quantity * current_price within tolerance"""
        if 'quantity' in info.data and 'current_price' in info.data:
            expected = info.data['quantity'] * info.data['current_price']
            tolerance = 0.01  # 1 cent tolerance
            if abs(v - expected) > tolerance:
                raise ValueError(f"market_value {v} does not match quantity * current_price {expected}")
        return v


class AssetClassAllocation(BaseModel):
    """Asset class allocation"""
    asset_class: str = Field(..., min_length=1, description="Asset class name (e.g., equities, fixed_income, cash, alternatives)")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of portfolio allocated to this asset class")


class Allocation(BaseModel):
    """Portfolio allocation by asset class"""
    asset_classes: List[AssetClassAllocation] = Field(..., min_length=1, description="List of asset class allocations")
    total_market_value: Optional[float] = Field(None, ge=0, description="Total market value of the portfolio")

    @field_validator('asset_classes')
    @classmethod
    def validate_allocation_sum(cls, v: List[AssetClassAllocation]) -> List[AssetClassAllocation]:
        """Validate that allocation percentages sum to 100 within tolerance"""
        total = sum(ac.percentage for ac in v)
        tolerance = 0.1  # 0.1% tolerance
        if abs(total - 100.0) > tolerance:
            raise ValueError(f"Asset class percentages must sum to 100, got {total}")
        return v


class ESGConstraints(BaseModel):
    """Environmental, Social, and Governance constraints"""
    min_esg_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum ESG score (0-100)")
    exclude_controversial_weapons: Optional[bool] = Field(None, description="Exclude controversial weapons")
    exclude_tobacco: Optional[bool] = Field(None, description="Exclude tobacco")
    exclude_fossil_fuels: Optional[bool] = Field(None, description="Exclude fossil fuels")


class CustomConstraint(BaseModel):
    """Custom constraint rule"""
    constraint_id: str = Field(..., description="Unique identifier for the constraint")
    constraint_description: str = Field(..., description="Human-readable description of the constraint")
    constraint_type: Optional[ConstraintType] = Field(None, description="Type of constraint")


class MandateConstraints(BaseModel):
    """Client mandate and policy constraints"""
    max_single_security_concentration: Optional[float] = Field(None, ge=0, le=100, description="Maximum percentage of portfolio in a single security")
    max_sector_concentration: Optional[float] = Field(None, ge=0, le=100, description="Maximum percentage of portfolio in a single sector")
    min_credit_rating: Optional[CreditRating] = Field(None, description="Minimum credit rating for fixed income securities")
    excluded_securities: Optional[List[str]] = Field(None, description="List of excluded security IDs")
    excluded_sectors: Optional[List[str]] = Field(None, description="List of excluded sectors")
    esg_constraints: Optional[ESGConstraints] = Field(None, description="Environmental, Social, and Governance constraints")
    custom_constraints: Optional[List[CustomConstraint]] = Field(None, description="List of custom constraint rules")

    @model_validator(mode='after')
    def validate_constraints_not_contradictory(self):
        """Validate that constraints are well-formed and non-contradictory"""
        # Example validation: if max_single_security_concentration is set, it should be reasonable
        if self.max_single_security_concentration is not None and self.max_single_security_concentration < 1.0:
            raise ValueError("max_single_security_concentration must be at least 1.0% if set")
        
        # Example validation: if max_sector_concentration is set, it should be reasonable
        if self.max_sector_concentration is not None and self.max_sector_concentration < 5.0:
            raise ValueError("max_sector_concentration must be at least 5.0% if set")
        
        return self


class RequestedActionContext(BaseModel):
    """Context for the requested rebalance action"""
    action_type: ActionType = Field(..., description="Type of rebalance action requested")
    action_reason: Optional[str] = Field(None, description="Human-readable reason for the rebalance request")
    urgency: Optional[Urgency] = Field(Urgency.NORMAL, description="Urgency level of the request")
    requested_by: Optional[str] = Field(None, description="Identity of the person or system requesting the rebalance")
    requested_at: Optional[datetime] = Field(None, description="Timestamp when the request was created")


class PortfolioRebalanceRequest(BaseModel):
    """
    A structured request to review and potentially rebalance a client portfolio.
    
    This is the primary input schema for the portfolio rebalancing workflow.
    """
    client_id: str = Field(..., min_length=1, max_length=100, description="Unique identifier for the client")
    account_id: str = Field(..., min_length=1, max_length=100, description="Unique identifier for the account")
    current_holdings: List[Holding] = Field(..., description="List of current portfolio holdings")
    current_allocation: Allocation = Field(..., description="Current portfolio allocation by asset class")
    target_allocation: Optional[Allocation] = Field(None, description="Target portfolio allocation by asset class (optional)")
    cash_position: float = Field(..., ge=0, description="Available cash position in the account")
    investment_objective: InvestmentObjective = Field(..., description="Client's investment objective")
    risk_profile: RiskProfile = Field(..., description="Client's risk tolerance profile")
    mandate_constraints: MandateConstraints = Field(..., description="Client mandate and policy constraints")
    requested_action_context: RequestedActionContext = Field(..., description="Context for the requested rebalance action")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Version of the schema")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "CLIENT-12345",
                "account_id": "ACCT-67890",
                "current_holdings": [
                    {
                        "security_id": "AAPL",
                        "security_name": "Apple Inc.",
                        "security_type": "stock",
                        "quantity": 100,
                        "current_price": 150.00,
                        "market_value": 15000.00
                    }
                ],
                "current_allocation": {
                    "asset_classes": [
                        {"asset_class": "equities", "percentage": 60.0},
                        {"asset_class": "fixed_income", "percentage": 30.0},
                        {"asset_class": "cash", "percentage": 10.0}
                    ],
                    "total_market_value": 100000.00
                },
                "cash_position": 10000.00,
                "investment_objective": "balanced",
                "risk_profile": "moderate",
                "mandate_constraints": {
                    "max_single_security_concentration": 10.0,
                    "max_sector_concentration": 25.0
                },
                "requested_action_context": {
                    "action_type": "periodic_rebalance",
                    "action_reason": "Quarterly rebalance",
                    "urgency": "normal",
                    "requested_by": "portfolio_manager_001"
                },
                "schema_version": "1.0.0"
            }
        }
