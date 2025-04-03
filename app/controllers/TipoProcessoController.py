from app.models.tables import TipoProcesso
from app.models.tables import Categoria
from app.controllers.FilterController import FilterController
from app.ext.db import db

class TipoProcessoController():
    @staticmethod
    def create(form):
        tipo_processo = TipoProcesso(nome=form["nome"])
        db.session.add(tipo_processo)
        db.session.commit()

    @staticmethod
    def update(form):
        tipo_processo = TipoProcesso.query.get(form["_id"])
        tipo_processo.nome = form["nome"]
        db.session.commit()

    staticmethod
    def delete(id):
        tipo_processo = TipoProcesso.query.get(id)
        db.session.delete(tipo_processo)
        db.session.commit()

    @staticmethod
    def get(id):
        tipo_processo = TipoProcesso.query.get(id)
        return tipo_processo
        
    @staticmethod
    def get_all(content):

        
        filter_tipo_processos = FilterController.filter(content, TipoProcesso)
        for tipo_processo in filter_tipo_processos:
            tipo_processo.categorias = Categoria.query.filter_by(tipo_de_processo_id=tipo_processo._id).all()

        return filter_tipo_processos
    