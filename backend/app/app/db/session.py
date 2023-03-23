from pymongo import MongoClient
from app.core.config import settings


def maker():
    return MongoClient(settings.MONGODB_URI).test

SessionLocal = maker