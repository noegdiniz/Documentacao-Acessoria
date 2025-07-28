from datetime import datetime
from app.models.tables import Contrato
from app.controllers.LogController import LogController
from app.controllers.EmpresaController import EmpresaController
from app.ext.db import db
from flask import session

class ContratoController:
    @staticmethod
    def create(contrato_form):
        new_contrato = Contrato(nome=contrato_form["nome"],
                                empresa_id=contrato_form["empresa"],
                                empresa_nome=contrato_form["empresa_nome"],
                                dt_inicio=datetime.strptime(contrato_form["dt-inicio"], "%Y-%m-%d"),
                                dt_fim=datetime.strptime(contrato_form["dt-fim"], "%Y-%m-%d")
                                )
        
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
    def get_all():
        filtered_data = Contrato.query.all()
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
    