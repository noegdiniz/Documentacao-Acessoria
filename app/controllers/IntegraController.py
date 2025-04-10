from app.controllers.FilterController import FilterController
from app.models.tables import Integracao, Funcionario
from app.ext.db import db

class IntegraController:

    ## Static methods for IntegraController

    ## Create, Update, Delete, Get methods for Integra
    @staticmethod
    def create_integra(form):
        try:
            new_integra = Integracao(
                nome=form['nome'],
                empresa_id=form['empresa_id'],
                unidade_atividade=form['unidade_atividade'],
                unidade_integracao = form['unidade_integracao']
            )

            db.session.add(new_integra)
            db.session.commit()
            return "ok"
        except Exception as e:
            raise Exception(f"Erro ao criar integração: {e}")
    
    @staticmethod
    def update_integra(form):
        integra = db.session.query(Integracao).get(form['id'])

        for key, value in form.items():
            setattr(integra, key, value)
        db.session.commit()

    @staticmethod
    def delete_integra(form):
        integra = db.session.query(Integracao).get(form['id'])
        db.session.delete(integra)
        db.session.commit()

    @staticmethod
    def get_integra(form):
        integra = db.session.query(Integracao).get(form['id'])
        return integra

    @staticmethod
    def get_all_integra(content):
        integra_list = FilterController.filter(content, Integracao)
        return integra_list
    
    ## Create, Update, Delete, Get methods for Funcionario
    @staticmethod
    def create_funcionario(form):
        new_funcionario = Funcionario(**form)
        db.session.add(new_funcionario)
        db.session.commit()

    @staticmethod
    def update_funcionario(form):
        funcionario = db.session.query(Funcionario).get(form['id'])
        for key, value in form.items():
            setattr(funcionario, key, value)
        db.session.commit()

    
    @staticmethod
    def delete_funcionario(form):
        funcionario = db.session.query(Funcionario).get(form['id'])
        db.session.delete(funcionario)
        db.session.commit()

    @staticmethod
    def get_funcionario(form):
        funcionario = db.session.query(Funcionario).get(form['id'])
        return funcionario
    
    @staticmethod
    def get_all_funcionario(content):
        funcionario_list = FilterController.filter(content, Funcionario)
        return funcionario_list
    
        