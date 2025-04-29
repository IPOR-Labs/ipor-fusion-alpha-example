# IPOR Fusion Alpha Bot Example

A Python-based bot for interacting with the IPOR Fusion Alpha platform.

## Description

This bot provides an example implementation for automating interactions with the IPOR Fusion Alpha.
It demonstrates how to connect to the platform, retrieve data, and execute trades programmatically.

## Prerequisites

- Docker
- Python 3.11 or newer
- Poetry (Python dependency management)


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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
 Web3.py and related libraries