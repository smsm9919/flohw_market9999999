# Render Deployment Guide for Flohmarkt (flowmarket.com)

الهدف: نشر الموقع Flohmarkt على Render، ربطه بالدومين flowmarket.com، وتفعيل SSL مع التشغيل 24/7.

---

## 1. خطوات إعداد Render

### الخطوة الأولى: إنشاء PostgreSQL Database
1. اذهب إلى [Render Dashboard](https://dashboard.render.com)
2. اضغط **"New +"** → **"PostgreSQL"**
3. املأ البيانات:
   ```
   Name: flowmarket-db
   Database Name: flowmarket
   User: flowmarket_user
   Region: Frankfurt (الأقرب لمصر)
   Plan: Free (للاختبار) أو Starter ($7/شهر للإنتاج)
   ```
4. اضغط **"Create Database"**
5. انتظر حتى يصبح Status = **"Available"**
6. انسخ **"Internal Database URL"** من صفحة Database

### الخطوة الثانية: إنشاء Web Service
1. اضغط **"New +"** → **"Web Service"**
2. اختر **"Build and deploy from a Git repository"**
3. اربط GitHub account واختر repository المشروع
4. املأ الإعدادات:
   ```
   Name: flowmarket
   Environment: Python 3
   Region: Frankfurt (نفس منطقة Database)
   Branch: main
   Build Command: pip install -r requirements_production.txt
   Start Command: gunicorn -c gunicorn.conf.py app:app
   Plan: Starter ($7/شهر - مطلوب للدومين المخصص)
   ```

### الخطوة الثالثة: إعداد Environment Variables
في صفحة Web Service → **Settings** → **Environment**، أضف:

```bash
SECRET_KEY = [اتركه فارغ - سينشئه Render تلقائياً]
DATABASE_URL = [الصق Internal Database URL من الخطوة الأولى]
ADMIN_EMAIL = admin@flowmarket.com
ADMIN_PASSWORD = admin123
MAX_CONTENT_LENGTH = 16777216
```

### الخطوة الرابعة: تفعيل Health Check
في **Settings** → **Health & Alerts**:
```
Health Check Path: /healthz
```

---

## 2. ربط الدومين المخصص

### في Render Dashboard:
1. اذهب إلى Web Service → **Settings** → **Custom Domains**
2. اضغط **"Add Custom Domain"**
3. أضف:
   - `flowmarket.com`
   - `www.flowmarket.com`

### في لوحة تحكم الدومين:
أضف سجلات DNS التالية:

#### لـ Cloudflare:
```
Type: CNAME
Name: flowmarket.com
Target: flowmarket.onrender.com
Proxy: ON (البرتقالي)

Type: CNAME
Name: www
Target: flowmarket.onrender.com
Proxy: ON (البرتقالي)
```

#### لـ GoDaddy:
```
Type: CNAME
Host: @
Points to: flowmarket.onrender.com
TTL: 600 seconds

Type: CNAME
Host: www
Points to: flowmarket.onrender.com
TTL: 600 seconds
```

#### لـ Namecheap:
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

---

## 3. مراحل التحقق من النجاح

### المرحلة الأولى: التحقق من الخدمات (5-10 دقائق)
✅ **PostgreSQL Database**: يجب أن يظهر **"Available"**  
✅ **Web Service**: يجب أن يظهر **"Live"**  
✅ **Build Logs**: لا توجد أخطاء في Deploy  
✅ **Application Logs**: Database initialization successful  

### المرحلة الثانية: اختبار التطبيق (فوري)
```bash
# اختبار Health Check
curl https://flowmarket.onrender.com/healthz
# المتوقع: {"status":"healthy","database":"connected"}

# اختبار الصفحة الرئيسية
curl -I https://flowmarket.onrender.com
# المتوقع: HTTP/1.1 200 OK
```

### المرحلة الثالثة: انتشار DNS (10-60 دقيقة)
```bash
# اختبار DNS resolution
dig flowmarket.com
nslookup flowmarket.com

# المتوقع: CNAME pointing to flowmarket.onrender.com
```

### المرحلة الرابعة: تفعيل SSL (5-15 دقيقة بعد DNS)
✅ **SSL Certificate**: يظهر **"Active"** في Custom Domains  
✅ **HTTPS Access**: https://flowmarket.com يعمل  
✅ **HTTP Redirect**: http://flowmarket.com يحول إلى https  

---

## 4. الروابط النهائية

بعد إتمام جميع المراحل:
- **الموقع الرئيسي**: https://flowmarket.com
- **لوحة الإدارة**: https://flowmarket.com/admin
- **Health Check**: https://flowmarket.com/healthz
- **API Categories**: https://flowmarket.com/api/categories

---

## 5. بيانات الوصول

### Admin Panel:
```
URL: https://flowmarket.com/admin
Email: admin@flowmarket.com
Password: admin123
```

### Test User:
```
Email: user@flowmarket.com
Password: user123
```

---

## 6. استكشاف الأخطاء

### مشكلة: Build Failed
**الأعراض**: Deploy يفشل أثناء البناء  
**الحل**:
1. تحقق من `requirements_production.txt`
2. تأكد من وجود جميع الملفات المطلوبة
3. راجع Build Logs في Dashboard

### مشكلة: Application Won't Start
**الأعراض**: Build ينجح لكن التطبيق لا يبدأ  
**الحل**:
1. تحقق من `DATABASE_URL` في Environment Variables
2. تأكد من وجود `gunicorn.conf.py`
3. راجع Application Logs

### مشكلة: Database Connection Failed
**الأعراض**: Health check يعود بخطأ database  
**الحل**:
1. تحقق من صحة `DATABASE_URL`
2. تأكد من أن PostgreSQL service نشط
3. اختبر الاتصال من Application Logs

### مشكلة: Domain Not Working
**الأعراض**: flowmarket.com لا يعمل  
**الحل**:
1. تحقق من انتشار DNS: `dig flowmarket.com`
2. انتظر حتى 24 ساعة لانتشار كامل
3. تأكد من صحة CNAME records

### مشكلة: SSL Certificate Pending
**الأعراض**: HTTPS لا يعمل، شهادة في حالة انتظار  
**الحل**:
1. تأكد من انتشار DNS أولاً
2. انتظر 10-15 دقيقة إضافية
3. تحقق من صحة DNS records

---

## 7. المراقبة والصيانة

### مراقبة دورية:
- **Health Check**: مراقبة `/healthz` كل 5 دقائق
- **Uptime**: متابعة status في Render Dashboard
- **Logs**: مراجعة Application Logs أسبوعياً
- **Performance**: مراقبة response time وmemory usage

### النسخ الاحتياطي:
```bash
# أسبوعياً - نسخة احتياطية من قاعدة البيانات
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# حفظ النسخ في مكان آمن خارج Render
```

### التحديثات:
- كل push إلى main branch سيعيد النشر تلقائياً
- يمكن تعطيل Auto-Deploy من Settings إذا رغبت في تحكم يدوي

---

## 8. التكلفة الشهرية

### للتشغيل 24/7 مع Custom Domain:
- **Web Service Starter**: $7/شهر
- **PostgreSQL Starter**: $7/شهر  
- **المجموع**: $14/شهر

### الميزات المشمولة:
✅ Custom domains وSSL certificates  
✅ No sleep (تشغيل مستمر 24/7)  
✅ Auto-scaling حسب الحاجة  
✅ Daily backups لقاعدة البيانات  
✅ مراقبة وlogs مفصلة  

---

## 9. قائمة التحقق النهائية

- [ ] PostgreSQL Database أنشئت وتعمل ✅
- [ ] Web Service deployed وتظهر "Live" ✅
- [ ] Environment Variables مضبوطة ✅
- [ ] Health check يعود بـ 200 ✅
- [ ] Custom domains أضيفت ✅
- [ ] DNS records مضبوطة ✅
- [ ] SSL certificates نشطة ✅
- [ ] https://flowmarket.com يعمل ✅
- [ ] Admin login يعمل ✅
- [ ] لوحة الإدارة تحمّل البيانات ✅
- [ ] إضافة منتجات تعمل ✅
- [ ] قبول/رفض المنتجات يعمل ✅

---

## 🎯 النتيجة النهائية

بعد إتمام جميع الخطوات:

🚀 **Flohmarkt سيكون متاح على**: https://flowmarket.com  
🔐 **مع SSL آمن ومُحدث تلقائياً**  
⚡ **تشغيل مستمر 24/7 بدون انقطاع**  
📊 **لوحة إدارة كاملة مع جميع الوظائف**  
🇪🇬 **منصة مصرية للتجارة الإلكترونية جاهزة للإنتاج**

**الموقع جاهز لاستقبال المستخدمين والبدء في العمل!** 🎉