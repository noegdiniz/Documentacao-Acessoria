from app.controllers.DocsControlller import DocsController
from app.models.tables import User
from app.ext.db import db
from app.controllers.LogController import LogController
from app.controllers.PerfilController import PerfilController
from app.controllers.FilterController import FilterController
from flask import session

class UserController:
    
    @staticmethod
    def create(_id, nome, file, email):
        user = User(_id=_id, nome=nome, file=file, email=email)
        db.session.add(user)
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                            "USER",
                            "CRIAR",
                            f"NOME: {user.nome} EMAIL: {user.email}")
        
        return user
    
    @staticmethod
    def get(user_id):
        return User.query.filter_by(_id=user_id).first()

    @staticmethod
    def get_all(filter):
        filtered_data = FilterController.filter(filter, User)
        
        return filtered_data

    @staticmethod
    def get_docs(user_id):
        return DocsController.get_all_by_user(user_id)
    
    @staticmethod
    def delete(_id):
        user = User.query.get(_id)
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "PERFIL",
                             "DELETAR",
                             f"NOME: {user.nome}")
        
        db.session.delete(user)
        db.session.commit()
        
    def update(user_id, perfil_id):
        user = UserController.get(user_id)
        old_user_perfil = user.perfil
        
        user.perfil = PerfilController.get(perfil_id).nome
        user.perfil_id = perfil_id
        
        new_user_perfil = user.perfil

        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "USER",
                             "ALTERAR",
                             f"PERFIL: {old_user_perfil} -> {new_user_perfil}")
    