import os
import string
import random

BASE_DIR = os.path.abspath('.')
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True 
SESSION_COOKIE_SAMESITE = 'Strict'

SECRET_KEY = os.environ.get("SECRET_KEY", 
                            ''.join(random.choice(string.ascii_letters) for i in range(42)))
if not os.environ.get("SECRET_KEY"):
    print("WARNING: SECRET_KEY not set in environment. Using a randomly generated key. THIS IS INSECURE FOR PRODUCTION!")

SQLALCHEMY_TRACK_MODIFICATIONS = False
# Use DATABASE_URL environment variable or fallback to SQLite
SQLALCHEMY_DATABASE_URI = 'postgresql://sa:senha123@localhost:6543/docs' #os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite'))
