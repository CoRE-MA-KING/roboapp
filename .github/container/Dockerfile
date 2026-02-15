# syntax=docker/dockerfile:1
FROM ubuntu:24.04

ARG GITHUB_REPOSITORY
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

# Run the project's init script using a bind mount to avoid extra layers.
# We use 'bash /tmp/init' to ensure it runs even if permissions are tricky on the mount.
RUN --mount=type=bind,source=.mise/tasks/init,target=/tmp/init \
    bash /tmp/init all && rm -rf /var/lib/apt/lists/*

# Install mise
RUN curl https://mise.jdx.dev/install.sh | sh
ENV PATH="/root/.local/share/mise/bin:/root/.local/share/mise/shims:$PATH"

WORKDIR /workspace
