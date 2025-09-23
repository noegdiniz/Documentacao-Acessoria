from app.controllers.DocsControlller import DocsController
from app.models.tables import CUBO, Empresa
from app.ext.db import db
from app.controllers.LogController import LogController

from flask import session

class EmpresaController():
    @staticmethod
    def create(nome, chave, cnpj, dep, status):
        nome = nome.strip().upper()
        empresa = Empresa(nome=nome, chave=chave, cnpj=cnpj, departamento=dep, status=status)
        db.session.add(empresa)
        db.session.commit()
        # Salva o Log da ação
        LogController.create(session.get("nome", "N/A"),
                             session.get("perfil", "N/A"),
                             "EMPRESA",
                             "CRIAR",
                             f"NOME: {empresa.nome} | CHAVE: {empresa.chave} | CNPJ: {empresa.cnpj}")
    
    @staticmethod
    def update(nome, chave, cnpj, dep, status, _id):
        empresa = EmpresaController.get(_id=_id)
        if not empresa:
            raise ValueError("Empresa não encontrada.")
        old_empresa_nome = empresa.nome
        old_empresa_chave = empresa.chave
        old_empresa_status = empresa.status

        empresa.nome = nome
        empresa.chave = chave
        empresa.cnpj = cnpj
        empresa.departamento = dep
        empresa.status = status

        db.session.commit()

        if empresa.status == "INATIVA":
            for cubo in CUBO.query.all():
                try:
                    print(f"Updating CUBO {cubo.perfil_nome} with new status INATIVA")
                    DocsController.update_inative_folders(cubo.pasta_drive, empresa.nome)
                except Exception as e:
                    print(f"{e}")
            return "ok"

        # Salva o Log da ação
        LogController.create(session.get("nome", "N/A"),
                             session.get("perfil", "N/A"),
                             "EMPRESA",
                             "ALTERAR",
                             f"NOME: {old_empresa_nome} | CHAVE: {old_empresa_chave} -> NOME: {empresa.nome} | CHAVE: {empresa.chave} | CNPJ: {empresa.cnpj} | STATUS: {old_empresa_status} -> {empresa.status}")
    
    @staticmethod
    def get(chave=None, _id=None):
        if chave is not None:
            return Empresa.query.filter_by(chave=chave).first()
        if _id is not None:
            return Empresa.query.filter_by(_id=_id).first()
        return None
    
    @staticmethod
    def get_all():
        return Empresa.query.all()
    
    @staticmethod
    def auth(nome, chave):
        empresa = Empresa.query.filter_by(chave=chave, nome=nome).first()
        if empresa:
            # Salva o Log da ação
            LogController.create(nome,
                                 "",
                                 "PRESTADORAS",
                                 "LOGIN PRESTADORA",
                                 "")
            return empresa
        return False
    
    @staticmethod
    def delete(_id):
        empresa = EmpresaController.get(_id=_id)
        if not empresa:
            raise ValueError("Empresa não encontrada.")
        # Salva o Log da ação
        LogController.create(session.get("nome", "N/A"),
                             session.get("perfil", "N/A"),
                             "EMPRESA",
                             "DELETAR",
                             f"NOME: {empresa.nome}")
        db.session.delete(empresa)
        db.session.commit()
    