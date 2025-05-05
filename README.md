# IPOR Fusion Alpha Bot Example

A Python-based bot for interacting with the IPOR Fusion Alpha platform.

## Description

This bot provides an example implementation for automating interactions with the IPOR Fusion Alpha.
It demonstrates how to connect to the platform, retrieve data, and execute trades programmatically.

## Prerequisites

- Docker
- Python 3.11 or newer
- Poetry (Python dependency management)

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

## Development Setup

1.  **Install Dependencies**:

    ```bash
    poetry install
    ```

2.  **Run Tests**:

    ```bash
    poetry run pytest
    ```

## Usage

### Running the Bot

Execute the bot with the following command:

```bash
poetry run python main.py
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
   docker-compose up -d
   ```

   This will start:
   - An anvil instance for local blockchain simulation
   - The alpha bot container connected to the anvil service


### Customizing the Bot

To customize the bot's behavior:

1. Modify the `AlphaBot.do_fusion()` method in `alpha_bot.py` to implement your strategy
2. Adjust the scheduling interval in `main.py`
3. Add additional environment variables as needed

## Architecture

- `main.py` - Entry point that sets up environment and initializes components
- `alpha_bot.py` - Core bot implementation with trading strategies
- `scheduler.py` - Handles periodic execution of the bot's operations

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.