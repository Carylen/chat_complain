from pydantic import BaseModel
from typing import Optional, List

token_prices = {
        "gpt-5.1": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5-mini": {"input": 0.25 / 1_000_000, "output": 2.00 / 1_000_000},
        "gpt-5-nano": {"input": 0.05 / 1_000_000, "output": 0.40 / 1_000_000},
        "gpt-5.1-chat-latest": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5-chat-latest": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5.1-codex": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5-codex": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-5-pro": {"input": 15.00 / 1_000_000, "output": 120.00 / 1_000_000},
        "gpt-4.1": {"input": 2.00 / 1_000_000, "output": 8.00 / 1_000_000},
        "gpt-4.1-mini": {"input": 0.40 / 1_000_000, "output": 1.60 / 1_000_000},
        "gpt-4.1-nano": {"input": 0.10 / 1_000_000, "output": 0.40 / 1_000_000},
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-2024-05-13": {"input": 5.00 / 1_000_000, "output": 15.00 / 1_000_000},
        "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "gpt-realtime": {"input": 4.00 / 1_000_000, "output": 16.00 / 1_000_000},
        "gpt-realtime-mini": {"input": 0.60 / 1_000_000, "output": 2.40 / 1_000_000},
        "gpt-4o-realtime-preview": {"input": 5.00 / 1_000_000, "output": 20.00 / 1_000_000},
        "gpt-4o-mini-realtime-preview": {"input": 0.60 / 1_000_000, "output": 2.40 / 1_000_000},
        "gpt-audio": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-audio-mini": {"input": 0.60 / 1_000_000, "output": 2.40 / 1_000_000},
        "gpt-4o-audio-preview": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-mini-audio-preview": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "o1": {"input": 15.00 / 1_000_000, "output": 60.00 / 1_000_000},
        "o1-pro": {"input": 150.00 / 1_000_000, "output": 600.00 / 1_000_000},
        "o3-pro": {"input": 20.00 / 1_000_000, "output": 80.00 / 1_000_000},
        "o3": {"input": 2.00 / 1_000_000, "output": 8.00 / 1_000_000},
        "o3-deep-research": {"input": 10.00 / 1_000_000, "output": 40.00 / 1_000_000},
        "o4-mini": {"input": 1.10 / 1_000_000, "output": 4.40 / 1_000_000},
        "o4-mini-deep-research": {"input": 2.00 / 1_000_000, "output": 8.00 / 1_000_000},
        "o3-mini": {"input": 1.10 / 1_000_000, "output": 4.40 / 1_000_000},
        "o1-mini": {"input": 1.10 / 1_000_000, "output": 4.40 / 1_000_000},
        "gpt-5.1-codex-mini": {"input": 0.25 / 1_000_000, "output": 2.00 / 1_000_000},
        "codex-mini-latest": {"input": 1.50 / 1_000_000, "output": 6.00 / 1_000_000},
        "gpt-5-search-api": {"input": 1.25 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-mini-search-preview": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "gpt-4o-search-preview": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "computer-use-preview": {"input": 3.00 / 1_000_000, "output": 12.00 / 1_000_000},
        "gpt-image-1": {"input": 5.00 / 1_000_000, "output": None},
        "gpt-image-1-mini": {"input": 2.00 / 1_000_000, "output": None},
    }

class Entities(BaseModel):
    """Entities extracted from the complaint"""
    amount: Optional[int] = None
    wrong_number: Optional[str] = None
    correct_number: Optional[str] = None
    transaction_id: Optional[str] = None

class ComplaintAnalysis(BaseModel):
    """Structure for complaint analysis output"""
    product_category: str
    issue_category: str
    entities: Entities
    brief_summary: str

class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    
    def cost_estimate(self, model: str) -> dict:
        """Calculate cost estimate based on model pricing"""
        input_token_price = token_prices.get(model, {}).get("input")
        output_token_price = token_prices.get(model, {}).get("output")
        if not input_token_price or not output_token_price:
            raise ValueError(f"Model '{model}' Not Found.")
        
        input_cost = self.input_tokens * input_token_price
        output_cost = self.output_tokens * output_token_price
        
        return {
            "input_token": self.input_tokens,
            "output_token": self.output_tokens,
            "total_token": self.total_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(input_cost + output_cost, 6)
        }