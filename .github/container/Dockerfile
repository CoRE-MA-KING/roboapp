FROM ubuntu:24.04

LABEL org.opencontainers.image.source=https://github.com/${GITHUB_REPOSITORY}
LABEL org.opencontainers.image.description="CI image for roboapp with all system dependencies pre-installed using the project init script"

ENV DEBIAN_FRONTEND=noninteractive
ENV ROBOAPP_CI_CONTAINER=true

# Install minimal bootstrap tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gpg \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Copy and run the project's init script to ensure consistency
# We run it with 'all' to install every component's dependencies
COPY .mise/tasks/init /tmp/init
RUN chmod +x /tmp/init && /tmp/init all && rm /tmp/init && rm -rf /var/lib/apt/lists/*

# Install mise
RUN curl https://mise.jdx.dev/install.sh | sh
ENV PATH="/root/.local/share/mise/bin:/root/.local/share/mise/shims:$PATH"

WORKDIR /workspace
