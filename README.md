# IPOR Fusion Alpha Bot Example

A Python-based bot for interacting with the IPOR Fusion Alpha platform.

## Description

This bot is an example Alpha built on the [IPOR Fusion SDK](https://github.com/IPOR-Labs/ipor-fusion.py).
On every cycle it reads the Plasma Vault's wstETH balance on Base and, when it is non-zero, supplies all of it
to Aave V3 through the `AaveV3SupplyFuse`.

## Prerequisites

- Docker or Podman (only for the compose sandbox)
- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) (Python dependency management)

## Environment Setup

1. **Configure Environment Variables**:

   Create a `.env` file in the root directory of the project by copying the provided example:

   ```bash
   cp .env.example .env
   ```

   Then, edit the `.env` file and replace the placeholder values with your actual credentials:
   - `PROVIDER_URL`: Your Base blockchain provider URL
   - `PRIVATE_KEY`: Your wallet private key
   - `PLASMA_VAULT_ADDRESS`: The address of the IPOR Plasma Vault

   For the compose sandbox (see [Docker Setup](#docker-setup)) leave `PRIVATE_KEY` at the `.env.example` value.
   It is anvil's account #0, the wallet `docker-entrypoint.sh` grants `ALPHA_ROLE` to; any other key makes the
   bot revert with `AccessManagedUnauthorized`. Use a real key only against a live RPC.

## Development Setup

1.  **Install Dependencies**:

    ```bash
    uv sync
    ```

2.  **Run Tests**:

    ```bash
    uv run pytest
    ```

    The test dry-runs the strategy with `eth_simulateV1` against a pinned Base block, so it needs
    `PROVIDER_URL` to point at an archive RPC that supports it (Alchemy does). No anvil or Docker required.

3.  **Lint and Format**:

    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

    CI runs both checks before the tests.

## Usage

### Running the Bot

Execute the bot with the following command:

```bash
uv run python main.py
```

The bot will:
1. Connect to the Base blockchain network using the provided credentials
2. Initialize the IPOR Plasma Vault system
3. Execute the trading strategy at the configured interval (default: 60 seconds)

## Docker Setup

The project includes Docker configuration for easy deployment:

1. **Docker Files**:
   - `Dockerfile` - Configures the Python environment for the alpha bot
   - `Dockerfile.anvil` - Sets up the Foundry environment with anvil for local blockchain testing
   - `docker-compose.yml` - Orchestrates both services with proper networking

2. **Running with Docker**:

   ```bash
   docker compose up -d
   ```

   This will start:
   - An anvil instance for local blockchain simulation
   - The alpha bot container connected to the anvil service

   The bot starts only after anvil reports healthy, which means the fork is up and the
   sandbox alpha wallet has been granted `ALPHA_ROLE`. If anvil never becomes healthy
   (`docker compose ps`), the role grant in `docker-entrypoint.sh` failed; check `docker compose logs anvil`.


### Customizing the Bot

To customize the bot's behavior:

1. Implement your strategy in `AlphaBot.build_actions()` in `alpha_bot.py`. It returns the list of `FuseAction`s
   to execute this cycle (empty when there is nothing to do); `do_fusion()` sends them and logs the result
2. Adjust the scheduling interval in `main.py`
3. Add additional environment variables as needed
4. Update `test_alpha_bot.py` so the new actions are dry-run with `eth_simulateV1` at the pinned block

## Architecture

- `main.py` - Entry point that sets up environment and initializes components
- `alpha_bot.py` - Core bot implementation with trading strategies
- `scheduler.py` - Handles periodic execution of the bot's operations
- `logging_config.py` - Per-component console loggers
- `test_alpha_bot.py`, `conftest.py` - `eth_simulateV1` dry-run of the strategy against a pinned Base block

## AI Coding Agents

Repository guidance for AI coding agents lives in [`AGENTS.md`](AGENTS.md). Codex and Cursor read it natively;
`CLAUDE.md` (Claude Code) and `.gemini/settings.json` (Gemini CLI) only point at it. Keep `AGENTS.md` as the single
source of truth for every tool.

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.