# Use a multi-stage build for optimizing the final image size
# Stage 1: Build stage for C++ components
FROM ubuntu:20.04 AS builder

# Install dependencies for building C++ components
RUN apt-get update && \
    apt-get install -y build-essential cmake git libboost-all-dev

# Set the working directory
WORKDIR /app

# Copy the core components of the HFT system
COPY ./core_components/execution/ ./execution/
COPY ./core_components/utils/ ./utils/

# Build C++ components (execution algorithms)
RUN mkdir build && cd build && \
    cmake ../execution && \
    make

# Stage 2: Runtime environment
FROM python:3.9-slim

# Install necessary Python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Install Java for Java-based strategies and compliance checks
RUN apt-get update && \
    apt-get install -y openjdk-11-jre

# Copy Python scripts for market data, trading strategies, and risk management
COPY ./core_components/market_data_management/ /app/market_data_management/
COPY ./core_components/trading_strategy_development/ /app/strategies/
COPY ./core_components/risk_management/ /app/risk_management/

# Copy pre-built C++ components from the build stage
COPY --from=builder /app/execution/ /app/execution/
COPY --from=builder /app/utils/ /app/utils/

# Set environment variables for API keys, configs, etc.
ENV CONFIG_FILE=/app/configs/config.yaml

# Expose ports for communication
EXPOSE 8080 9000

# Set the entrypoint to start the HFT system
ENTRYPOINT ["python", "/app/strategies/backtest.py"]

# Define the command to run a specific strategy
CMD ["--strategy", "momentum"]