import os
import string
import random


BASE_DIR = os.path.abspath('.')

SECRET_KEY = ''.join(random.choice(string.ascii_letters) for i in range(42))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite')
