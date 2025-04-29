import logging
import os

from dotenv import load_dotenv
from ipor_fusion.AnvilTestContainerStarter import AnvilTestContainerStarter
from ipor_fusion.CheatingPlasmaVaultSystemFactory import (
    CheatingPlasmaVaultSystemFactory,
)
from ipor_fusion.Roles import Roles
from web3 import Web3

from alpha_bot import AlphaBot
from logging_config import LoggingConfig

logger = LoggingConfig.get_logger("test_main_executor")

logging.getLogger("web3").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("schedule").setLevel(logging.INFO)

load_dotenv(verbose=True)  # load provider url from .env file

ANVIL_PRIVATE_KEY = "0xcd40c97ee4395e67dd780e5e98583abd315d7c4e4a8d3f95866c89c739e6fc40"
ATOMIST = Web3.to_checksum_address("0xF6a9bd8F6DC537675D499Ac1CA14f2c55d8b5569")
PLASMA_VAULT_ADDRESS = Web3.to_checksum_address(
    "0xFe8b23B493579e5c3a0A3BC5BBF20662B3072DE6"
)
PRIVATE_KEY = "0xcd40c97ee4395e67dd780e5e98583abd315d7c4e4a8d3f95866c89c739e6fc40"

os.environ["PRIVATE_KEY"] = ANVIL_PRIVATE_KEY
os.environ["PLASMA_VAULT_ADDRESS"] = str(PLASMA_VAULT_ADDRESS)


def test_alpha_bot():
    logger.info("Loading environment variables")
    if "PROVIDER_URL" not in os.environ:
        logger.error("PROVIDER_URL environment variable missing")
        raise Exception("Environment PROVIDER_URL variable does not exist.")

    # Initialize the Anvil tests container
    anvil = AnvilTestContainerStarter(
        fork_url=os.getenv("PROVIDER_URL"), fork_block_number=29007455
    )
    anvil.start()

    cheating_system = CheatingPlasmaVaultSystemFactory(
        provider_url=anvil.get_anvil_http_url(),
        private_key=PRIVATE_KEY,
    ).get(PLASMA_VAULT_ADDRESS)

    cheating_system.prank(ATOMIST)
    cheating_system.access_manager().grant_role(
        Roles.ALPHA_ROLE, cheating_system.alpha(), 0
    )

    logger.info("Loading environment variables")
    if "PROVIDER_URL" not in os.environ:
        logger.error("PROVIDER_URL environment variable missing")
        raise Exception("Environment PROVIDER_URL variable does not exist.")

    os.environ["PROVIDER_URL"] = anvil.get_anvil_http_url()

    # Get the transaction executor
    AlphaBot(
        provider_url=anvil.get_anvil_http_url(),
        private_key=PRIVATE_KEY,
        plasma_vault_address=PLASMA_VAULT_ADDRESS,
    ).do_fusion()


if __name__ == "__main__":
    test_alpha_bot()
