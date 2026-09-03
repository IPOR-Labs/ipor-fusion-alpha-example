import logging

from eth_account import Account
from ipor_fusion import AccessManager, PlasmaVault, Roles, Web3Context
from ipor_fusion.types import Period
from web3 import Web3

from alpha_bot import AlphaBot

logging.getLogger("web3").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)

PRIVATE_KEY = "0xcd40c97ee4395e67dd780e5e98583abd315d7c4e4a8d3f95866c89c739e6fc40"
ALPHA_WALLET = Web3.to_checksum_address(Account.from_key(PRIVATE_KEY).address)
ATOMIST = Web3.to_checksum_address("0xF6a9bd8F6DC537675D499Ac1CA14f2c55d8b5569")
PLASMA_VAULT_ADDRESS = Web3.to_checksum_address(
    "0xFe8b23B493579e5c3a0A3BC5BBF20662B3072DE6"
)


def grant_alpha_role(ctx: Web3Context) -> None:
    """Send grantRole from the impersonated ATOMIST (anvil --auto-impersonate)."""
    vault = PlasmaVault(ctx, PLASMA_VAULT_ADDRESS)
    access_manager = AccessManager(ctx, vault.get_access_manager_address().call())
    grant = access_manager.grant_role(Roles.ALPHA_ROLE, ALPHA_WALLET, Period(0))

    tx_hash = ctx.web3.eth.send_transaction(
        {"from": ATOMIST, "to": grant.to, "data": grant.calldata}
    )
    receipt = ctx.web3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt["status"] == 1, "grantRole reverted"


def test_alpha_bot(anvil_url):
    grant_alpha_role(Web3Context.from_url(anvil_url))

    receipt = AlphaBot(
        provider_url=anvil_url,
        private_key=PRIVATE_KEY,
        plasma_vault_address=PLASMA_VAULT_ADDRESS,
    ).do_fusion()

    assert receipt is not None, "do_fusion did not execute a transaction"
    assert receipt["status"] == 1
