# -*- coding: utf-8 -*-
# wsgi.py — Gunicorn entrypoint expected by Render (wsgi:app)
import os, importlib
from datetime import timedelta
from flask import Flask, request, make_response

try:
    from werkzeug.middleware.proxy_fix import ProxyFix
except Exception:
    ProxyFix = None

def _load_existing_app():
    import_path = os.getenv("APP_IMPORT_PATH", "").strip()
    candidates = [c for c in [import_path] if c] + [
        "app:app", "main:app", "server:app", "application:app",
        "app:create_app", "main:create_app", "server:create_app",
    ]
    for cand in candidates:
        try:
            mod_name, obj_name = cand.split(":")
            mod = importlib.import_module(mod_name)
            obj = getattr(mod, obj_name)
            app = obj() if callable(obj) else obj
            return app
        except Exception:
            continue
    fb = Flask(__name__)
    @fb.route("/", methods=["GET","HEAD"])
    def _root():
        if request.method == "HEAD":
            return "", 200
        return {"status":"ok","hint":"حدد APP_IMPORT_PATH لتطبيقك الحقيقي"}, 200
    return fb

def _apply_security(app):
    app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY","change-me-now"))
    app.config.setdefault("SESSION_COOKIE_NAME", os.getenv("SESSION_COOKIE_NAME","flow_sess"))
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    if ProxyFix is not None:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    try:
        from flask_cors import CORS
        origins = []
        for key in ("FRONTEND_ORIGIN","FRONTEND_ORIGIN_2","SELF_ORIGIN"):
            v = (os.getenv(key) or "").strip().rstrip("/")
            if v and not v.startswith("http"):
                v = "https://" + v
            if v:
                origins.append(v)
        CORS(app,
             supports_credentials=True,
             resources={r"/api/*": {"origins": origins or ["*"]}},
             expose_headers=["Content-Type","Set-Cookie"],
             allow_headers=["Content-Type","Authorization","X-CSRF-Token"],
             methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
             max_age=86400)
    except Exception:
        pass

    @app.before_request
    def _preflight():
        if request.method == "OPTIONS":
            resp = make_response("", 204)
            origin = request.headers.get("Origin","")
            if origin:
                resp.headers["Access-Control-Allow-Origin"] = origin
                resp.headers["Vary"] = "Origin"
                resp.headers["Access-Control-Allow-Credentials"] = "true"
                resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRF-Token"
            return resp

    @app.after_request
    def _after(resp):
        if request.method == "HEAD" and resp.status_code == 200:
            resp.set_data(b"")
        origin = request.headers.get("Origin","")
        if origin:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
        return resp

    @app.route("/healthz", methods=["GET","HEAD"])
    def _health():
        if request.method == "HEAD":
            return "", 200
        return {"ok": True, "service": os.getenv("SERVICE_NAME","flow-market"), "version": os.getenv("RELEASE","dev")}, 200

    @app.post("/api/debug_set_cookie")
    def _dbg_set_cookie():
        resp = make_response({"set": True})
        resp.set_cookie(app.config["SESSION_COOKIE_NAME"], "test", httponly=True, secure=True, samesite="None", max_age=3600)
        return resp

base = _load_existing_app()
_apply_security(base)
app = base
