FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -ms /bin/bash vscode

# Set working directory
WORKDIR /workspace

# Install Python packages for development
RUN pip install --user \
    black \
    flake8 \
    isort \
    pytest \
    pytest-cov

# Add user's local bin to PATH
ENV PATH="/home/vscode/.local/bin:$PATH"

# Change ownership of workspace
RUN chown -R vscode:vscode /workspace

# Switch to non-root user
USER vscode

# Default command
CMD ["sleep", "infinity"] 