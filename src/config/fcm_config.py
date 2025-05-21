import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app

load_dotenv()

firebase_json_path = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_json_path:
    raise ValueError("FIREBASE_CREDENTIALS no está definida en .env")

cred = credentials.Certificate(firebase_json_path)
default_app = initialize_app(cred)
