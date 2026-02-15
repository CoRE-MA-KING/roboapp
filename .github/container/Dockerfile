# syntax=docker/dockerfile:1

FROM ubuntu:24.04 AS fetcher

RUN \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update  \
    && apt-get -y --no-install-recommends install  \
    # install any other dependencies you might need
    sudo curl git ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV MISE_DATA_DIR="/mise"
ENV MISE_CONFIG_DIR="/mise"
ENV MISE_CACHE_DIR="/mise/cache"
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
ENV PATH="/mise/shims:$PATH"
# ENV MISE_VERSION="..."

RUN curl https://mise.run | sh

FROM ubuntu:24.04

ARG GITHUB_REPOSITORY
LABEL org.opencontainers.image.source=https://github.com/${GITHUB_REPOSITORY}
LABEL org.opencontainers.image.description="CI image for roboapp with all system dependencies pre-installed"

ENV DEBIAN_FRONTEND=noninteractive
ENV ROBOAPP_CI_CONTAINER=true

# Optimize apt usage with cache mounts
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install minimal bootstrap tools using cache mounts
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    curl \
    git \
    gpg \
    sudo \
    pipx

# Run the project's init script using both bind mount (for the script) and cache mounts (for apt)
# The cache mount ensures that apt-get update/install inside the script are fast and don't bloat the image
RUN --mount=type=bind,source=.mise/tasks/init,target=/tmp/init \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    bash /tmp/init

WORKDIR /workspace

COPY --from=fetcher /usr/local/bin/mise /tmp/mise

RUN \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    /tmp/mise trust && \
    /tmp/mise install --verbose && \
    rm -f /tmp/mise
