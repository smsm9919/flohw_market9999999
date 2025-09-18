# Placeholder app — استبدله بتطبيقك الفعلي أو استخدم APP_IMPORT_PATH
from flask import Flask
app = Flask(__name__)

@app.get("/")
def index():
    return {"msg": "Placeholder running. حدد APP_IMPORT_PATH لتطبيقك الفعلي."}, 200
