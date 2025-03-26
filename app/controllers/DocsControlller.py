from app.models.tables import Documento, User
from app.controllers.EmpresaController import EmpresaController
from app.controllers.LogController import LogController
from app.models.tables import User
from app.models.tables import CUBO

from app.ext.db import db

from sqlalchemy import inspect
from datetime import datetime
import zlib
from flask import session

def check_prazo(doc):
    #Check if the diference of doc.data and today is equal or less cubo.prazo in days
    cubo = CUBO.query.filter_by(categoria_id=doc.categoria_id).filter_by(contrato_id=doc.contrato_id).first()            
    diff = (datetime.now() - datetime.strptime(doc.data, "%d/%m/%Y %H:%M")).days

    print(diff)
    print(cubo.prazo)

    if diff <= int(cubo.prazo):
        doc.expirado = False
    else:
        doc.expirado = True

def compress_file(file):
    if file:
        # Read file content
        file_content = file.read()
        
        # Compress the file using zlib
        compressed_data = zlib.compress(file_content, level=9)
        return compressed_data


class DocsController:
    @staticmethod
    def get(doc_id):
        doc = Documento.query.filter_by(_id=doc_id).first()
        return doc

    @staticmethod
    def get_all_by_user(user_id):
        perfil = User.query.filter_by(_id=user_id).first().perfil

        docs = Documento.query.filter_by(perfil=perfil).all()

        return docs
    

    @staticmethod
    def filter(emp, content):
        from collections import defaultdict

        # Initialize a dictionary to hold lists of documents for each company
        filtered_emps = defaultdict(list)

        try:
            perfil = User.query.get(session["id"])
            cubos = CUBO.query.filter_by(perfil_id=perfil.perfil_id).all()
            categorias = [cubo.categoria_id for cubo in cubos]

            # Retrieve all documents
            if emp:
                docs = Documento.query.filter_by(empresa_id=emp).filter(Documento.categoria_id.in_(categorias)).all()
            else:
                docs = Documento.query.filter(Documento.categoria_id.in_(categorias)).all()
        except:
            docs = Documento.query.filter_by(empresa_id=emp).all()
            
        # Get the list of column names dynamically
        mapper = inspect(Documento)
        columns = [column.key for column in mapper.attrs]
        columns.remove("anexo")
        
        if content:
            for doc in docs:

                check_prazo(doc)
                
                # Check if the content is in the column value
                for column in columns:

                    if content in str(getattr(doc, column)):
                        # Append the document to the list corresponding to its company
                        filtered_emps[doc.empresa_nome].append(doc)
                        #sai do loop depois que o primeiro 
                        break
        else:
            for doc in docs:
                # Append the document to the list corresponding to its company

                check_prazo(doc)
                filtered_emps[doc.empresa_nome].append(doc)

        db.session.commit()
        return filtered_emps
    
    @staticmethod
    def create(form, files):
        data = datetime.strptime(form["data"], "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M")
        
        doc = Documento(titulo=form["titulo"],
                        contrato_id=form["contrato"],
                        empresa_id = form["empresa"],
                        contrato_nome = form["contrato_nome"],
                        categoria_nome = form["categoria_nome"],

                        ## Nome da empresa
                        empresa_nome = EmpresaController.get(_id=form["empresa"]).nome,
                        categoria_id=form["categoria"],
                        data=data,
                        anexo=compress_file(files["anexo"]))
        
        db.session.add(doc)
        db.session.commit()

        #Salva o Log da ação
        LogController.create(doc.empresa_nome,
                             "",
                             "DOCUMENTOS",
                             "CRIAR",
                             f"NOME: {doc.titulo}")
    
    @staticmethod
    def delete(id):
        documento = DocsController.get(id)

        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "DOCUMENTOS",
                             "DELETAR",
                             f"NOME: {documento.titulo}")
        
        db.session.delete(documento)
        db.session.commit()
    
    @staticmethod
    def update_status(_id, obs, status):
        doc = Documento.query.filter_by(_id=_id).first()

        old_doc = doc
        doc.obs = obs
        doc.status = status
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "DOCUMENTOS",
                             "ALTERAR",
                             f"NOME: {old_doc.nome} -> {doc.nome}")
        