import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Setup logger dasar
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] - %(message)s",
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger(__name__)

# Muat variabel dari .env
# load_dotenv()

# API_KEY = os.getenv("OPEN_API_KEY")

# if not API_KEY:
#     logger.error("Cannot find OpenAI ApiKey.")
#     sys.exit(1)

# try:
#     client = OpenAI(api_key=API_KEY)
# except Exception as e:
#     logger.error(f"Unable to initialize OpenAI client: {e}")
#     sys.exit(1)

"""
Configuration management for the application.
Centralizes all configuration, constants, and environment variables.
"""

import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="OPENAI_API_KEY", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    
    # Context Configuration
    max_context_messages: int = Field(default=5, alias="MAX_CONTEXT_MESSAGES")
    max_complaint_history: int = Field(default=3, alias="MAX_COMPLAINT_HISTORY")
    
    # Application Configuration
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    google_chat_finance_webhook: Optional[str] = Field(default=None, alias="GOOGLE_CHAT_FINANCE_WEBHOOK")
    
    # WhatsApp Configuration
    whatsapp_enabled: bool = Field(default=True, alias="WHATSAPP_ENABLED")
    whatsapp_base_url: str = Field(default="https://wa.me/", alias="WHATSAPP_BASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


class Categories:
    """Valid categories for complaint classification"""
    
    PRODUCT_CATEGORIES: List[str] = [
        "Mobile Credit",
        "Data Package",
        "PLN Electricity",
        "E-Wallet",
        "Voucher Game",
        "Other"
    ]
    
    ISSUE_CATEGORIES: List[str] = [
        "Product Not Received",
        "Wrong Destination Number",
        "Transaction Failed",
        "Request Refund",
        "Payment Issue",
        "Account Problem",
        "Other"
    ]
    
    @classmethod
    def get_categories_prompt(cls) -> str:
        """Generate prompt text for categories"""
        return f"""
            Product Categories: {', '.join(cls.PRODUCT_CATEGORIES)}
            Issue Categories: {', '.join(cls.ISSUE_CATEGORIES)}
        """


class FAQDatabase:
    """FAQ database organized by issue category"""
    
    FAQS = {
        "Product Not Received": [
            {
                "question": "How long does it take for the product to arrive?",
                "answer": "Digital products are usually delivered within 1-5 minutes. If you haven't received it after 15 minutes, please check your transaction status.",
                "keywords": ["not received", "belum masuk", "waiting", "delay", "belum diterima"]
            },
            {
                "question": "What should I do if I haven't received my product?",
                "answer": "1. Check your email/SMS for confirmation\n2. Wait up to 15 minutes\n3. Check transaction status with your TRX ID\n4. If still not received, contact our support team",
                "keywords": ["not received", "missing", "lost", "hilang", "tidak masuk"]
            }
        ],
        "Wrong Destination Number": [
            {
                "question": "Can I change the destination number after payment?",
                "answer": "Unfortunately, transactions cannot be modified after payment is confirmed. However, we can help process a new transaction to the correct number. The incorrect transaction may be eligible for refund depending on the status.",
                "keywords": ["wrong number", "salah nomor", "change", "ganti nomor", "ubah nomor"]
            },
            {
                "question": "How to get a refund for wrong number transaction?",
                "answer": "To request a refund:\n1. Provide your transaction ID\n2. Confirm the wrong number\n3. Provide the correct number for retry\n4. We'll process refund if the product is unused",
                "keywords": ["refund", "wrong number", "salah kirim", "salah nomor"]
            }
        ],
        "Transaction Failed": [
            {
                "question": "Why did my transaction fail?",
                "answer": "Common reasons:\n1. Insufficient balance\n2. Network timeout\n3. System maintenance\n4. Invalid destination number\nYour money will be automatically refunded within 1x24 hours.",
                "keywords": ["failed", "gagal", "error", "timeout", "tidak berhasil"]
            },
            {
                "question": "When will I get my refund for failed transaction?",
                "answer": "Automatic refund for failed transactions is processed within 1x24 hours. You'll receive notification once completed.",
                "keywords": ["refund", "failed", "money back", "uang kembali", "kapan"]
            }
        ],
        "Request Refund": [
            {
                "question": "How long does refund take?",
                "answer": "Refund processing time:\n- Failed transaction: 1x24 hours (automatic)\n- Successful transaction: 3-7 business days (manual review)\n- E-wallet: 1-3 business days",
                "keywords": ["refund", "how long", "berapa lama", "kapan", "proses"]
            },
            {
                "question": "What documents do I need for refund?",
                "answer": "Required information:\n1. Transaction ID (TRX ID)\n2. Payment proof/screenshot\n3. Reason for refund\n4. Account information for refund",
                "keywords": ["refund", "document", "persyaratan", "syarat", "dokumen"]
            }
        ],
        "Payment Issue": [
            {
                "question": "My payment was deducted but transaction failed",
                "answer": "If your payment was deducted but transaction shows as failed:\n1. Check your transaction history\n2. Wait up to 15 minutes\n3. Contact us with TRX ID and payment proof\n4. Automatic refund will be processed if confirmed",
                "keywords": ["payment", "deducted", "terpotong", "failed", "gagal bayar"]
            }
        ],
        "Account Problem": [
            {
                "question": "I can't login to my account",
                "answer": "Troubleshooting steps:\n1. Check your internet connection\n2. Clear cache and cookies\n3. Reset your password\n4. Try different browser/device\n5. Contact support if issue persists",
                "keywords": ["login", "account", "password", "access", "masuk", "akun"]
            }
        ]
    }
    
    @classmethod
    def get_faqs_by_category(cls, category: str) -> List[Dict]:
        """Get FAQs for specific issue category"""
        return cls.FAQS.get(category, [])
    
    @classmethod
    def get_all_faqs(cls) -> Dict[str, List[Dict]]:
        """Get all FAQs"""
        return cls.FAQS


class WhatsAppConfig:
    """WhatsApp department routing configuration"""
    
    DEPARTMENTS = {
        "Product Not Received": {
            "department": "Transaction Support",
            "phone": "6281234567890",  # Replace with actual number
            "message_template": "Hi, I have an issue with product not received. TRX ID: {trx_id}",
            "priority": "high"
        },
        "Wrong Destination Number": {
            "department": "Transaction Support",
            "phone": "6281234567890",
            "message_template": "Hi, I sent product to wrong number. TRX ID: {trx_id}. Wrong: {wrong_number}, Correct: {correct_number}",
            "priority": "high"
        },
        "Transaction Failed": {
            "department": "Technical Support",
            "phone": "6281234567891",  # Different number for technical
            "message_template": "Hi, my transaction failed. TRX ID: {trx_id}",
            "priority": "medium"
        },
        "Request Refund": {
            "department": "Finance Department",
            "phone": "6281234567892",  # Finance department
            "message_template": "Hi, I want to request a refund. TRX ID: {trx_id}",
            "priority": "high"
        },
        "Payment Issue": {
            "department": "Payment Support",
            "phone": "6281234567893",
            "message_template": "Hi, I have a payment issue. TRX ID: {trx_id}",
            "priority": "high"
        },
        "Account Problem": {
            "department": "Account Support",
            "phone": "6281234567894",
            "message_template": "Hi, I have an account issue. Details: {details}",
            "priority": "medium"
        },
        "Other": {
            "department": "General Support",
            "phone": "6281234567895",
            "message_template": "Hi, I need assistance with: {details}",
            "priority": "low"
        }
    }
    
    @classmethod
    def get_department_info(cls, issue_category: str) -> Dict:
        """Get WhatsApp department info for issue category"""
        return cls.DEPARTMENTS.get(issue_category, cls.DEPARTMENTS["Other"])
    
    @classmethod
    def generate_whatsapp_url(cls, issue_category: str, **kwargs) -> str:
        """
        Generate WhatsApp URL with pre-filled message.
        
        Args:
            issue_category: Issue category
            **kwargs: Variables for message template (trx_id, wrong_number, etc.)
            
        Returns:
            WhatsApp URL
        """
        dept_info = cls.get_department_info(issue_category)
        phone = dept_info["phone"]
        message_template = dept_info["message_template"]
        
        # Fill template with provided kwargs
        try:
            message = message_template.format(**kwargs)
        except KeyError:
            # If missing keys, use raw template
            message = message_template
        
        # URL encode the message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        return f"https://wa.me/{phone}?text={encoded_message}"

class Prompts:
    """System prompts and templates"""
    
    @staticmethod
    def get_analysis_system_prompt(context_summary: str = "") -> str:
        """
        Get the system prompt for complaint analysis.
        
        Args:
            context_summary: Optional context from previous complaints
            
        Returns:
            Formatted system prompt
        """
        return f"""
            You are an AI Customer Service agent that analyzes customer complaints.

            {Categories.get_categories_prompt()}

            Extract important information and create a brief summary (max 10 words).
            {context_summary}
        """.strip()

class AutomationRules:
    """Business rules for automation logic"""
    
    ACTIONS = {
        "Wrong Destination Number": {
            "required_fields": ["correct_number", "amount"],
            "api_endpoint": "/api/transaction/retry",
            "escalate_if_missing": True,
            "show_faq": True,
            "auto_resolve": False
        },
        "Request Refund": {
            # "required_fields": ["transaction_id"],
            "required_fields": ["transaction_id", "refund_method", "refund_destination"],
            "api_endpoint": "/api/refund/process",
            "escalate_if_missing": True,
            "show_faq": True,
            "auto_resolve": False
        },
        "Product Not Received": {
            "required_fields": [],
            "api_endpoint": "/api/transaction/status",
            "escalate_if_missing": False,
            "show_faq": True,
            "auto_resolve": False
        },
        "Transaction Failed": {
            "required_fields": ["transaction_id"],
            "api_endpoint": "/api/transaction/investigate",
            "escalate_if_missing": False,
            "show_faq": True,
            "auto_resolve": True  # Can auto-resolve with FAQ
        },
        "Payment Issue": {
            "required_fields": ["transaction_id"],
            "api_endpoint": "/api/payment/investigate",
            "escalate_if_missing": True,
            "show_faq": True,
            "auto_resolve": False
        },
        "Account Problem": {
            "required_fields": [],
            "api_endpoint": "/api/account/support",
            "escalate_if_missing": False,
            "show_faq": True,
            "auto_resolve": True  # Can auto-resolve with FAQ
        }
    }
    
    @classmethod
    def get_action_config(cls, issue_category: str) -> Dict:
        """Get automation configuration for a specific issue category"""
        return cls.ACTIONS.get(issue_category, {
            "required_fields": [],
            "api_endpoint": "/api/escalate",
            "escalate_if_missing": True,
            "show_faq": True,
            "auto_resolve": False
        })


# Singleton settings instance
settings = Settings()