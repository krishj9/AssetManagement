"""
Research Agent

This module implements the Research Agent logic for market data retrieval
and sentiment analysis.
"""

import logging
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from AssetManagement.schemas.research_response import ResearchResponse

logger = logging.getLogger(__name__)


class ResearchAgentLogic:
    """
    Business logic for Research Agent.
    
    Retrieves market data using yfinance and generates sentiment summaries
    using Bedrock models.
    """
    
    # Agent Instructions for Bedrock Agent Configuration
    AGENT_INSTRUCTIONS = """
You are the Research Agent for portfolio management.

Your role is to:
1. Retrieve latest market prices for securities
2. Provide market context and news summary
3. Generate sentiment summary
4. Track data freshness and confidence

Data Sources:
- Use yfinance for market data
- Mark data freshness with timestamps
- Distinguish retrieved facts from model-derived commentary

Output Format: ResearchResponse JSON schema

If data is stale or missing, set degraded_mode_reason.
Never fabricate market facts. Only use retrieved data.
"""
    
    def __init__(self):
        """Initialize Research Agent Logic."""
        logger.info("Research Agent Logic initialized")
    
    def retrieve_market_data(
        self,
        securities: List[str]
    ) -> Dict[str, Any]:
        """
        Retrieve market data using yfinance.
        
        Args:
            securities: List of security symbols (e.g., ['AAPL', 'MSFT'])
        
        Returns:
            Dict containing market data for each security
        """
        try:
            market_data = {}
            
            for security in securities:
                try:
                    ticker = yf.Ticker(security)
                    info = ticker.info
                    history = ticker.history(period="1mo")
                    
                    market_data[security] = {
                        'symbol': security,
                        'current_price': info.get('currentPrice'),
                        'previous_close': info.get('previousClose'),
                        'volume': info.get('volume'),
                        'market_cap': info.get('marketCap'),
                        '52_week_high': info.get('fiftyTwoWeekHigh'),
                        '52_week_low': info.get('fiftyTwoWeekLow'),
                        'pe_ratio': info.get('trailingPE'),
                        'dividend_yield': info.get('dividendYield'),
                        'beta': info.get('beta'),
                        'sector': info.get('sector'),
                        'industry': info.get('industry'),
                        'data_freshness': datetime.now(timezone.utc).isoformat(),
                        'data_source': 'yfinance'
                    }
                    
                    logger.info(
                        f"Retrieved market data for {security}",
                        extra={
                            'security': security,
                            'current_price': market_data[security]['current_price']
                        }
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Failed to retrieve market data for {security}: {str(e)}",
                        extra={
                            'security': security,
                            'error': str(e)
                        }
                    )
                    market_data[security] = {
                        'symbol': security,
                        'error': str(e),
                        'data_freshness': datetime.now(timezone.utc).isoformat()
                    }
            
            return market_data
            
        except Exception as e:
            logger.error(
                f"Failed to retrieve market data: {str(e)}",
                extra={'error': str(e)}
            )
            raise
    
    def generate_sentiment_summary(
        self,
        securities: List[str],
        market_data: Dict[str, Any]
    ) -> str:
        """
        Generate market sentiment summary.
        
        In production, this would use Bedrock Converse API with Claude
        for sentiment analysis. For now, returns a placeholder.
        
        Args:
            securities: List of security symbols
            market_data: Market data retrieved from yfinance
        
        Returns:
            Sentiment summary string
        """
        try:
            # Placeholder implementation
            # In production, use Bedrock Converse API
            
            sentiment_parts = []
            
            for security in securities:
                data = market_data.get(security, {})
                current_price = data.get('current_price')
                previous_close = data.get('previous_close')
                
                if current_price and previous_close:
                    change_pct = ((current_price - previous_close) / previous_close) * 100
                    
                    if change_pct > 0:
                        sentiment = "positive"
                    elif change_pct < 0:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                    
                    sentiment_parts.append(
                        f"{security}: {sentiment} ({change_pct:+.2f}%)"
                    )
            
            sentiment_summary = "Market sentiment: " + ", ".join(sentiment_parts)
            
            logger.info(
                "Generated sentiment summary",
                extra={'sentiment_summary': sentiment_summary}
            )
            
            return sentiment_summary
            
        except Exception as e:
            logger.error(
                f"Failed to generate sentiment summary: {str(e)}",
                extra={'error': str(e)}
            )
            return "Sentiment analysis unavailable"
    
    def calculate_confidence_score(
        self,
        market_data: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score based on data completeness and freshness.
        
        Args:
            market_data: Market data retrieved from yfinance
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            total_securities = len(market_data)
            successful_retrievals = sum(
                1 for data in market_data.values()
                if 'error' not in data and data.get('current_price') is not None
            )
            
            if total_securities == 0:
                return 0.0
            
            confidence = successful_retrievals / total_securities
            
            logger.info(
                f"Calculated confidence score: {confidence}",
                extra={
                    'total_securities': total_securities,
                    'successful_retrievals': successful_retrievals,
                    'confidence': confidence
                }
            )
            
            return confidence
            
        except Exception as e:
            logger.error(
                f"Failed to calculate confidence score: {str(e)}",
                extra={'error': str(e)}
            )
            return 0.0
    
    def create_research_response(
        self,
        request_id: str,
        session_id: str,
        trace_id: str,
        securities: List[str]
    ) -> ResearchResponse:
        """
        Create complete research response.
        
        Args:
            request_id: Request correlation ID
            session_id: Session correlation ID
            trace_id: Trace correlation ID
            securities: List of security symbols
        
        Returns:
            ResearchResponse with market data and sentiment
        """
        try:
            # Retrieve market data
            market_data = self.retrieve_market_data(securities)
            
            # Generate sentiment summary
            sentiment_summary = self.generate_sentiment_summary(securities, market_data)
            
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(market_data)
            
            # Create evidence list
            evidence = [
                f"Market data retrieved from yfinance for {len(securities)} securities",
                f"Data freshness: {datetime.now(timezone.utc).isoformat()}"
            ]
            
            # Check for degraded mode
            degraded_mode_reason = None
            if confidence_score < 0.8:
                degraded_mode_reason = f"Low data quality: {confidence_score:.2f} confidence"
            
            response = ResearchResponse(
                request_id=request_id,
                session_id=session_id,
                trace_id=trace_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version='1.0.0',
                schema_version='1.0.0',
                market_data=market_data,
                sentiment_summary=sentiment_summary,
                confidence_score=confidence_score,
                evidence=evidence,
                provenance_metadata={
                    'data_source': 'yfinance',
                    'retrieval_time': datetime.now(timezone.utc).isoformat()
                },
                degraded_mode_reason=degraded_mode_reason
            )
            
            logger.info(
                "Created research response",
                extra={
                    'request_id': request_id,
                    'confidence_score': confidence_score,
                    'degraded_mode': degraded_mode_reason is not None
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Failed to create research response: {str(e)}",
                extra={
                    'request_id': request_id,
                    'error': str(e)
                }
            )
            raise
