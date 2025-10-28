#!/usr/bin/env bash

sudo apt-get install curl libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev clang libclang-dev llvm llvm-dev
curl https://sh.rustup.rs -sSf | sh -s -- -y
curl https://get.volta.sh | bash

$HOME/.volta/bin/volta install node@lts pnpm
