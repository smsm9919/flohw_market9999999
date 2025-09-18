#!/usr/bin/env python3
"""
DNS_STATUS_REPORT.py - تقرير شامل لحالة DNS و SSL لـ flowmarket.com
"""

import subprocess
import requests
import json
import time
from datetime import datetime

class DNSStatusChecker:
    def __init__(self):
        self.domain = "flowmarket.com"
        self.www_domain = "www.flowmarket.com"
        self.dns_servers = {
            "Cloudflare": "1.1.1.1",
            "Google": "8.8.8.8", 
            "Quad9": "9.9.9.9",
            "OpenDNS": "208.67.222.222"
        }
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "dns_status": {},
            "ssl_status": {},
            "health_check": {},
            "propagation_status": "checking"
        }
    
    def check_dns_server(self, server_name, server_ip):
        """فحص DNS على خادم محدد"""
        dns_result = {
            "server": server_name,
            "ip": server_ip,
            "apex_record": None,
            "www_record": None,
            "status": "unknown"
        }
        
        try:
            # فحص apex domain
            apex_cmd = f"dig @{server_ip} {self.domain} A +short +time=5"
            apex_result = subprocess.run(apex_cmd.split(), capture_output=True, text=True, timeout=10)
            
            if apex_result.returncode == 0 and apex_result.stdout.strip():
                dns_result["apex_record"] = apex_result.stdout.strip()
                dns_result["status"] = "resolved"
            else:
                dns_result["apex_record"] = "No answer"
                dns_result["status"] = "no_record"
            
            # فحص www subdomain
            www_cmd = f"dig @{server_ip} {self.www_domain} CNAME +short +time=5"
            www_result = subprocess.run(www_cmd.split(), capture_output=True, text=True, timeout=10)
            
            if www_result.returncode == 0 and www_result.stdout.strip():
                dns_result["www_record"] = www_result.stdout.strip()
            else:
                dns_result["www_record"] = "No answer"
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            dns_result["status"] = "timeout"
            dns_result["error"] = str(e)
        
        return dns_result
    
    def check_all_dns_servers(self):
        """فحص جميع خوادم DNS"""
        print("🔍 فحص DNS على جميع الخوادم...")
        
        for server_name, server_ip in self.dns_servers.items():
            print(f"   فحص {server_name} ({server_ip})...")
            result = self.check_dns_server(server_name, server_ip)
            self.results["dns_status"][server_name] = result
            
            # طباعة النتيجة
            if result["status"] == "resolved":
                print(f"   ✅ {server_name}: {result['apex_record']}")
            elif result["status"] == "no_record":
                print(f"   ❌ {server_name}: لا يوجد سجل")
            else:
                print(f"   ⏰ {server_name}: انتهت المهلة الزمنية")
    
    def check_ssl_status(self):
        """فحص حالة SSL"""
        print("🔒 فحص SSL...")
        
        ssl_results = {
            "https_apex": {"status": "unknown", "response_code": None},
            "http_apex": {"status": "unknown", "response_code": None},
            "https_www": {"status": "unknown", "response_code": None}
        }
        
        # فحص HTTPS على apex
        try:
            response = requests.get(f"https://{self.domain}", timeout=10, verify=True)
            ssl_results["https_apex"] = {
                "status": "working",
                "response_code": response.status_code,
                "headers": dict(response.headers)
            }
            print(f"   ✅ HTTPS {self.domain}: {response.status_code}")
            
        except requests.exceptions.SSLError:
            ssl_results["https_apex"]["status"] = "ssl_error"
            print(f"   ❌ HTTPS {self.domain}: خطأ في شهادة SSL")
        except requests.exceptions.ConnectionError:
            ssl_results["https_apex"]["status"] = "connection_error"
            print(f"   ❌ HTTPS {self.domain}: فشل في الاتصال")
        except Exception as e:
            ssl_results["https_apex"]["status"] = f"error: {e}"
            print(f"   ❌ HTTPS {self.domain}: {e}")
        
        # فحص HTTP redirect
        try:
            response = requests.get(f"http://{self.domain}", timeout=10, allow_redirects=False)
            ssl_results["http_apex"] = {
                "status": "redirect" if response.status_code in [301, 302] else "no_redirect",
                "response_code": response.status_code,
                "location": response.headers.get("Location", "")
            }
            print(f"   ↗️ HTTP {self.domain}: {response.status_code} → {response.headers.get('Location', '')}")
            
        except Exception as e:
            ssl_results["http_apex"]["status"] = f"error: {e}"
            print(f"   ❌ HTTP {self.domain}: {e}")
        
        self.results["ssl_status"] = ssl_results
    
    def check_health_endpoint(self):
        """فحص Health Check endpoint"""
        print("🏥 فحص Health Check...")
        
        try:
            response = requests.get(f"https://{self.domain}/healthz", timeout=10)
            
            health_result = {
                "status": "working" if response.status_code == 200 else "error",
                "response_code": response.status_code,
                "response_body": response.text if response.status_code == 200 else None,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                print(f"   ✅ Health Check: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                try:
                    health_data = response.json()
                    print(f"   📊 Status: {health_data.get('status', 'unknown')}")
                    print(f"   🗄️ Database: {health_data.get('database', 'unknown')}")
                except:
                    print(f"   📝 Response: {response.text[:100]}")
            else:
                print(f"   ❌ Health Check: {response.status_code}")
                
        except Exception as e:
            health_result = {"status": "error", "error": str(e)}
            print(f"   ❌ Health Check: {e}")
        
        self.results["health_check"] = health_result
    
    def calculate_propagation_status(self):
        """حساب نسبة انتشار DNS"""
        dns_results = self.results["dns_status"]
        total_servers = len(dns_results)
        resolved_servers = sum(1 for result in dns_results.values() if result["status"] == "resolved")
        
        propagation_percentage = (resolved_servers / total_servers) * 100 if total_servers > 0 else 0
        
        propagation_status = {
            "percentage": propagation_percentage,
            "resolved_servers": resolved_servers,
            "total_servers": total_servers,
            "status": "complete" if propagation_percentage == 100 else "partial" if propagation_percentage > 0 else "none"
        }
        
        # تحديد الخوادم التي لم تُحدث بعد
        not_updated = [name for name, result in dns_results.items() if result["status"] != "resolved"]
        propagation_status["pending_servers"] = not_updated
        
        # تقدير الوقت المتبقي
        if propagation_percentage == 0:
            propagation_status["estimated_time"] = "DNS غير مُعدّ بعد"
        elif propagation_percentage < 100:
            propagation_status["estimated_time"] = "15-60 دقيقة"
        else:
            propagation_status["estimated_time"] = "مكتمل"
        
        self.results["propagation_status"] = propagation_status
        return propagation_status
    
    def generate_recommendations(self):
        """إنشاء التوصيات"""
        recommendations = []
        
        # فحص DNS
        propagation = self.results.get("propagation_status", {})
        if propagation.get("percentage", 0) == 0:
            recommendations.append({
                "type": "dns_setup",
                "priority": "high",
                "message": "DNS غير مُعدّ بعد. يجب إضافة السجلات التالية:",
                "required_records": [
                    {
                        "type": "CNAME",
                        "name": "@",
                        "value": "6f60513c-8834-49af-9334-e0fd476a5e81-00-38776ye7bjjmo.picard.replit.dev",
                        "ttl": 300
                    },
                    {
                        "type": "CNAME", 
                        "name": "www",
                        "value": "6f60513c-8834-49af-9334-e0fd476a5e81-00-38776ye7bjjmo.picard.replit.dev",
                        "ttl": 300
                    }
                ]
            })
        elif propagation.get("percentage", 0) < 100:
            recommendations.append({
                "type": "dns_propagation",
                "priority": "medium",
                "message": f"DNS منتشر جزئياً ({propagation.get('percentage', 0):.0f}%). انتظر {propagation.get('estimated_time', 'غير محدد')}"
            })
        
        # فحص SSL
        ssl_status = self.results.get("ssl_status", {})
        if ssl_status.get("https_apex", {}).get("status") == "connection_error":
            recommendations.append({
                "type": "ssl_wait",
                "priority": "medium", 
                "message": "SSL غير متاح بعد. انتظر اكتمال انتشار DNS ثم Let's Encrypt سيصدر الشهادة تلقائياً"
            })
        
        return recommendations
    
    def print_detailed_report(self):
        """طباعة التقرير المفصل"""
        print("\n" + "="*70)
        print("📊 تقرير DNS و SSL النهائي - flowmarket.com")
        print("="*70)
        print(f"🕐 وقت الفحص: {self.results['timestamp']}")
        print()
        
        # DNS Status
        print("🔍 حالة DNS:")
        print("-" * 40)
        for server_name, result in self.results["dns_status"].items():
            status_icon = "✅" if result["status"] == "resolved" else "❌" if result["status"] == "no_record" else "⏰"
            print(f"   {status_icon} {server_name} ({result['ip']})")
            print(f"      Apex: {result.get('apex_record', 'غير متاح')}")
            print(f"      WWW:  {result.get('www_record', 'غير متاح')}")
            print()
        
        # Propagation Status  
        propagation = self.results.get("propagation_status", {})
        print(f"📈 حالة الانتشار: {propagation.get('percentage', 0):.0f}%")
        print(f"   الخوادم المُحدثة: {propagation.get('resolved_servers', 0)}/{propagation.get('total_servers', 0)}")
        print(f"   الوقت المتبقي: {propagation.get('estimated_time', 'غير محدد')}")
        if propagation.get("pending_servers"):
            print(f"   الخوادم المعلقة: {', '.join(propagation['pending_servers'])}")
        print()
        
        # SSL Status
        print("🔒 حالة SSL:")
        print("-" * 40)
        ssl_status = self.results.get("ssl_status", {})
        for endpoint, data in ssl_status.items():
            status_icon = "✅" if data.get("status") == "working" else "❌"
            print(f"   {status_icon} {endpoint}: {data.get('status', 'unknown')} ({data.get('response_code', 'N/A')})")
        print()
        
        # Health Check
        print("🏥 Health Check:")
        print("-" * 40)
        health = self.results.get("health_check", {})
        if health.get("status") == "working":
            print(f"   ✅ /healthz: {health.get('response_code')} ({health.get('response_time', 0):.2f}s)")
            print(f"   📊 Response: {health.get('response_body', 'غير متاح')[:100]}")
        else:
            print(f"   ❌ /healthz: {health.get('status', 'غير متاح')}")
        print()
        
        # Recommendations
        recommendations = self.generate_recommendations()
        if recommendations:
            print("💡 التوصيات:")
            print("-" * 40)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['message']}")
                if "required_records" in rec:
                    print("   السجلات المطلوبة:")
                    for record in rec["required_records"]:
                        print(f"     Type: {record['type']}")
                        print(f"     Name: {record['name']}")
                        print(f"     Value: {record['value']}")
                        print(f"     TTL: {record['ttl']}")
                        print()
        
        print("="*70)
    
    def run_complete_check(self):
        """تشغيل الفحص الكامل"""
        print("🚀 بدء الفحص الشامل لـ DNS و SSL...")
        
        # فحص DNS
        self.check_all_dns_servers()
        
        # حساب حالة الانتشار
        self.calculate_propagation_status()
        
        # فحص SSL
        self.check_ssl_status()
        
        # فحص Health Check
        self.check_health_endpoint()
        
        # طباعة التقرير
        self.print_detailed_report()
        
        # حفظ النتائج
        with open("dns_status_report.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return self.results

if __name__ == "__main__":
    checker = DNSStatusChecker()
    results = checker.run_complete_check()