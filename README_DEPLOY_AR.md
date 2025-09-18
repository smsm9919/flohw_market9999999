# FlowMarket جاهز للنشر على Render
## الملفات الأساسية
- `render.yaml` → ملف إعداد Render
- `requirements.txt` → المكتبات المطلوبة
- `wsgi.py` → نقطة دخول Gunicorn
- `.env.example` → مثال لمتغيرات البيئة
- `README_DEPLOY_AR.md` → هذا الشرح

## خطوات سريعة
1. ارفع الملفات دي على GitHub في الجذر.
2. اربط الريبو بـ Render → New Web Service.
3. Render هيقرأ `render.yaml` ويجهز السيرفر تلقائيًا.
4. أضف متغيرات البيئة من `.env.example` في Render Settings.

## Endpoints
- `/healthz` → للتحقق من الصحة.
- `/api/debug_set_cookie` → لاختبار الكوكي.
