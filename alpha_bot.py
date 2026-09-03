from ipor_fusion import Web3Context, PlasmaVault, ERC20, AaveV3SupplyFuse, FuseAction
from web3 import Web3

from logging_config import LoggingConfig


class AlphaBot:
    WSTETH_ADDRESS = Web3.to_checksum_address(
        "0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452"
    )
    BASE_AAVE_V3_SUPPLY_FUSE = Web3.to_checksum_address(
        "0x44dcb8a4c40fa9941d99f409b2948fe91b6c15d5"
    )

    def __init__(self, provider_url: str, private_key: str, plasma_vault_address: str):
        self.plasma_vault_address = Web3.to_checksum_address(plasma_vault_address)
        self.logger = LoggingConfig.get_logger("AlphaBot")

        self.ctx = Web3Context.from_url(
            url=provider_url,
            private_key=private_key,
        )
        self.vault = PlasmaVault(self.ctx, self.plasma_vault_address)
        self.wsteth = ERC20(self.ctx, self.WSTETH_ADDRESS)
        self.aave_v3_supply = AaveV3SupplyFuse(self.BASE_AAVE_V3_SUPPLY_FUSE)

    def build_actions(self) -> list[FuseAction]:
        """Strategy step: the fuse actions to execute now, empty when there is nothing to do."""
        balance = self.wsteth.balance_of(self.plasma_vault_address).call()
        self.logger.info(f"Current wstETH balance to supply: {balance}")

        if balance == 0:
            self.logger.warning("wstETH balance is zero, nothing to supply")
            return []

        self.logger.debug(
            f"Creating supply action asset={self.WSTETH_ADDRESS} amount={balance} e_mode=1"
        )
        supply = self.aave_v3_supply.supply(
            asset=self.WSTETH_ADDRESS, amount=balance, e_mode=1
        )
        return [supply]

    def do_fusion(self):
        self.logger.info("Starting fusion operation")

        try:
            actions = self.build_actions()
            if not actions:
                return None

            self.logger.info("Executing transaction...")
            tx_receipt = self.vault.execute(actions).send()
            tx_hash = tx_receipt.transactionHash.hex()
            self.logger.info(f"Transaction executed successfully hash: 0x{tx_hash}")

            self.logger.debug(
                f"Transaction details: gas used={tx_receipt.gasUsed}, "
                f"block number={tx_receipt.blockNumber}"
            )

            return tx_receipt

        except Exception as e:
            self.logger.error(f"Fusion operation failed: {str(e)}")
            self.logger.exception("Full exception traceback:")
