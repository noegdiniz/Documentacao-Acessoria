import datetime
from flask import session
from app.controllers.FilterController import FilterController
from app.controllers.LogController import LogController
from app.models.tables import Funcionario, StatusFuncionario, Subcont, Empresa
from app.ext.db import db

class IntegraController:

    ## Static methods for IntegraController

    @staticmethod
    def create_subcontratado(form):
        try:
            new_subcontratado = Subcont(
                nome=form['nome'],
                cnpj=form['cnpj'],
                empresa_id=Empresa.query.filter_by(chave=form['chave_empresa']).first()._id,
                contrato_id=form['contrato_id'],
            )

            db.session.add(new_subcontratado)
            db.session.commit()
            return "ok"
        except Exception as e:
            raise Exception(f"Erro ao criar subcontratado: {e}")

    @staticmethod
    def update_subcontratado(form):
        subcontratado = db.session.query(Subcont).get(form['id'])

        for key, value in form.items():
            setattr(subcontratado, key, value)
        db.session.commit()

    @staticmethod
    def delete_subcontratado(id):
        subcontratado = Subcont.query.get(id)
        if subcontratado:
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "SUBCONTRATADOS",
                                 "EXCLUIR",
                                 f"NOME: {subcontratado.nome}")
            
            db.session.delete(subcontratado)
            db.session.commit()
            return True 
        return False
            
    @staticmethod
    def get_subcontratado(id):
        subcontratado = Subcont.query.get(id)
        return subcontratado
    
    @staticmethod
    def get_all_subcontratados(filter):
        subcontratado_list = FilterController.filter(filter, Subcont)
        return subcontratado_list
    
    ## Create, Update, Delete, Get methods for Funcionario
    @staticmethod
    def create_funcionario(form):
        print(form)

        new_funcionario = Funcionario(
            nome=form['nome']
        )

        db.session.add(new_funcionario)
        db.session.flush()

        empresa = Empresa.query.filter_by(_id=form['empresa_id']).first()


        status_funcionario = StatusFuncionario(
            status_contratual="ativo",
            status_integracao="pendente",

            unidade_atividade="",
            unidade_integracao="",

            data_integracao="",
            data_aso="",

            contrato_id="",
            contrato_nome="",

            funcionario_id = new_funcionario._id,
            funcionario_nome = new_funcionario.nome,
            funcao=form['funcao'],
            cargo=form['cargo'],
            setor=form['setor'],
            empresa_id=form['empresa_id'],
            empresa_nome=empresa.nome,
            tipo=form['tipo'],

            data=datetime.datetime.now().strftime("%d/%m/%Y"),
        )
        
        db.session.add(status_funcionario)
        db.session.commit()
    
    @staticmethod
    def update_funcionario(form):

        funcionario = db.session.query(Funcionario).get(form['_id'])
        status_funcionario = db.session.query(StatusFuncionario).filter_by(funcionario_id=form['_id']).order_by(StatusFuncionario.versao.desc()).first()
        
        new_status_funcionario = StatusFuncionario(
            status_contratual=form["status"],
            status_integracao=form["status_integracao"],
            funcionario_id = funcionario._id,
            funcionario_nome = funcionario.nome,
            
            unidade_atividade=form['unidade_atividade'],
            unidade_integracao=form['unidade_integracao'],
            data_integracao=form['data_integracao'],
            data_aso=form['data_aso'],
            contrato_id=form['contrato_id'],
            contrato_nome=form['contrato_nome'],

            funcao=form['funcao'],
            cargo=form['cargo'],
            setor=form['setor'],
            empresa_id=form['empresa_id'],
            empresa_nome=form['empresa_nome'],
            tipo=form['tipo'],
            data=datetime.datetime.now().strftime("%d/%m/%Y"),
            versao=float(status_funcionario.versao) + 0.1
        )
        
        if form['nome']:
            status_funcionario.funcionario_nome = form['nome']

        db.session.add(new_status_funcionario)
        db.session.commit()
    
    @staticmethod
    def delete_funcionario(id):
        funcionario = db.session.query(Funcionario).get(id)
        db.session.delete(funcionario)
        db.session.commit()
    
    @staticmethod
    def get_funcionario(id):
        funcionario = db.session.query(Funcionario).get(id)
        funcionario.status_funcionario = StatusFuncionario.query.filter_by(funcionario_id=funcionario._id).all()
        return funcionario
    
    @staticmethod
    def get_all_funcionario(content):
        funcionario_status = FilterController.filter(content, StatusFuncionario)
        funcionario_list = []
        
        for status in funcionario_status:
            funcionario_list.append(Funcionario.query.filter_by(_id=status.funcionario_id).first())
        
        for funcionario in funcionario_list:
            funcionario.status_funcionario = StatusFuncionario.query.filter_by(funcionario_id=funcionario._id).all()

        return funcionario_list
    