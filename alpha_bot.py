from ipor_fusion.PlasmaVaultSystemFactory import PlasmaVaultSystemFactory
from web3 import Web3

from logging_config import LoggingConfig


class AlphaBot:
    WSTETH_ADDRESS = "0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452"

    def __init__(self, provider_url: str, private_key: str, plasma_vault_address: str):
        """
        Initialize the Fusion Alpha Bot with necessary credentials and settings.

        Args:
            provider_url: The blockchain provider URL
            private_key: The private key for transaction signing
            plasma_vault_address: The address of the plasma vault to interact with
        """
        self.provider_url = provider_url
        self.private_key = private_key
        self.plasma_vault_address = Web3.to_checksum_address(plasma_vault_address)

        self.logger = LoggingConfig.get_logger("AlphaBot")

        self.plasma_system = PlasmaVaultSystemFactory(
            provider_url=self.provider_url,
            private_key=self.private_key,
        ).get(self.plasma_vault_address)

    def do_fusion(self):
        """
        Execute the Fusion strategy - supply wstETH to Aave v3 protocol in E-Mode.

        This method performs the following operations:
        1. Access the plasma vault instance
        2. Get a reference to the wstETH token
        3. Create a supply transaction to deposit all wstETH into Aave v3 with E-Mode enabled
        4. Execute the transaction through the vault

        Returns:
            dict or None: Transaction receipt if successful, None if the balance is zero

        Raises:
            Exception: Any errors during the process are logged and re-raised
        """
        self.logger.info("Starting fusion operation")

        try:
            # Get the plasma vault instance
            self.logger.debug("Accessing plasma vault instance")
            vault = self.plasma_system.plasma_vault()

            # Get the wstETH token instance using its address
            self.logger.debug(f"Getting wstETH token at address: {self.WSTETH_ADDRESS}")
            wsteth = self.plasma_system.erc20(asset_address=self.WSTETH_ADDRESS)

            # Get balance to supply
            balance = wsteth.balance_of(self.plasma_vault_address)
            self.logger.info(f"Current wstETH balance to supply: {balance}")

            if balance == 0:
                self.logger.warning(
                    "wstETH balance is zero, cannot proceed with fusion"
                )
                return None

            # Create a supply transaction to deposit all available wstETH into Aave v3
            self.logger.debug(
                f"Creating supply transaction asset_address={wsteth.address()} amount={balance} e_mode={1}"
            )
            supply = self.plasma_system.aave_v3().supply(
                asset_address=wsteth.address(), amount=balance, e_mode=1
            )

            # Execute the supply transaction through the vault
            self.logger.info("Executing transaction...")
            tx_receipt = vault.execute([supply])
            tx_hash = tx_receipt.transactionHash.hex()
            self.logger.info(f"Transaction executed successfully hash: 0x{tx_hash}")

            # Log more transaction details if debug is enabled
            self.logger.debug(
                f"Transaction details: gas used={tx_receipt.gasUsed}, "
                f"block number={tx_receipt.blockNumber}"
            )

            return tx_receipt

        except Exception as e:
            self.logger.error(f"Fusion operation failed: {str(e)}")
            self.logger.exception("Full exception traceback:")
