#!/bin/bash
# Deploy latest changes on the VPS.
# Usage: ssh into VPS, then run: ./deploy.sh

set -e

cd ~/aichoir

echo "Pulling latest changes..."
git pull

echo "Building frontend..."
npm run build

echo "Restarting server..."
sudo systemctl restart aichoir

echo "Done. Checking status..."
sudo systemctl status aichoir --no-pager
