from app.models.tables import Contrato
from app.controllers.LogController import LogController
from app.controllers.EmpresaController import EmpresaController
from app.ext.db import db
from sqlalchemy import inspect
from flask import session

class ContratoController:
    @staticmethod
    def create(contrato_form):
        new_contrato = Contrato(nome=contrato_form["nome"],
                                empresa_id=contrato_form["empresa"],
                                empresa_nome=contrato_form["empresa_nome"])
        db.session.add(new_contrato)
        db.session.commit()

        #Salva o log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "CONTRATOS",
                             "CRIAR",
                             f"NOME: {new_contrato.nome}")

    @staticmethod
    def update(form):
        contrato = ContratoController.get(form["_id"])
        
        old_contrato = contrato
        
        contrato.nome = form["nome"]
        contrato.empresa_id = form["empresa"]
        contrato.empresa_nome = EmpresaController.get(_id=form["empresa"]).nome
        db.session.commit()

        #Salva o log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "CONTRATOS",
                             "ALTERAR",
                             f"NOME: {old_contrato.nome} -> {contrato.nome}")
    
    @staticmethod
    def get(id):
        contrato = Contrato.query.get(id)
        return contrato
    
    @staticmethod
    def get_all(filter):
        filtered_data = []
        
        # Get the list of column names dynamically
        mapper = inspect(Contrato)
        columns = [column.key for column in mapper.attrs]

        contratos = Contrato.query.all()
        
        if filter:
            for emp in contratos:
                for column in columns:
                    if filter in str(getattr(emp, column)):
                        filtered_data.append(emp)
                        break
        else:
            return contratos
        return filtered_data
    
    @staticmethod
    def delete(id):
        contrato = Contrato.query.get(id)
        if contrato:

            #Salva o log da ação
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "CONTRATOS",
                                 "DELETAR",
                                 f"NOME: {contrato.nome}")

            db.session.delete(contrato)
            db.session.commit()
            return True
        return False
