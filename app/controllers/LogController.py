from app.models.tables import Log
from datetime import datetime
from app.ext.db import db

from app.controllers.FilterController import FilterController # type: ignore

class LogController:
    @staticmethod
    def create(user, perfil, menu, action, info:str):
        log = Log(user_name=user,
                    user_perfil=perfil,
                    menu=menu,
                    action=action,
                    info=info.upper(),
                    date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        
        db.session.add(log)
        db.session.commit()
    
    def get(id):
        return Log.query.get(id)
    
    def get_all(filter):
        logs = FilterController.filter(filter, Log)
        logs.reverse()
        return logs
        
    def delete(id):
        log = Log.query.get(id)
        db.session.remove(log)
        db.session.commit()
