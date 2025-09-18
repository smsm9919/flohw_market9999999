#!/usr/bin/env python3
"""
Automated deployment script for Flohmarkt on Render
This script automates the deployment process as much as possible
"""

import os
import json
import subprocess
import time
import requests
from datetime import datetime

class FlohmarktDeployer:
    def __init__(self):
        self.project_name = "flowmarket"
        self.domain = "flowmarket.com"
        self.admin_email = "admin@flowmarket.com"
        self.admin_password = "admin123"
        
    def check_prerequisites(self):
        """Check if all required files exist"""
        required_files = [
            'app.py', 'requirements_production.txt', 'gunicorn.conf.py',
            'Procfile', 'render.yaml', 'dns_records.json'
        ]
        
        missing = []
        for file in required_files:
            if not os.path.exists(file):
                missing.append(file)
        
        if missing:
            print(f"❌ Missing files: {missing}")
            return False
        
        print("✅ All deployment files present")
        return True
    
    def test_local_functionality(self):
        """Test all functionality locally before deployment"""
        print("🧪 Testing local functionality...")
        
        tests = {
            "Health Check": self.test_health_check,
            "Homepage": self.test_homepage,
            "Admin Access": self.test_admin_access,
            "API Endpoints": self.test_api_endpoints,
            "Database": self.test_database
        }
        
        results = {}
        for test_name, test_func in tests.items():
            try:
                result = test_func()
                results[test_name] = "✅ PASS" if result else "❌ FAIL"
            except Exception as e:
                results[test_name] = f"❌ ERROR: {str(e)}"
        
        return results
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = requests.get("http://localhost:5000/healthz", timeout=5)
            data = response.json()
            return response.status_code == 200 and data.get('status') == 'healthy'
        except:
            return False
    
    def test_homepage(self):
        """Test homepage loads correctly"""
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            return response.status_code == 200 and 'فلو ماركت' in response.text
        except:
            return False
    
    def test_admin_access(self):
        """Test admin panel accessibility"""
        try:
            response = requests.get("http://localhost:5000/admin", timeout=5, allow_redirects=False)
            # Should redirect to login (302) or show admin page (200)
            return response.status_code in [200, 302]
        except:
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints availability"""
        try:
            # Test public API endpoints
            response = requests.get("http://localhost:5000/api/categories", timeout=5)
            # Should return 401 (requires auth) or 200 (public access)
            return response.status_code in [200, 401]
        except:
            return False
    
    def test_database(self):
        """Test database connectivity"""
        try:
            response = requests.get("http://localhost:5000/healthz", timeout=5)
            data = response.json()
            return data.get('database') == 'connected'
        except:
            return False
    
    def generate_render_blueprint(self):
        """Generate optimized render.yaml"""
        render_config = {
            "databases": [{
                "name": "flowmarket-db",
                "databaseName": "flowmarket",
                "user": "flowmarket_user",
                "plan": "starter",
                "region": "frankfurt"
            }],
            "services": [{
                "type": "web",
                "name": "flowmarket",
                "runtime": "python3",
                "plan": "starter",
                "region": "frankfurt",
                "buildCommand": "pip install -r requirements_production.txt",
                "startCommand": "gunicorn -c gunicorn.conf.py app:app",
                "healthCheckPath": "/healthz",
                "autoDeploy": True,
                "envVars": [
                    {"key": "SECRET_KEY", "generateValue": True},
                    {"key": "DATABASE_URL", "fromDatabase": {"name": "flowmarket-db", "property": "connectionString"}},
                    {"key": "ADMIN_EMAIL", "value": self.admin_email},
                    {"key": "ADMIN_PASSWORD", "value": self.admin_password},
                    {"key": "MAX_CONTENT_LENGTH", "value": "16777216"}
                ],
                "domains": [self.domain, f"www.{self.domain}"]
            }]
        }
        
        # Save as YAML
        import yaml
        with open('render_optimized.yaml', 'w') as f:
            yaml.dump(render_config, f, default_flow_style=False)
        
        print("✅ Generated render_optimized.yaml")
        return True
    
    def generate_deployment_commands(self):
        """Generate shell commands for deployment"""
        commands = f"""#!/bin/bash
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
echo "🔗 Your site will be available at: https://{self.domain}"
"""
        
        with open('deploy.sh', 'w') as f:
            f.write(commands)
        
        os.chmod('deploy.sh', 0o755)
        print("✅ Generated deploy.sh script")
        return True
    
    def generate_dns_instructions(self):
        """Generate DNS configuration instructions"""
        dns_config = {
            "domain": self.domain,
            "records": [
                {
                    "type": "CNAME",
                    "name": "@",
                    "value": f"{self.project_name}.onrender.com",
                    "ttl": 300
                },
                {
                    "type": "CNAME", 
                    "name": "www",
                    "value": f"{self.project_name}.onrender.com",
                    "ttl": 300
                }
            ],
            "providers": {
                "cloudflare": {
                    "instructions": "Add CNAME records with Proxy ON (orange cloud)",
                    "ssl": "Full (strict) SSL mode recommended"
                },
                "godaddy": {
                    "instructions": "Add CNAME records in DNS management",
                    "ssl": "SSL will be provided by Render"
                },
                "namecheap": {
                    "instructions": "Add CNAME records in Advanced DNS",
                    "ssl": "SSL will be provided by Render"
                }
            }
        }
        
        with open('dns_setup_instructions.json', 'w') as f:
            json.dump(dns_config, f, indent=2)
        
        print("✅ Generated DNS setup instructions")
        return True
    
    def create_monitoring_script(self):
        """Create monitoring script for post-deployment"""
        monitoring_script = f"""#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime

