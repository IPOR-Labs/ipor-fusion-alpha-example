import logging

from eth_account import Account
from ipor_fusion import ERC20, AccessManager, PlasmaVault, Roles, VaultSimulator
from ipor_fusion.types import Period
from web3 import Web3

from alpha_bot import AlphaBot

logging.getLogger("web3").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)

# Any key works: eth_simulateV1 runs with validation=false, so nothing is signed.
PRIVATE_KEY = "0xcd40c97ee4395e67dd780e5e98583abd315d7c4e4a8d3f95866c89c739e6fc40"
ALPHA_WALLET = Web3.to_checksum_address(Account.from_key(PRIVATE_KEY).address)
ATOMIST = Web3.to_checksum_address("0xF6a9bd8F6DC537675D499Ac1CA14f2c55d8b5569")
PLASMA_VAULT_ADDRESS = Web3.to_checksum_address(
    "0xFe8b23B493579e5c3a0A3BC5BBF20662B3072DE6"
)
# Aave V3 aToken minted when supplying wstETH on Base
BASE_AAVE_V3_A_WSTETH = Web3.to_checksum_address(
    "0x99CBC45ea5bb7eF3a5BC08FB1B7E56bB2442Ef0D"
)
PINNED_BLOCK = 29007455


def test_alpha_bot(provider_url):
    bot = AlphaBot(
        provider_url=provider_url,
        private_key=PRIVATE_KEY,
        plasma_vault_address=PLASMA_VAULT_ADDRESS,
    )
    # Pin the strategy's reads to the same block the simulation runs on
    bot.ctx.default_block = PINNED_BLOCK

    vault = PlasmaVault(bot.ctx, PLASMA_VAULT_ADDRESS)
    access_manager = AccessManager(bot.ctx, vault.get_access_manager_address().call())
    wsteth = ERC20(bot.ctx, AlphaBot.WSTETH_ADDRESS)
    awsteth = ERC20(bot.ctx, BASE_AAVE_V3_A_WSTETH)

    actions = bot.build_actions()
    assert actions, "vault holds no wstETH at the pinned block, nothing to simulate"

    # Role grant, strategy execution and balance reads in one eth_simulateV1 roundtrip
    sim = VaultSimulator(
        web3=bot.ctx.web3,
        vault=PLASMA_VAULT_ADDRESS,
        alpha=ALPHA_WALLET,
        block=PINNED_BLOCK,
    )
    sim.add_call(
        call=access_manager.grant_role(Roles.ALPHA_ROLE, ALPHA_WALLET, Period(0)),
        from_=ATOMIST,
    )
    sim.observe("wsteth_before", wsteth.balance_of(PLASMA_VAULT_ADDRESS))
    sim.observe("awsteth_before", awsteth.balance_of(PLASMA_VAULT_ADDRESS))
    sim.execute(actions)
    sim.observe("wsteth_after", wsteth.balance_of(PLASMA_VAULT_ADDRESS))
    sim.observe("awsteth_after", awsteth.balance_of(PLASMA_VAULT_ADDRESS))

    result = sim.run()

    failed = [(call.label, call.error) for call in result.failed_calls]
    assert result.all_success, f"calls failed: {failed} (reason={result.revert_reason})"

    supplied = result.get("wsteth_before")
    assert supplied > 0
    assert result.get("wsteth_after") == 0
    minted = result.get("awsteth_after") - result.get("awsteth_before")
    # aTokens rebase, so allow a few wei of rounding
    assert abs(minted - supplied) <= 10
