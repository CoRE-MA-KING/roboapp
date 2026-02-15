FROM ubuntu:24.04

LABEL org.opencontainers.image.source=https://github.com/${GITHUB_REPOSITORY}
LABEL org.opencontainers.image.description="CI image for roboapp with all system dependencies pre-installed"

ENV DEBIAN_FRONTEND=noninteractive
ENV ROBOAPP_CI_CONTAINER=true

# Install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gpg \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Setup Zenoh Repository
RUN mkdir -p /etc/apt/keyrings && \
    curl -L https://download.eclipse.org/zenoh/debian-repo/zenoh-public-key | gpg --dearmor --yes --output /etc/apt/keyrings/zenoh-public-key.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/zenoh-public-key.gpg] https://download.eclipse.org/zenoh/debian-repo/ /" | tee /etc/apt/sources.list.d/zenoh.list >/dev/null

# Install all dependencies
RUN apt-get update && apt-get install -y \
    # Common
    build-essential cmake ninja-build \
    libzenohc=1.6.2 libzenohc-dev=1.6.2 libzenohcpp-dev=1.6.2 zenohd \
    # UI System
    libwebkit2gtk-4.1-dev file libxdo-dev libssl-dev \
    libayatana-appindicator3-dev librsvg2-dev clang libclang-dev llvm llvm-dev \
    # Main Camera System
    nasm \
    # Lidar System
    libgflags-dev libopencv-dev nlohmann-json3-dev \
    clang-tidy clang-format \
    libprotobuf-dev protobuf-compiler \
    # UART Bridge
    socat \
    && apt-mark hold libzenohc libzenohc-dev libzenohcpp-dev zenohd \
    && rm -rf /var/lib/apt/lists/*

# Pre-disable zenohd
RUN systemctl disable zenohd --now || true

# Install mise (optional, as mise-action will install it anyway, but good for local use)
RUN curl https://mise.jdx.dev/install.sh | sh
ENV PATH="/root/.local/share/mise/bin:/root/.local/share/mise/shims:$PATH"

WORKDIR /workspace
