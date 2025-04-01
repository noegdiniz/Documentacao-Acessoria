from app.models.tables import Empresa
from app.ext.db import db
from app.controllers.LogController import LogController
from app.controllers.FilterController import FilterController

from flask import session

from sqlalchemy import inspect

class EmpresaController():
    @staticmethod
    def create(nome, chave):
        empresa = Empresa(nome=nome, chave=chave)
        db.session.add(empresa)
        db.session.commit()

        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "EMPRESA",
                             "CRIAR",
                             f"NOME: {empresa.nome} | CHAVE: {empresa.chave}")
    
    @staticmethod
    def update(nome, chave, _id):
        empresa = EmpresaController.get(_id=_id)
        old_empresa_nome = empresa.nome
        old_empresa_chave = empresa.chave
        
        empresa.nome = nome
        empresa.chave = chave
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "EMPRESA",
                             "ALTERAR",
                             f"NOME: {old_empresa_nome} | CHAVE: {old_empresa_chave} -> NOME: {empresa.nome} | CHAVE: {empresa.chave}")
    
    @staticmethod
    def get(chave=None, _id=None):
        if chave:
            empresa = Empresa.query.filter_by(chave=chave).first()
        else:
            empresa = Empresa.query.filter_by(_id=_id).first()
        
        return empresa
    
    @staticmethod
    def get_all(content):
        filtered_emps = FilterController.filter(content, Empresa)
        return filtered_emps
    
    @staticmethod
    def auth(nome, chave):
        if empresa := Empresa.query.filter_by(chave=chave, nome=nome).first():
            #Salva o Log da ação
            LogController.create(nome,
                                 "",
                                 "PRESTADORAS",
                                 "LOGIN PRESTADORA",
                                 "")
            return empresa
        return False
    
    def delete(_id):
        empresa = EmpresaController.get(_id=_id)

        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "EMPRESA",
                             "DELETAR",
                             f"NOME: {empresa.nome}")
        
        db.session.delete(empresa)
        db.session.commit()
    