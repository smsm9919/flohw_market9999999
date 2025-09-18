# DNS Configuration for flowmarket.com

## 📋 DNS Records Required

To connect your flowmarket.com domain to Render, you need to configure these DNS records in your domain registrar's control panel:

### Primary Domain (Apex/Root Domain)
```
Type: CNAME (or ALIAS/ANAME if supported by your provider)
Name: @
Value: flowmarket.onrender.com
TTL: 300 (5 minutes) or Auto
```

### WWW Subdomain
```
Type: CNAME
Name: www
Value: flowmarket.onrender.com
TTL: 300 (5 minutes) or Auto
```

## 🔧 Configuration by DNS Provider

### Popular DNS Providers

#### Cloudflare (Recommended)
1. Login to Cloudflare dashboard
2. Select your domain: flowmarket.com
3. Go to DNS section
4. Add these records:
   ```
   Type: CNAME
   Name: flowmarket.com
   Target: flowmarket.onrender.com
   Proxy status: Proxied (orange cloud) ✅
   
   Type: CNAME
   Name: www
   Target: flowmarket.onrender.com
   Proxy status: Proxied (orange cloud) ✅
   ```

#### GoDaddy
1. Login to GoDaddy account
2. Go to Domain Manager
3. Click DNS for flowmarket.com
4. Add these records:
   ```
   Type: CNAME
   Name: @
   Value: flowmarket.onrender.com
   TTL: 600 seconds
   
   Type: CNAME
   Name: www
   Value: flowmarket.onrender.com
   TTL: 600 seconds
   ```

#### Namecheap
1. Login to Namecheap account
2. Go to Domain List → Manage
3. Advanced DNS tab
4. Add these records:
   ```
   Type: CNAME Record
   Host: @
   Value: flowmarket.onrender.com
   TTL: 300
   
   Type: CNAME Record
   Host: www
   Value: flowmarket.onrender.com
   TTL: 300
   ```

#### Google Domains
1. Login to Google Domains
2. Select flowmarket.com
3. Go to DNS settings
4. Add custom resource records:
   ```
   Name: @
   Type: CNAME
   TTL: 300
   Data: flowmarket.onrender.com
   
   Name: www
   Type: CNAME
   TTL: 300
   Data: flowmarket.onrender.com
   ```

## ⚠️ Important Notes

### Apex Domain CNAME Limitations
Some DNS providers don't support CNAME records for apex domains (@). If you encounter this issue:

1. **Use ALIAS or ANAME records** (if supported):
   ```
   Type: ALIAS (or ANAME)
   Name: @
   Value: flowmarket.onrender.com
   ```

2. **Switch to Cloudflare** (Recommended):
   - Transfer DNS management to Cloudflare (free)
   - Cloudflare supports CNAME flattening for apex domains
   - Additional benefits: CDN, DDoS protection, analytics

3. **Use A records** (Alternative, but requires manual updates):
   - Get current IP address: `dig flowmarket.onrender.com`
   - Create A record pointing to that IP
   - Note: IPs may change, so CNAME is preferred

### DNS Propagation Time
- **Local changes**: 5-15 minutes
- **Global propagation**: 24-48 hours maximum
- **Check propagation**: Use [whatsmydns.net](https://www.whatsmydns.net/)

## 🔍 Verification Steps

### 1. DNS Lookup Test
```bash
# Check apex domain
dig flowmarket.com
nslookup flowmarket.com

# Check www subdomain
dig www.flowmarket.com
nslookup www.flowmarket.com
```

### 2. Expected Results
Both commands should return:
```
flowmarket.com.         300     IN      CNAME   flowmarket.onrender.com.
flowmarket.onrender.com. 300    IN      A       <IP_ADDRESS>
```

### 3. Browser Test
- Visit: http://flowmarket.com (should redirect to https://)
- Visit: https://flowmarket.com (should work)
- Visit: https://www.flowmarket.com (should redirect to https://flowmarket.com)

## 🚨 Troubleshooting

### Common Issues

#### "CNAME not allowed at apex domain"
**Solution**: Use ALIAS/ANAME record or switch to Cloudflare

#### "SSL certificate pending"
**Solution**: Wait 10-15 minutes after DNS propagation for Let's Encrypt certificate generation

#### "Domain not accessible"
**Checks**:
1. Verify DNS records are correct
2. Check DNS propagation with online tools
3. Clear browser cache and DNS cache
4. Try accessing from different device/network

#### "www version not working"
**Solution**: Ensure both @ and www CNAME records are configured

### DNS Cache Clearing

#### Windows
```bash
ipconfig /flushdns
```

#### macOS
```bash
sudo dscacheutil -flushcache
```

#### Linux
```bash
sudo systemctl restart systemd-resolved
```

### Testing Commands
```bash
# Test domain resolution
ping flowmarket.com
ping www.flowmarket.com

# Check HTTP/HTTPS response
curl -I http://flowmarket.com
curl -I https://flowmarket.com

# Test SSL certificate
openssl s_client -connect flowmarket.com:443 -servername flowmarket.com
```

## 📞 Support

### If DNS configuration isn't working:

1. **Double-check DNS records** in your provider's control panel
2. **Wait for propagation** (up to 24 hours)
3. **Test with online tools**:
   - [whatsmydns.net](https://www.whatsmydns.net/)
   - [dnschecker.org](https://dnschecker.org/)
4. **Contact your DNS provider** if records aren't updating
5. **Consider switching to Cloudflare** for easier management

### Render Support
- Domain configuration: [Render Custom Domains Docs](https://render.com/docs/custom-domains)
- SSL certificates: [Render SSL Docs](https://render.com/docs/tls-ssl)

---

## ✅ Final Configuration Summary

After successful DNS configuration, you should have:

- **Root domain**: flowmarket.com → flowmarket.onrender.com
- **WWW subdomain**: www.flowmarket.com → flowmarket.onrender.com
- **SSL certificates**: Auto-generated by Let's Encrypt
- **HTTPS redirect**: Automatic (HTTP → HTTPS)
- **WWW redirect**: Configure in Render settings (www → non-www)

**Test URL**: https://flowmarket.com

Once DNS propagates (usually 10-30 minutes), your Flohmarkt marketplace will be accessible at your custom domain with automatic SSL/HTTPS!