def monitor_deployment():
    \"\"\"Monitor the deployed site\"\"\"
    domain = "{self.domain}"
    endpoints = [
        f"https://{domain}",
        f"https://{domain}/healthz", 
        f"https://{domain}/admin",
        f"https://{domain}/api/categories"
    ]
    
    print(f"🔍 Monitoring {domain}...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            status = "✅ UP" if response.status_code in [200, 302, 401] else "❌ DOWN"
            print(f"{endpoint}: {status} ({response.status_code})")
        except Exception as e:
            print(f"{endpoint}: ❌ ERROR - {str(e)}")
    
    # Check SSL
    try:
        import ssl
        import socket
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                print(f"🔒 SSL Certificate: ✅ Valid (Expires: {cert['notAfter']})")
    except Exception as e:
        print(f"🔒 SSL Certificate: ❌ Error - {str(e)}")

if __name__ == "__main__":
    monitor_deployment()
"""
        
        with open('monitor_deployment.py', 'w') as f:
            f.write(monitoring_script)
        
        os.chmod('monitor_deployment.py', 0o755)
        print("✅ Generated monitoring script")
        return True
    
    def run_deployment_preparation(self):
        """Run complete deployment preparation"""
        print("🚀 Preparing Flohmarkt for production deployment...")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Test local functionality
        print("\\n🧪 Running comprehensive tests...")
        test_results = self.test_local_functionality()
        
        for test, result in test_results.items():
            print(f"  {test}: {result}")
        
        # Check if all tests passed
        failed_tests = [test for test, result in test_results.items() if "❌" in result]
        if failed_tests:
            print(f"\\n❌ Failed tests: {failed_tests}")
            print("Please fix issues before deployment")
            return False
        
        # Generate deployment files
        print("\\n📦 Generating deployment files...")
        self.generate_render_blueprint()
        self.generate_deployment_commands()
        self.generate_dns_instructions()
        self.create_monitoring_script()
        
        print("\\n✅ Deployment preparation complete!")
        print("=" * 60)
        print("Next steps:")
        print("1. Run: ./deploy.sh (requires Render API key)")
        print("2. Configure DNS using dns_setup_instructions.json")
        print("3. Wait 30-90 minutes for propagation")
        print("4. Monitor with: python monitor_deployment.py")
        print(f"\\n🎯 Final result: https://{self.domain}")
        
        return True

def main():
    deployer = FlohmarktDeployer()
    success = deployer.run_deployment_preparation()
    
    if success:
        print("\\n🎉 Flohmarkt is ready for production deployment!")
    else:
        print("\\n❌ Deployment preparation failed")
    
    return success

if __name__ == "__main__":
    main()