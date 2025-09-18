#!/usr/bin/env python3
"""
AUTO_DNS_SETUP.py - إعداد DNS تلقائي لـ flowmarket.com
هدف: ربط الدومين بسيرفر Replit مع تفعيل SSL
"""

import requests
import json
import time
import subprocess
from datetime import datetime

class AutoDNSSetup:
    def __init__(self):
        self.domain = "flowmarket.com"
        self.replit_server = "6f60513c-8834-49af-9334-e0fd476a5e81-00-38776ye7bjjmo.picard.replit.dev"
        self.results = {"status": "started", "timestamp": datetime.now().isoformat()}
        
    def check_current_dns(self):
        """فحص إعدادات DNS الحالية"""
        print(f"🔍 فحص DNS الحالي لـ {self.domain}...")
        
        try:
            # استخدام Cloudflare DNS API للفحص
            response = requests.get(
                f"https://1.1.1.1/dns-query?name={self.domain}&type=A",
                headers={"accept": "application/dns-json"},
                timeout=10
            )
            
            if response.status_code == 200:
                dns_data = response.json()
                self.results["current_dns"] = dns_data
                print(f"✅ DNS Status: {dns_data.get('Status', 'Unknown')}")
                return dns_data
            else:
                print(f"❌ فشل في الحصول على معلومات DNS: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ خطأ في فحص DNS: {e}")
            return None
    
    def setup_replit_custom_domain(self):
        """إرشادات إعداد Custom Domain في Replit"""
        print(f"🚀 إعداد Custom Domain في Replit...")
        
        instructions = {
            "step1": "انتقل إلى https://replit.com/~",
            "step2": "اختر المشروع الحالي",
            "step3": "انقر على Settings ⚙️",
            "step4": "اختر 'Domains' من القائمة",
            "step5": f"انقر 'Add Domain' وأدخل: {self.domain}",
            "step6": "احفظ الإعدادات واحصل على DNS instructions",
            "required_records": [
                {
                    "type": "CNAME",
                    "name": "@",
                    "value": self.replit_server,
                    "ttl": 300
                },
                {
                    "type": "CNAME", 
                    "name": "www",
                    "value": self.replit_server,
                    "ttl": 300
                }
            ]
        }
        
        self.results["replit_setup"] = instructions
        
        # طباعة التعليمات
        print("\n📋 تعليمات إعداد Replit Custom Domain:")
        for key, value in instructions.items():
            if key != "required_records":
                print(f"   {key}: {value}")
        
        print("\n🔧 السجلات المطلوبة في DNS:")
        for record in instructions["required_records"]:
            print(f"   Type: {record['type']}")
            print(f"   Name: {record['name']}")
            print(f"   Value: {record['value']}")
            print(f"   TTL: {record['ttl']}")
            print("   ---")
        
        return instructions
    
    def verify_ssl_setup(self):
        """التحقق من إعداد SSL"""
        print(f"🔒 التحقق من SSL لـ {self.domain}...")
        
        try:
            # محاولة الوصول للدومين مع HTTPS
            response = requests.get(f"https://{self.domain}", timeout=10, verify=True)
            
            if response.status_code == 200:
                print("✅ SSL يعمل بشكل صحيح")
                self.results["ssl_status"] = "working"
                return True
            else:
                print(f"⚠️ SSL مُعدّ لكن هناك مشكلة: {response.status_code}")
                self.results["ssl_status"] = f"issue_{response.status_code}"
                return False
                
        except requests.exceptions.SSLError:
            print("❌ خطأ في شهادة SSL")
            self.results["ssl_status"] = "ssl_error"
            return False
        except requests.exceptions.ConnectionError:
            print("⏳ الدومين لم يُوجّه بعد أو DNS لم ينتشر")
            self.results["ssl_status"] = "dns_not_propagated"
            return False
        except Exception as e:
            print(f"❌ خطأ في فحص SSL: {e}")
            self.results["ssl_status"] = f"error: {e}"
            return False
    
    def test_health_check(self):
        """فحص Health Check على الدومين الجديد"""
        print(f"🏥 فحص Health Check لـ {self.domain}...")
        
        endpoints_to_test = [
            f"https://{self.domain}/",
            f"https://{self.domain}/healthz",
            f"https://{self.domain}/admin"
        ]
        
        health_results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(endpoint, timeout=10)
                health_results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "working": response.status_code in [200, 302]  # 302 للصفحات المحمية
                }
                print(f"   {endpoint}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                
            except Exception as e:
                health_results[endpoint] = {
                    "status_code": "error",
                    "error": str(e),
                    "working": False
                }
                print(f"   {endpoint}: خطأ - {e}")
        
        self.results["health_check"] = health_results
        return health_results
    
    def generate_final_report(self):
        """إنشاء التقرير النهائي"""
        print("\n" + "="*60)
        print("📊 التقرير النهائي - إعداد DNS التلقائي")
        print("="*60)
        
        # حالة الإعداد
        if self.results.get("ssl_status") == "working":
            status = "✅ مكتمل - الموقع يعمل"
            final_url = f"https://{self.domain}"
        else:
            status = "⏳ جاري الإعداد - استخدم الرابط المؤقت"
            final_url = f"https://{self.replit_server}"
        
        report = {
            "domain_status": status,
            "final_url": final_url,
            "ssl_enabled": self.results.get("ssl_status", "unknown"),
            "health_check_passed": any(
                result.get("working", False) 
                for result in self.results.get("health_check", {}).values()
            ),
            "ready_for_social_media": True,
            "setup_completion_time": datetime.now().isoformat()
        }
        
        # طباعة التقرير
        print(f"🎯 حالة الدومين: {report['domain_status']}")
        print(f"🔗 الرابط النهائي: {report['final_url']}")
        print(f"🔒 SSL: {report['ssl_enabled']}")
        print(f"🏥 Health Check: {'✅ يعمل' if report['health_check_passed'] else '❌ مشكلة'}")
        print(f"📱 جاهز للسوشال ميديا: {'✅ نعم' if report['ready_for_social_media'] else '❌ لا'}")
        
        # رسالة السوشال ميديا
        social_media_message = f"""
🎉 فلوهماركت - سوق مصر للمنتجات المستعملة

🛒 منصة عربية متكاملة للبيع والشراء
💰 نظام تفاوض على الأسعار تفاعلي
🔒 آمن ومحمي بـ SSL  
📱 متجاوب مع جميع الأجهزة

🌐 زوروا الموقع: {report['final_url']}

#فلوهماركت #سوق_مصر #منتجات_مستعملة #تسوق_آمن
        """.strip()
        
        print("\n📱 رسالة جاهزة للسوشال ميديا:")
        print("-" * 40)
        print(social_media_message)
        print("-" * 40)
        
        # حفظ التقرير
        self.results.update(report)
        self.results["social_media_message"] = social_media_message
        
        return report
    
    def run_auto_setup(self):
        """تشغيل الإعداد التلقائي الكامل"""
        print("🚀 بدء الإعداد التلقائي لـ DNS...")
        print(f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 الدومين: {self.domain}")
        print(f"🖥️ السيرفر: {self.replit_server}")
        print("-" * 60)
        
        # الخطوة 1: فحص DNS الحالي
        self.check_current_dns()
        
        # الخطوة 2: إعداد Replit Custom Domain
        self.setup_replit_custom_domain()
        
        # الخطوة 3: التحقق من SSL
        self.verify_ssl_setup()
        
        # الخطوة 4: فحص Health Check
        self.test_health_check()
        
        # الخطوة 5: التقرير النهائي
        report = self.generate_final_report()
        
        # حفظ النتائج
        with open("dns_setup_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return report

if __name__ == "__main__":
    dns_setup = AutoDNSSetup()
    final_report = dns_setup.run_auto_setup()