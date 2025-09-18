
# -*- coding: utf-8 -*-
# auth_cors_fix.py
import os
from datetime import timedelta
from urllib.parse import urlparse
from flask import request, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
try:
    from flask_cors import CORS
except Exception as e:
    raise RuntimeError("flask-cors not installed. Add to requirements.txt") from e

DEFAULT_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "flow_sess")

def _origin_whitelist():
    fronts = []
    for key in ("FRONTEND_ORIGIN", "FRONTEND_ORIGIN_2", "SELF_ORIGIN"):
        v = os.getenv(key)
        if not v:
            continue
        v = v.strip().rstrip("/")
        if v and not v.startswith("http"):
            v = "https://" + v
        fronts.append(v)
    return set(fronts)

def _is_allowed_origin(origin: str, allowed: set) -> bool:
    if not origin or not allowed:
        return False
    try:
        from urllib.parse import urlparse
        o = urlparse(origin)
        norm = f"{o.scheme}://{o.netloc}"
        return norm in allowed
    except Exception:
        return False

def apply_security(app):
    # 1) ثابت سر الجلسة
    app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "change-me-now"))

    # 2) إعدادات الكوكي
    app.config.update(
        SESSION_COOKIE_NAME=DEFAULT_COOKIE_NAME,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="None",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )

    cookie_domain = os.getenv("SESSION_COOKIE_DOMAIN")
    if cookie_domain:
        app.config["SESSION_COOKIE_DOMAIN"] = cookie_domain

    # 3) الثقة في البروكسي
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # 4) CORS
    origins = list(_origin_whitelist()) or ["*"]
    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": origins}},
        expose_headers=["Content-Type", "Set-Cookie"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=86400,
    )

    allowed = _origin_whitelist()

    @app.before_request
    def _cors_preflight():
        if request.method == "OPTIONS":
            resp = make_response("", 204)
            req_origin = request.headers.get("Origin", "")
            if _is_allowed_origin(req_origin, allowed):
                resp.headers["Access-Control-Allow-Origin"] = req_origin
                resp.headers["Vary"] = "Origin"
                resp.headers["Access-Control-Allow-Credentials"] = "true"
                resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRF-Token"
            return resp

    @app.after_request
    def _add_cors_headers(resp):
        req_origin = request.headers.get("Origin", "")
        if _is_allowed_origin(req_origin, allowed):
            resp.headers["Access-Control-Allow-Origin"] = req_origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
        return resp

    @app.get("/healthz")
    def _health():
        return {"ok": True, "service": "flow-market", "version": os.getenv("RELEASE", "dev")}, 200

    @app.post("/api/debug_set_cookie")
    def _debug_set_cookie():
        resp = make_response({"set": True})
        resp.set_cookie(
            DEFAULT_COOKIE_NAME,
            "test-cookie",
            httponly=True,
            secure=True,
            samesite="None",
            max_age=3600,
        )
        return resp
