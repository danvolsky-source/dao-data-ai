# Vercel Serverless Function для DAO Analytics API
import sys
import os

# Добавляем путь к backend модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.main import app

# Vercel автоматически обнаруживает ASGI приложения
app = app
