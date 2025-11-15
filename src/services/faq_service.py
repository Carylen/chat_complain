# src/services/faq_service.py

"""
FAQ Service for retrieving relevant FAQs based on complaint analysis.
Uses keyword matching and semantic similarity.
"""

from typing import List, Dict, Tuple
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.schemas import ComplaintAnalysis
from src.config import FAQDatabase, settings, AutomationRules
from src.utils.logger import get_logger


logger = get_logger(__name__, settings.log_level)


class FAQMatch:
    """Represents a matched FAQ with relevance score"""
    
    def __init__(self, question: str, answer: str, score: float, keywords: List[str]):
        self.question = question
        self.answer = answer
        self.score = score
        self.keywords = keywords
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "question": self.question,
            "answer": self.answer,
            "score": round(self.score, 2),
            "keywords": self.keywords
        }


class FAQService:
    """Service for retrieving and ranking relevant FAQs"""
    
    def __init__(self):
        """Initialize FAQ service"""
        self.faq_database = FAQDatabase()
        logger.info("FAQ service initialized")
    
    def get_relevant_faqs(
        self,
        analysis: ComplaintAnalysis,
        top_k: int = 3
    ) -> List[FAQMatch]:
        """
        Get most relevant FAQs for the complaint.
        
        Args:
            analysis: Complaint analysis object
            top_k: Number of top FAQs to return
            
        Returns:
            List of FAQMatch objects sorted by relevance
        """
        logger.info(f"Retrieving FAQs for category: {analysis.issue_category}")
        
        # Get FAQs for this issue category
        category_faqs = self.faq_database.get_faqs_by_category(analysis.issue_category)
        
        if not category_faqs:
            logger.warning(f"No FAQs found for category: {analysis.issue_category}")
            return []
        
        # Score each FAQ based on keyword matching
        scored_faqs = []
        for faq in category_faqs:
            score = self._calculate_relevance_score(analysis, faq)
            if score > 0:
                matched_faq = FAQMatch(
                    question=faq["question"],
                    answer=faq["answer"],
                    score=score,
                    keywords=faq["keywords"]
                )
                scored_faqs.append(matched_faq)
        
        # Sort by score and return top K
        scored_faqs.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Found {len(scored_faqs)} relevant FAQs")
        
        return scored_faqs[:top_k]
    
    def _calculate_relevance_score(
        self,
        analysis: ComplaintAnalysis,
        faq: Dict
    ) -> float:
        """
        Calculate relevance score between complaint and FAQ.
        
        Args:
            analysis: Complaint analysis
            faq: FAQ dictionary with keywords
            
        Returns:
            Relevance score (0-100)
        """
        score = 0.0
        
        # Base score for category match
        score += 30.0
        
        # Build search text from analysis
        search_text = f"{analysis.brief_summary} {analysis.issue_category}".lower()
        
        # Add entities to search text
        entities = analysis.entities.model_dump()
        for key, value in entities.items():
            if value:
                search_text += f" {value}".lower()
        
        # Check keyword matches
        faq_keywords = faq.get("keywords", [])
        matched_keywords = 0
        
        for keyword in faq_keywords:
            if keyword.lower() in search_text:
                matched_keywords += 1
        
        # Add score based on keyword matches
        if faq_keywords:
            keyword_score = (matched_keywords / len(faq_keywords)) * 70.0
            score += keyword_score
        
        return score
    
    def format_faq_response(self, faqs: List[FAQMatch]) -> str:
        """
        Format FAQs into user-friendly response.
        
        Args:
            faqs: List of matched FAQs
            
        Returns:
            Formatted FAQ string
        """
        if not faqs:
            return "No relevant FAQs found for your issue."
        
        response = "📚 Here are some resources that might help:\n\n"
        
        for i, faq in enumerate(faqs, 1):
            response += f"**Q{i}: {faq.question}**\n"
            response += f"{faq.answer}\n\n"
            response += "---\n\n"
        
        return response.strip()
    
    def check_if_faq_resolves_issue(
        self,
        analysis: ComplaintAnalysis,
        faqs: List[FAQMatch]
    ) -> bool:
        """
        Check if FAQs are likely to resolve the issue.
        
        Args:
            analysis: Complaint analysis
            faqs: List of matched FAQs
            
        Returns:
            True if FAQs might resolve, False if escalation needed
        """
        if not faqs:
            return False
        
        # Check if top FAQ has high relevance
        top_faq = faqs[0]
        
        # High confidence resolution
        if top_faq.score >= 80:
            logger.info(f"High confidence FAQ match (score: {top_faq.score})")
            return True
        
        # Medium confidence - check category
        config = AutomationRules.get_action_config(analysis.issue_category)
        
        if config.get("auto_resolve") and top_faq.score >= 60:
            logger.info(f"Medium confidence FAQ match with auto_resolve enabled")
            return True
        
        return False


def create_faq_service() -> FAQService:
    """
    Factory function to create FAQ service.
    
    Returns:
        FAQService instance
    """
    return FAQService()