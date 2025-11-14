import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Setup logger dasar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Muat variabel dari .env
load_dotenv()

API_KEY = os.getenv("OPEN_API_KEY")

if not API_KEY:
    logger.error("Cannot find OpenAI ApiKey.")
    sys.exit(1)

try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    logger.error(f"Unable to initialize OpenAI client: {e}")
    sys.exit(1)