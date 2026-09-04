import os

import pytest
from dotenv import load_dotenv
from ipor_fusion import is_simulate_v1_supported
from web3 import Web3

load_dotenv()


@pytest.fixture(scope="session")
def provider_url() -> str:
    """Base RPC used for reads and for eth_simulateV1 dry-runs (no anvil needed)."""
    url = os.getenv("PROVIDER_URL")
    if not url:
        pytest.fail("PROVIDER_URL environment variable is required (Base archive RPC)")
    if not is_simulate_v1_supported(Web3(Web3.HTTPProvider(url))):
        pytest.fail("PROVIDER_URL does not support eth_simulateV1 (Alchemy does)")
    return url
