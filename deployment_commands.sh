
# Render Deployment Commands for Flohmarkt

## 1. Create PostgreSQL Database
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "postgresql",
    "name": "flowmarket-db", 
    "databaseName": "flowmarket",
    "databaseUser": "flowmarket_user",
    "plan": "starter",
    "region": "frankfurt"
  }'

## 2. Create Web Service  
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "flowmarket",
    "runtime": "python3",
    "plan": "starter", 
    "region": "frankfurt",
    "repo": "YOUR_GITHUB_REPO_URL",
    "buildCommand": "pip install -r requirements_production.txt",
    "startCommand": "gunicorn -c gunicorn.conf.py app:app",
    "healthCheckPath": "/healthz",
    "envVars": [
      {"key": "SECRET_KEY", "generateValue": true},
      {"key": "DATABASE_URL", "fromDatabase": {"name": "flowmarket-db", "property": "connectionString"}},
      {"key": "ADMIN_EMAIL", "value": "admin@flowmarket.com"},
      {"key": "ADMIN_PASSWORD", "value": "admin123"},
      {"key": "MAX_CONTENT_LENGTH", "value": "16777216"}
    ]
  }'

## 3. Add Custom Domains
curl -X POST https://api.render.com/v1/services/SERVICE_ID/custom-domains \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "flowmarket.com"}'

curl -X POST https://api.render.com/v1/services/SERVICE_ID/custom-domains \
  -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "www.flowmarket.com"}'

## 4. Verification Commands
curl -s https://flowmarket.onrender.com/healthz
curl -s https://flowmarket.com/healthz
curl -I https://flowmarket.com
