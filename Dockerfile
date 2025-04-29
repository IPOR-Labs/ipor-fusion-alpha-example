# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Install poetry and dependencies
RUN pip install poetry && poetry install --no-root

# Copy the application code
COPY . /app/

# Run the bot
CMD ["poetry", "run", "python", "main.py"]