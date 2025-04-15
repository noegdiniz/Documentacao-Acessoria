from app.controllers.FilterController import FilterController
from app.models.tables import Categoria
from app.ext.db import db
from app.controllers.LogController import LogController
from flask import session

class CategoriaController:
    @staticmethod
    def create(categoria_form):
        new_categoria = Categoria(nome=categoria_form["nome"],
                                tipo_de_processo_id=categoria_form["tipo_processo"],
                                tipo_de_processo_nome=categoria_form["tipo_processo_nome"],
                                documentos_pedidos=categoria_form["docs_precisos"])
        
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
        categoria.tipo_de_processo_id = form["tipo_processo"]
        categoria.tipo_de_processo_nome = form["tipo_processo_nome"]
        categoria.documentos_pedidos = form["docs_precisos"]
        
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
        filtered_data = FilterController.filter(filter, Categoria)
        return filtered_data
    
    @staticmethod
    def delete(id):
        categoria = CategoriaController.get(id)
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
