import logging
import os

from dotenv import load_dotenv

from alpha_bot import AlphaBot
from logging_config import LoggingConfig
from scheduler import Scheduler

load_dotenv(verbose=True)  # load provider url from .env file

logging.getLogger("web3").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("schedule").setLevel(logging.INFO)

logger = LoggingConfig.get_logger("main")

if __name__ == "__main__":

    provider_url = os.getenv("PROVIDER_URL")
    private_key = os.getenv("PRIVATE_KEY")
    plasma_vault_address = os.getenv("PLASMA_VAULT_ADDRESS")

    # Check if any of the required environment variables are missing
    missing_vars = []
    if provider_url is None:
        missing_vars.append("PROVIDER_URL")
    if private_key is None:
        missing_vars.append("PRIVATE_KEY")
    if plasma_vault_address is None:
        missing_vars.append("PLASMA_VAULT_ADDRESS")

    if missing_vars:
        logger.error(
            f"Error: The following required environment variables are missing: {', '.join(missing_vars)}"
        )
        logger.error(
            "Please set these variables in your .env file or environment before running the application."
        )
        exit(1)

    fusion_alpha_bot = AlphaBot(
        provider_url=provider_url,
        private_key=private_key,
        plasma_vault_address=plasma_vault_address,
    )

    scheduler = Scheduler(
        fusion_alpha_bot=fusion_alpha_bot, interval=60
    )  # run every 60 seconds

    scheduler.schedule()
