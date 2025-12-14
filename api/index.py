# Vercel Serverless Function для DAO Analytics API
import sys
import os

# Добавляем путь к backend модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.main import app
from mangum import Mangum

# Создаем handler для Vercel
handler = Mangum(app, lifespan="off")
