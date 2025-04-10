from app.models.tables import Empresa
from app.ext.db import db
from app.controllers.LogController import LogController
from app.controllers.FilterController import FilterController

from flask import session

from sqlalchemy import inspect

class EmpresaController():
    @staticmethod
    def create(nome, chave, cnpj):
        empresa = Empresa(nome=nome, chave=chave, cnpj=cnpj)
        db.session.add(empresa)
        db.session.commit()

        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "EMPRESA",
                             "CRIAR",
                             f"NOME: {empresa.nome} | CHAVE: {empresa.chave} | CNPJ: {empresa.cnpj}")
    
    @staticmethod
    def update(nome, chave, cnpj, _id):
        empresa = EmpresaController.get(_id=_id)
        old_empresa_nome = empresa.nome
        old_empresa_chave = empresa.chave
        old_empresa_chave = empresa.cnpj
        
        empresa.nome = nome
        empresa.chave = chave
        empresa.cnpj = cnpj

        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "EMPRESA",
                             "ALTERAR",
                             f"NOME: {old_empresa_nome} | CHAVE: {old_empresa_chave} -> NOME: {empresa.nome} | CHAVE: {empresa.chave} | CNPJ: {empresa.cnpj}")
    
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
    