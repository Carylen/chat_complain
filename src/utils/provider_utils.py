# src/utils/provider_utils.py

from typing import Optional

def detect_provider(phone_number: Optional[str]) -> str:
    if not phone_number:
        return "Unknown"
    if phone_number.startswith(("0811", "0812", "0813")):
        return "Telkomsel"
    elif phone_number.startswith(("0857", "0858")):
        return "Indosat"
    elif phone_number.startswith(("0895", "0896", "0897")):
        return "Three"
    return "Unknown"

def adjust_nominal_equivalent(amount: int, old_provider: str, new_provider: str) -> int:
    # Example: adjust based on provider difference
    if old_provider != new_provider:
        return int(amount * 0.95)  # 5% adjustment
    return amount