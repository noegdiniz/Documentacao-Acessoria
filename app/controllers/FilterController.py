# This file is deprecated and maintained for backward compatibility
from app.ext.db import db

class FilterController:
    @staticmethod
    def filter(content, table):
        return table.query.all()
    