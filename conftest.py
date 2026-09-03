import os
import time

import pytest
import requests
from dotenv import load_dotenv
from testcontainers.core.config import testcontainers_config
from testcontainers.core.container import DockerContainer
from web3 import Web3

load_dotenv()

ANVIL_IMAGE = (
    "ghcr.io/ipor-labs/foundry:nightly-aa69ed1e46dd61fbf9d73399396a4db4dd527431"
)
ANVIL_PORT = 8545
FORK_BLOCK_NUMBER = 29007455
PODMAN_SOCKETS = (
    f"{os.getenv('XDG_RUNTIME_DIR', '')}/podman/podman.sock",
    "/run/podman/podman.sock",
)


def _use_podman_if_no_docker() -> None:
    """testcontainers only looks for Docker; point it at podman when that is what runs here."""
    if os.getenv("DOCKER_HOST") or os.path.exists("/var/run/docker.sock"):
        return
    for sock in PODMAN_SOCKETS:
        if os.access(sock, os.R_OK | os.W_OK):
            os.environ["DOCKER_HOST"] = f"unix://{sock}"
            # Ryuk mounts the Docker socket into a sidecar; podman has no equivalent
            testcontainers_config.ryuk_disabled = True
            return


def _wait_until_ready(url: str, timeout_s: int = 120) -> None:
    web3 = Web3(Web3.HTTPProvider(url))
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if web3.eth.block_number > 0:
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise TimeoutError(f"anvil at {url} did not become ready in {timeout_s}s")


@pytest.fixture(scope="session")
def anvil_url() -> str:
    """Base fork on anvil (Docker or Podman) with --auto-impersonate, so any address can send txs."""
    fork_url = os.getenv("PROVIDER_URL")
    if not fork_url:
        pytest.fail("PROVIDER_URL environment variable is required to fork Base")
    _use_podman_if_no_docker()

    # The foundry image entrypoint is `sh -c`, so the whole command has to reach
    # it as one argument; the outer quotes keep docker from splitting it.
    command = (
        f'"anvil --auto-impersonate --host 0.0.0.0 '
        f'--fork-url {fork_url} --fork-block-number {FORK_BLOCK_NUMBER}"'
    )
    container = (
        DockerContainer(ANVIL_IMAGE).with_exposed_ports(ANVIL_PORT).with_command(command)
    )

    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(ANVIL_PORT)
        url = f"http://{host}:{port}"
        _wait_until_ready(url)
        yield url
