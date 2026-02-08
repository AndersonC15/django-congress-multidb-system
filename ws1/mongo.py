
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["sistema_academico"]

eventos_col = db["eventos"]
inscripciones_col = db["inscripciones_evento"]