from app.models.tables import CUBO
from app.controllers.LogController import LogController
from app.ext.db import db
from sqlalchemy import inspect
from flask import session
import os


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "13256348917-k29q8fpfoblkan04mfadpr8fe6vafkg6.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "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")

class CuboController:
    @staticmethod
    def create(cubo_form):
        # Create a new CUBO entry

        new_cubo = CUBO(
            categoria_id=cubo_form["categoria"],
            categoria_nome=cubo_form["categoria_nome"],
            contrato_id=cubo_form["contrato"],
            contrato_nome=cubo_form["contrato_nome"],
            prazo=cubo_form["prazo"],
            perfil_id=cubo_form["perfil"],
            perfil_nome=cubo_form["perfil_nome"],
            pasta_drive=cubo_form["drive"]
        )
        
        db.session.add(new_cubo)
        db.session.commit()

        #Salva o log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "DADOS",
                             "CRIAR",
                             f"PERFIL: {new_cubo.perfil_nome} | CATEGORIA: {new_cubo.categoria_nome}")
    
    @staticmethod
    def update(form):
        cubo = CuboController.get(form["_id"])

        old_cubo = cubo

        cubo.categoria_id = form["categoria"]
        cubo.categoria_nome = form["categoria_nome"]
        cubo.contrato_id = form["contrato"]
        cubo.contrato_nome = form["contrato_nome"]
        cubo.prazo = form["prazo"]
        cubo.perfil_id = form["perfil"]
        cubo.perfil_nome = form["perfil_nome"]

        db.session.commit()
        
        #Salva o log da ação 
        LogController.create(session["nome"],
                             session["perfil"],
                            "DADOS",
                            "ALTERAR",
                            f"NOME: {old_cubo.nome} -> {cubo.nome}")
    
    @staticmethod
    def get(id):
        # Retrieve a CUBO by its ID
        cubo = CUBO.query.get(id)
        return cubo

    @staticmethod
    def get_all(filter):
        filtered_data = []
        
        # Get the list of column names dynamically
        mapper = inspect(CUBO)
        columns = [column.key for column in mapper.attrs]

        cubos = CUBO.query.all()
        
        if filter:
            for emp in cubos:
                for column in columns:
                    if filter in str(getattr(emp, column)):
                        filtered_data.append(emp)
                        break
        else:
            return cubos
        
        return filtered_data

    @staticmethod
    def delete(id):
        # Delete a CUBO by its ID
        cubo = CUBO.query.get(id)
        if cubo:
            db.session.delete(cubo)
            db.session.commit()

            #Salva o log da ação 
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "DADOS",
                                 "DELETAR",
                                 f"PERFIL: {cubo.perfil_nome} | CATEGORIA: {cubo.categoria_nome}")
            return True
        return False

## Eis a questao do prazo...
## Resolver