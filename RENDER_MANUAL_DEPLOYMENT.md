# 📋 دليل النشر اليدوي السريع على Render

## 🎯 الهدف: نشر flowmarket.com خلال 15 دقيقة

### الخطوة 1: إنشاء Web Service
1. اذهب إلى https://dashboard.render.com
2. انقر "New" → "Web Service"
3. اختر "Deploy from a Git repository" أو "Deploy from source"

### الخطوة 2: إعدادات الخدمة
```
Name: flohmarkt-production
Runtime: Python 3
Region: Oregon (recommended)
Branch: main
Root Directory: . (root)
```

### الخطوة 3: أوامر البناء والتشغيل
```
Build Command: pip install -r requirements_production.txt
Start Command: gunicorn --config gunicorn_production.conf.py main:app
```

### الخطوة 4: متغيرات البيئة
```
FLASK_ENV=production
SECRET_KEY=[Auto Generate]
ADMIN_EMAIL=admin@flowmarket.com
ADMIN_PASSWORD=admin123
PYTHONPATH=.
```

### الخطوة 5: إنشاء قاعدة البيانات
1. في نفس الصفحة، انقر "Add Database"
2. اختر "PostgreSQL"
3. اسم قاعدة البيانات: flohmarkt-postgres
4. خطة: Starter (مجاني)

### الخطوة 6: ربط قاعدة البيانات
```
DATABASE_URL=[سيتم إنشاؤها تلقائياً]
```

### الخطوة 7: إعدادات إضافية
```
Health Check Path: /healthz
Auto-Deploy: Yes
```

### الخطوة 8: إضافة الدومين المخصص
1. بعد النشر، اذهب إلى Settings
2. انقر "Custom Domains"
3. أضف: flowmarket.com
4. أضف: www.flowmarket.com
5. فعّل "Redirect www to apex domain"

### الخطوة 9: تكوين DNS
في موفر الدومين (Cloudflare/Namecheap/GoDaddy):
```
Type: A
Name: @
Value: [IP من Render Dashboard]

Type: CNAME
Name: www
Value: flowmarket.com
```

### الخطوة 10: التحقق
1. انتظر 5-15 دقيقة لانتشار DNS
2. تحقق من https://flowmarket.com
3. تحقق من https://flowmarket.com/healthz

---

## 🔄 البديل: استخدام Blueprint

1. في Render Dashboard، انقر "New" → "Blueprint"
2. ارفع ملف `render_production_final.yaml`
3. اتبع التعليمات التلقائية
4. أضف الدومين المخصص كما هو موضح أعلاه

---

**الوقت المتوقع**: 15-30 دقيقة
**النتيجة**: https://flowmarket.com يعمل بـ SSL كامل