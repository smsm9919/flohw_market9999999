# دليل النشر التلقائي لـ Flohmarkt على Render

## 🎯 الهدف
نشر موقع Flohmarkt تلقائياً على https://flowmarket.com مع SSL وتشغيل 24/7

## 🔧 الأدوات المطلوبة

### 1. حساب Render
- اذهب إلى https://dashboard.render.com
- سجل حساب جديد أو ادخل لحسابك
- احصل على API Key من Settings > API Keys

### 2. بيانات DNS Provider
- **Cloudflare**: API Token من My Profile > API Tokens
- **Namecheap**: API Key من Profile > Tools > API Access
- **GoDaddy**: API Key من Developer Portal

## 🚀 طرق النشر

### الطريقة 1: نشر تلقائي بالكامل (مع API Keys)
```bash
# ضبط المتغيرات
export RENDER_API_KEY="your_render_api_key"
export CLOUDFLARE_API_TOKEN="your_cloudflare_token"  # اختياري

# تشغيل النشر التلقائي
python render_deploy_script.py
```

### الطريقة 2: نشر باستخدام Render CLI
```bash
# تثبيت Render CLI
curl -fsSL https://cli.render.com/install | sh

# تسجيل الدخول
render login

# نشر باستخدام Blueprint
render blueprint deploy render_production.yaml
```

### الطريقة 3: نشر عبر Dashboard (يدوي)
1. اذهب إلى https://dashboard.render.com
2. انقر "New" > "Blueprint"
3. ارفع ملف `render_production.yaml`
4. اتبع التعليمات لإكمال النشر

## 📋 خطوات النشر التفصيلية

### الخطوة 1: إعداد قاعدة البيانات
```yaml
# في render_production.yaml
databases:
  - name: flowmarket-db
    databaseName: flowmarket
    user: flowmarket_user
    plan: starter
    region: frankfurt
```

### الخطوة 2: إعداد Web Service
```yaml
services:
  - type: web
    name: flowmarket
    runtime: python3
    buildCommand: pip install -r requirements_production.txt
    startCommand: gunicorn -c gunicorn.conf.py app:app
    healthCheckPath: /healthz
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: flowmarket-db
          property: connectionString
```

### الخطوة 3: ربط الدومين
```bash
# إضافة الدومين المخصص
render service domain add --service flowmarket --domain flowmarket.com
render service domain add --service flowmarket --domain www.flowmarket.com
```

### الخطوة 4: ضبط DNS
```json
// إضافة في DNS Provider
{
  "type": "CNAME",
  "name": "@",
  "value": "flowmarket.onrender.com",
  "ttl": 300
},
{
  "type": "CNAME", 
  "name": "www",
  "value": "flowmarket.onrender.com",
  "ttl": 300
}
```

## 🔒 الأمان وإدارة البيانات

### حماية بيانات الاعتماد
```python
# مثال على الحذف الآمن للبيانات
def cleanup_credentials():
    import os
    sensitive_vars = [
        'RENDER_API_KEY',
        'CLOUDFLARE_API_TOKEN',
        'NAMECHEAP_API_KEY'
    ]
    
    for var in sensitive_vars:
        if var in os.environ:
            del os.environ[var]
    
    # حذف الملفات المؤقتة
    temp_files = ['.credentials', 'temp_keys.json']
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
```

### متغيرات البيئة المطلوبة
```bash
DATABASE_URL=postgresql://...  # تلقائي من Render
SECRET_KEY=auto_generated      # تلقائي من Render
ADMIN_EMAIL=admin@flowmarket.com
ADMIN_PASSWORD=admin123
MAX_CONTENT_LENGTH=16777216
```

## 📊 مراقبة النشر

### Health Check
```bash
# اختبار الصحة
curl https://flowmarket.com/healthz

# النتيجة المتوقعة:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-27T...",
  "version": "1.0.0"
}
```

### اختبارات الوظائف
```bash
# اختبار الصفحة الرئيسية
curl -I https://flowmarket.com

# اختبار لوحة الإدارة
curl -I https://flowmarket.com/admin

# اختبار API
curl https://flowmarket.com/api/categories
```

## 🔄 النسخ الاحتياطي

### إعداد النسخ الاحتياطي التلقائي
```yaml
# في render_production.yaml
databases:
  - name: flowmarket-db
    backup:
      enabled: true
      schedule: "0 2 * * *"  # يومياً في 2 صباحاً UTC
      retention: 30          # الاحتفاظ لمدة 30 يوم
```

### استعادة النسخة الاحتياطية
```bash
# عرض النسخ المتاحة
render database backup list --database flowmarket-db

# استعادة نسخة احتياطية
render database backup restore --database flowmarket-db --backup backup_id
```

## 📈 مراقبة الأداء

### مراقبة Uptime
```bash
# إعداد مراقبة تلقائية
render service monitor create --service flowmarket \
  --url https://flowmarket.com/healthz \
  --interval 30s
```

### إعادة التشغيل التلقائي
```yaml
# في render_production.yaml
services:
  - name: flowmarket
    autoRestart: true
    healthCheckPath: /healthz
    healthCheckGracePeriod: 30s
```

## 🎯 التحقق من النجاح

### قائمة التحقق النهائية
- [ ] https://flowmarket.com يفتح بنجاح
- [ ] SSL نشط (قفل أخضر في المتصفح)
- [ ] https://flowmarket.com/admin يعمل
- [ ] تسجيل دخول admin@flowmarket.com/admin123 يعمل
- [ ] إضافة منتج جديد يعمل مع رفع الصور
- [ ] https://flowmarket.com/healthz يرجع {"status":"healthy"}
- [ ] جميع بيانات الاعتماد تم حذفها

### معلومات الاتصال النهائية
```
الموقع: https://flowmarket.com
الإدارة: https://flowmarket.com/admin
البريد: admin@flowmarket.com
كلمة المرور: admin123
Health Check: https://flowmarket.com/healthz
```

## 🔐 حذف البيانات الحساسة

بعد إتمام النشر، تأكد من:
1. حذف جميع API Keys من متغيرات البيئة
2. حذف الملفات المؤقتة
3. مسح سجلات الأوامر التي تحتوي على كلمات مرور
4. التأكد من عدم حفظ البيانات في أي ملف أو سجل

```bash
# تشغيل التنظيف النهائي
python -c "
import os
for var in ['RENDER_API_KEY', 'CLOUDFLARE_API_TOKEN']:
    if var in os.environ:
        del os.environ[var]
print('✅ جميع البيانات الحساسة تم حذفها')
"
```