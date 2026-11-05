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
#
# - Disable apt recommends: they pull GUI/GPU/documentation packages that are
#   not needed to build, lint or test in CI (about 250 MB).
# - Drop package documentation and manpages in the same layer as the install;
#   deleting them afterwards would not shrink the image (lower layers keep the
#   files).
RUN \
    --mount=type=bind,from=jdxcode/mise:2026.10.24,source=/usr/local/bin/mise,target=/usr/local/bin/mise \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    printf 'APT::Install-Recommends "false";\n' > /etc/apt/apt.conf.d/99no-install-recommends && \
    mise trust && \
    mise bootstrap --skip tools,services && \
    rm -rf /usr/share/doc/* /usr/share/man/*

# Install the mise-managed tools declared at the repo root.
#
# The lock file must be mounted as well. Without it mise regenerates the lock
# inside the build, which downloads release artifacts for every supported
# platform (macOS/Windows/arm64/...) and fails when GitHub returns transient
# errors. `--locked` also fails fast when mise.toml and mise.lock are out of
# sync.
#
# Component toolchains are intentionally not installed here. They are installed
# per job by jdx/mise-action (which caches them); baking them in would add
# ~1.5 GB to every image pull to save only a few seconds per job.
RUN \
    --mount=type=bind,from=jdxcode/mise:2026.10.24,source=/usr/local/bin/mise,target=/usr/local/bin/mise \
    --mount=type=bind,source=mise.toml,target=/workspace/mise.toml \
    --mount=type=bind,source=mise.lock,target=/workspace/mise.lock \
    mise trust && \
    mise install --locked

