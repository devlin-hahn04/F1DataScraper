#!/usr/bin/env bash

apt-get update
apt-get install -y chromium-browser chromium-chromedriver

echo "Chromium location: $(which chromium-browser)"
echo "Chromedriver location: $(which chromedriver)"
