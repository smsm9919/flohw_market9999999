#!/bin/bash
# Production deployment script for Flohmarkt

echo "🚀 Deploying Flohmarkt to production..."

# Check Render CLI
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    curl -fsSL https://cli.render.com/install | sh
fi

# Deploy using Blueprint
echo "Deploying services with render.yaml..."
render blueprint deploy render_production.yaml

# Display next steps
echo "✅ Deployment initiated!"
echo "📝 Next steps:"
echo "1. Configure DNS records (see dns_production_config.json)"
echo "2. Wait for deployment completion (10-20 minutes)"
echo "3. Wait for DNS propagation (10-60 minutes)"
echo "4. SSL will activate automatically"
echo "🔗 Site will be available at: https://flowmarket.com"
