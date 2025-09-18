# Domain Setup Instructions for flowmarket.com

## Current Status
- DNS Check: No records found for flowmarket.com
- Application: Running on https://6f60513c-8834-49af-9334-e0fd476a5e81-00-38776ye7bjjmo.picard.replit.dev/
- Status: Ready for domain connection

## Required DNS Records

### At your domain registrar (Namecheap/GoDaddy):

1. **A Record:**
   - Host: @
   - Value: 34.232.119.183
   - TTL: 3600

2. **CNAME Record:**
   - Host: www
   - Value: cname.replit.dev
   - TTL: 3600

## Replit Deployment Configuration

1. Go to Replit → Your Project → Deployments
2. Click on "Domains" tab
3. Add domain: flowmarket.com
4. Wait for verification (green checkmark)
5. HTTPS will be automatically enabled

## Verification Commands
```bash
# Check A record
dig flowmarket.com A +short

# Check CNAME record  
dig www.flowmarket.com CNAME +short

# Test HTTPS access
curl -I https://flowmarket.com
curl -I https://www.flowmarket.com
```

## Expected Results After Setup
- https://flowmarket.com → Your Flohmarkt application
- https://www.flowmarket.com → Your Flohmarkt application
- SSL/HTTPS automatically enabled
- Admin login: admin@flowmarket.com / admin123