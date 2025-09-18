#!/bin/bash
# Automated Deployment Commands for Flohmarkt

echo "🚀 Starting Flohmarkt deployment..."

# Step 1: Verify Render CLI installation
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    curl -fsSL https://cli.render.com/install | sh
fi

# Step 2: Login to Render (requires API key)
echo "Please set your Render API key:"
echo "export RENDER_API_KEY=your_api_key_here"

# Step 3: Deploy using Infrastructure as Code
echo "Deploying services..."
render blueprint deploy render_optimized.yaml

# Step 4: Get service URLs
echo "Getting service information..."
render services list

# Step 5: Setup custom domains
echo "Setting up custom domains..."
# This requires manual DNS configuration

echo "✅ Deployment commands ready"
echo "🔗 Your site will be available at: https://flowmarket.com"
