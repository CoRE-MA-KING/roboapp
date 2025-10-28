#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install curl build-essential cmake nasm
curl https://sh.rustup.rs -sSf | sh -s -- -y
