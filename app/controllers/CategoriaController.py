from app.models.tables import Categoria
from app.ext.db import db
from app.controllers.LogController import LogController
from flask import session

class CategoriaController:
    @staticmethod
    def create(categoria_form):
        new_categoria = Categoria(nome=categoria_form["nome"])
        db.session.add(new_categoria)
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "CATEGORIAS",
                             "CRIAR",
                             f"NOME: {new_categoria.nome}")
    
    @staticmethod
    def update(form):
        categoria = CategoriaController.get(form["_id"])
        
        old_categoria = categoria

        categoria.nome = form["nome"]
        db.session.commit()

        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "CATEGORIAS",
                             "ALTERAR",
                             f"NOME: {old_categoria.nome} -> {categoria.nome}")

    
    @staticmethod
    def get(id):
        categoria = Categoria.query.get(id)
        return categoria
    
    @staticmethod
    def get_all(filter):
        filtered_data = []
        
        categorias = Categoria.query.all()
        
        if filter:
            for item in categorias:
                if filter in str(item.nome):
                    filtered_data.append(item)
        else:
            return categorias

        return filtered_data
        
    @staticmethod
    def delete(id):
        categoria = Categoria.get(id)
        if categoria:
            #Salva o Log da ação
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "CATEGORIAS",
                                 "DELETAR",
                                 f"NOME: {categoria.nome}"
                                 )
            
            db.session.delete(categoria)
            db.session.commit()
            
            return True
        return False
