# syntax=docker/dockerfile:1
# check=error=true

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

RUN --mount=type=bind,source=.mise/tasks/init,target=/tmp/init \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    bash /tmp/init

SHELL ["/bin/bash", "-c"]

WORKDIR /workspace

RUN \
    --mount=type=bind,from=jdxcode/mise:2026.2.13,source=/usr/local/bin/mise,target=/tmp/mise \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    eval "$(/tmp/mise activate bash)" && \
    /tmp/mise trust && \
    /tmp/mise install

