import logging
import os

from dotenv import load_dotenv
from eth_account import Account
from ipor_fusion.testing import AnvilTestContainerStarter, ForkedWeb3Context
from ipor_fusion import Roles, PlasmaVault, AccessManager
from web3 import Web3

from alpha_bot import AlphaBot
from logging_config import LoggingConfig

logger = LoggingConfig.get_logger("test_main_executor")

logging.getLogger("web3").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("schedule").setLevel(logging.INFO)

load_dotenv(verbose=True)

PRIVATE_KEY = "0xcd40c97ee4395e67dd780e5e98583abd315d7c4e4a8d3f95866c89c739e6fc40"
ALPHA_WALLET = Web3.to_checksum_address(Account.from_key(PRIVATE_KEY).address)
ATOMIST = Web3.to_checksum_address("0xF6a9bd8F6DC537675D499Ac1CA14f2c55d8b5569")
PLASMA_VAULT_ADDRESS = Web3.to_checksum_address(
    "0xFe8b23B493579e5c3a0A3BC5BBF20662B3072DE6"
)

os.environ["PRIVATE_KEY"] = PRIVATE_KEY
os.environ["PLASMA_VAULT_ADDRESS"] = str(PLASMA_VAULT_ADDRESS)


def test_alpha_bot():
    logger.info("Loading environment variables")
    if "PROVIDER_URL" not in os.environ:
        logger.error("PROVIDER_URL environment variable missing")
        raise Exception("Environment PROVIDER_URL variable does not exist.")

    anvil = AnvilTestContainerStarter(
        fork_url=os.getenv("PROVIDER_URL"), fork_block_number=29007455
    )
    anvil.start()

    # Impersonate ATOMIST to grant ALPHA_ROLE
    cheating_ctx = ForkedWeb3Context.from_url(
        url=anvil.get_anvil_http_url(),
        impersonate=ATOMIST,
    )

    vault = PlasmaVault(cheating_ctx, PLASMA_VAULT_ADDRESS)
    access_manager_address = vault.get_access_manager_address()
    access_manager = AccessManager(cheating_ctx, access_manager_address)
    access_manager.grant_role(Roles.ALPHA_ROLE, ALPHA_WALLET, 0)

    os.environ["PROVIDER_URL"] = anvil.get_anvil_http_url()

    AlphaBot(
        provider_url=anvil.get_anvil_http_url(),
        private_key=PRIVATE_KEY,
        plasma_vault_address=PLASMA_VAULT_ADDRESS,
    ).do_fusion()


if __name__ == "__main__":
    test_alpha_bot()
