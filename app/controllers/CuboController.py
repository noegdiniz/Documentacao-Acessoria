from datetime import datetime
from app.controllers.FilterController import FilterController
from app.models.tables import CUBO, Categoria, Perfil
from app.controllers.LogController import LogController
from app.ext.db import db
from sqlalchemy import inspect
from flask import session
import os
import re


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "13256348917-k29q8fpfoblkan04mfadpr8fe6vafkg6.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "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")

class CuboController:
    @staticmethod
    def create(cubo_form):
        # Create a new CUBO entry
        pattern_perfil = r'"(\d+)"'
        
        # Extract perfil IDs from the stringified list
        cats_id_list = re.findall(pattern_perfil, cubo_form["categoria"])
        cats_ids = ",".join(cats_id_list) if cats_id_list else ""  # Handle empty case explicitly
        
        # Calculate perfil_nomes only if there are perfil IDs
        if cats_ids:
            cats_nomes = ",".join(
                [Categoria.query.get(int(cat_id)).nome 
                for cat_id in cats_ids.split(",") if cat_id and Categoria.query.get(int(cat_id))]
            )
        else:
            cats_nomes = ""  # Empty string if no Categoria

        # Create new CUBO object
        new_cubo = CUBO(
            categoria_ids=cats_ids,
            categoria_nomes=cats_nomes,
            perfil_ids=cubo_form["perfil"],
            perfil_nomes=cubo_form["perfil_nome"],
            pasta_drive=cubo_form["drive"]
        )
        
        # Add to session first to get an ID if needed
        db.session.add(new_cubo)
        db.session.flush()  # Flush to get the ID before commit

        # Commit all changes
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")
            raise

        # Save the log of the action
        LogController.create(
            session["nome"],
            session["perfil"],
            "DADOS",
            "CRIAR",
            f"PERFIL: {new_cubo.perfil_nomes} | CATEGORIA: {new_cubo.categoria_nome}"
        )
    
    @staticmethod
    def update(form):
        cubo = CuboController.get(form["_id"])

        # Store old data for logging
        old_data = {
            "categoria_ids": cubo.categoria_ids,
            "categoria_nomes": cubo.categoria_nomes,
            "prazo": cubo.prazo,
            "perfil_ids": cubo.perfil_ids,
            "perfil_nomes": cubo.perfil_nomes,
            "pasta_drive": cubo.pasta_drive
        }

        # Create a new CUBO entry
        pattern_perfil = r'"(\d+)"'
        
        # Extract perfil IDs from the stringified list
        pids_list = re.findall(pattern_perfil, form["perfis"])
        pids = ",".join(pids_list) if pids_list else ""  # Handle empty case explicitly
        
        # Calculate perfil_nomes only if there are perfil IDs
        if pids:
            pnomes = ",".join(
                [Perfil.query.get(int(pid)).nome 
                for pid in pids.split(",") if pid and Perfil.query.get(int(pid))]
            )
        else:
            pnomes = ""  # Empty string if no profiles

        # Update cubo with new data
        cubo.categoria_ids = form["categoria"]
        cubo.categoria_nomes = form["categoria_nome"]
        cubo.prazo = form["prazo"]
        cubo.perfil_ids = pids
        cubo.perfil_nomes = pnomes
        cubo.pasta_drive = form["drive"]

        db.session.commit()
        
        # Store new data for logging
        new_data = {
            "categoria_ids": cubo.categoria_ids,
            "categoria_nomes": cubo.categoria_nomes,
            "prazo": cubo.prazo,
            "perfil_ids": cubo.perfil_ids,
            "perfil_nomes": cubo.perfil_nomes,
            "pasta_drive": cubo.pasta_drive
        }

        # Save the log of the action
        LogController.create(
            session["nome"],
            session["perfil"],
            "DADOS",
            "ALTERAR",
            f"""
            OLD DATA: {old_data} | 
            NEW DATA: {new_data}
            """
        )
    
    @staticmethod
    def get(id):
        # Retrieve a CUBO by its ID
        cubo = CUBO.query.get(id)
        return cubo
    
    @staticmethod
    def get_all(filter):
        filtered_data = FilterController.filter(filter, CUBO)

        for cubo in filtered_data:
            cubo.tipo_processo_nome = Categoria.query.filter_by(categoria_id=cubo.categoria_id).first().tipo_de_processo_nome
            
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
