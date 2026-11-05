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
    sudo

SHELL ["/bin/bash", "-c"]

# Provide a no-op systemctl so Debian postinst scripts (e.g. zenohd) succeed
# in the container, where systemd is not running as PID 1. The diversion keeps
# the stub in place even if the systemd package is installed as a dependency.
RUN dpkg-divert --local --no-rename --add /usr/bin/systemctl && \
    printf '#!/bin/sh\nexit 0\n' > /usr/bin/systemctl && \
    chmod +x /usr/bin/systemctl

WORKDIR /workspace

# `services` needs systemd, which the container does not run.
RUN \
    --mount=type=bind,from=jdxcode/mise:2026.10.24,source=/usr/local/bin/mise,target=/usr/local/bin/mise \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    mise trust && \
    mise bootstrap --skip tools,services

RUN \
    --mount=type=bind,from=jdxcode/mise:2026.10.24,source=/usr/local/bin/mise,target=/usr/local/bin/mise \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    mise trust && \
    mise install

