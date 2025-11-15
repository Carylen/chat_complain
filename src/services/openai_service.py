"""
OpenAI service for handling API interactions.
Provides structured output parsing and token tracking.
"""

from typing import Tuple, Optional
from openai import OpenAI
import time
import sys
import os

# Add parent directory to path for imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.schemas import ComplaintAnalysis, TokenUsage
from src.utils.context_manager import ConversationContext
from src.utils.logger import get_logger
from src.config import settings, Prompts


logger = get_logger(__name__, settings.log_level)


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model to use (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.token_usage = {
            "input_token": 0,
            "output_token": 0,
            "total_token": 0,
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0
        }
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
            raise
    
    def analyze_complaint(
        self,
        user_text: str,
        context: ConversationContext
    ) -> Optional[Tuple[ComplaintAnalysis, TokenUsage]]:
        """
        Analyze customer complaint using structured outputs.
        
        Args:
            user_text: Customer complaint text
            context: Conversation context manager
            
        Returns:
            Tuple of (ComplaintAnalysis, TokenUsage) or None if error
        """
        # Get system prompt with context
        system_prompt = Prompts.get_analysis_system_prompt(
            context.get_context_summary()
        )
        
        logger.info(f"Analyzing complaint: '{user_text[:50]}...'")
        start_time = time.time()
        
        try:
            # Call OpenAI API with structured outputs
            response = self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_text,
                text_format=ComplaintAnalysis,
            )
            
            # Extract analysis and usage
            analysis = response.output_parsed
            usage = TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log API call
            logger.log_api_call(
                endpoint="beta.chat.completions.parse",
                model=self.model,
                tokens_used=usage.total_tokens,
                duration=duration
            )
            
            # Update context
            context.add_complaint_summary(analysis.brief_summary)
            
            logger.debug(f"Analysis successful: {analysis.brief_summary}")
            
            return analysis, usage
        
        except Exception as e:
            logger.error(f"Failed to analyze complaint: {e}", exc_info=True)
            return None
    
    # def get_model_pricing(self, token_usage: TokenUsage) -> dict:
    #     """
    #     Get pricing information for current model.
        
    #     Returns:
    #         Dictionary with pricing information
    #     """
    #     new_costs = token_usage.cost_estimate(self.model)
    #     for key in self.token_usage:
    #         self.token_usage[key] += new_costs[key]
    #     return self.token_usage
    
    def estimate_cost(self, usage: TokenUsage) -> dict:
        """
        Estimate cost for token usage.
        
        Args:
            usage: TokenUsage object
            
        Returns:
            Dictionary with cost breakdown
        """
        new_costs = usage.cost_estimate(self.model)
        for key in self.token_usage:
            self.token_usage[key] += new_costs[key]
        return new_costs
    
    def change_model(self, model: str) -> None:
        """
        Change the model being used.
        
        Args:
            model: New model name
        """
        self.model = model
        logger.info(f"Model changed to: {model}")


def create_openai_service(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> OpenAIService:
    """
    Factory function to create OpenAI service.
    
    Args:
        api_key: Optional API key override
        model: Optional model override
        
    Returns:
        OpenAIService instance
    """
    return OpenAIService(api_key=api_key, model=model)