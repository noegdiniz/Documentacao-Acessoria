from io import BytesIO
import json
from collections import defaultdict

import requests
from app.models.tables import Anexo, Aprovacao, Documento, Perfil, User
from app.controllers.EmpresaController import EmpresaController
from app.controllers.LogController import LogController
from app.models.tables import User
from app.models.tables import CUBO
from app.models.tables import Aprovacao
from app.ext.db import db
from app.mail.mail import mail

from sqlalchemy import inspect
from datetime import datetime
import zlib
from flask import session
from flask_mail import Message

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
    def get_history_docs(titulo):
        filtered_emps = defaultdict(list)

        docs = Documento.query.filter_by(titulo=titulo).order_by(Documento.data.desc()).all()
        
        for doc in docs:
            # Load anexos to the document
            doc.anexos = Anexo.query.filter_by(documento_id=doc._id).all()

            # Load pasta_drive to the document
            doc.pasta_drive = CUBO.query.filter_by(categoria_id=doc.categoria_id).filter_by(contrato_id=doc.contrato_id).first().pasta_drive

            cubo = CUBO.query.filter_by(categoria_id=doc.categoria_id).filter_by(contrato_id=doc.contrato_id).first()

            doc.pasta = cubo.pasta_drive
            doc.perfil_nomes = cubo.perfil_nomes
            doc.aprovacoes = Aprovacao.query.filter_by(documento_id=doc._id).all()

            filtered_emps[doc.empresa_nome].append(doc).all()
        
        return filtered_emps

    @staticmethod
    def is_all_uploaded():
        # Check if all documents are uploaded
        # Uploaded == False : Upload pendente, se os pendentes forem 0, retorna True,
        # ou seja, todos os documentos foram enviados
        docs = Documento.query.filter_by(uploaded=False).all()
        return len(docs) == 0
    
    @staticmethod
    def filter(emp, content):

        # Initialize a dictionary to hold lists of documents for each company
        filtered_emps = defaultdict(list)

        try:
            perfil_id = User.query.get(session["id"]).perfil_id

            # Retrieve all cubos associated with the user's profile
            cubos = CUBO.query.filter(CUBO.perfil_ids.contains(perfil_id)).all()
            categorias = [cubo.categoria_id for cubo in cubos]
            
            # Retrieve all documents
            if emp:
                docs = Documento.query.filter_by(empresa_id=emp).filter(Documento.categoria_id.in_(categorias)).order_by(Documento.data.desc(), Documento.titulo).all()
            else:
                docs = Documento.query.filter(Documento.categoria_id.in_(categorias)).order_by(Documento.data.desc(), Documento.titulo).all()
        except:
            docs = Documento.query.filter_by(empresa_id=emp).order_by(Documento.data.desc(), Documento.titulo).all()
            
        # Get the list of column names dynamically
        mapper = inspect(Documento)
        columns = [column.key for column in mapper.attrs]
        
        if content:
            for doc in docs:

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
                filtered_emps[doc.empresa_nome].append(doc)

        for doc in docs:
            # Load anexos to the document
            doc.anexos = Anexo.query.filter_by(documento_id=doc._id).all()

            # Load pasta_drive to the document
            doc.pasta_drive = CUBO.query.filter_by(categoria_id=doc.categoria_id).filter_by(contrato_id=doc.contrato_id).first().pasta_drive

            cubo = CUBO.query.filter_by(categoria_id=doc.categoria_id).filter_by(contrato_id=doc.contrato_id).first()

            doc.pasta = cubo.pasta_drive
            doc.perfil_nomes = cubo.perfil_nomes
            doc.aprovacoes = Aprovacao.query.filter_by(documento_id=doc._id).all()

        return filtered_emps
        
    @staticmethod
    def create(form, files):
        # Check if no files are uploaded
        if not files.getlist("anexo"):
            return
        
        data = datetime.strptime(form["data"], "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M")
        
        doc = Documento(titulo=form["titulo"],
                        contrato_id=form["contrato"],
                        empresa_id=form["empresa"],
                        contrato_nome=form["contrato_nome"],
                        categoria_nome=form["categoria_nome"],

                        ## Nome da empresa
                        empresa_nome=EmpresaController.get(_id=form["empresa"]).nome,
                        categoria_id=form["categoria"],
                        data=data)
        
        db.session.add(doc)
        db.session.commit()
        
        cubo = CUBO.query.filter_by(categoria_id=form["categoria"]).filter_by(contrato_id=form["contrato"]).first()
        users = User.query.filter(User.perfil_id.in_(cubo.perfil_ids.split(","))).all()
        emails = [user.email for user in users]
        
        # Create Aprovacao for documento based on perfil_id
        for perfi_id in cubo.perfil_ids.split(","):
            new_aprovacao = Aprovacao(
                perfil_id=perfi_id,
                perfil_nome=Perfil.query.get(int(perfi_id)).nome,
                documento_id=doc._id,  # Assumes _id is available after add
                data=datetime.now().strftime("%d/%m/%Y %H:%M"),
                status="AGUARDANDO"
            )

            db.session.add(new_aprovacao)
            db.session.commit()

        # Send email to all users in the profile
        if emails:
            subject = f"NOVA DOCUMENTAÇÃO ACESSORIA N°{doc._id} - {doc.empresa_nome}"
            body = f"""
            Um novo documento foi adicionado: {doc.titulo}.\n\n
            Contrato: {doc.contrato_nome}\n
            Categoria: {doc.categoria_nome}\n
            Data: {doc.data}\n
            Prazo: {cubo.prazo} dias\n
            """

            # Create a Message object
            msg = Message(subject=subject,
                        recipients=emails,
                        body=body)
                        
            # Crete an Anexo object for each file
            for file in files.getlist("anexo"):
                file.seek(0)  # Reset file pointer to the beginning

                anexo = Anexo(
                    filename=file.filename,
                    data=compress_file(file),
                    documento_id=doc._id
                )

                db.session.add(anexo)
                db.session.commit()
                
            mail.send(msg)
            
            # Save the log of the action
            LogController.create(doc.empresa_nome,
                                session["perfil"],
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
        aprove = Aprovacao.query.filter_by(_id=_id).first()

        aprove.obs = obs
        aprove.status = status
        db.session.commit()
        
        # Se o status status de alguma aprovação for "NAO APROVADO"
        # o status do documento também deve ser "NAO APROVADO"
        if status == "NAO APROVADO":
            doc = Documento.query.filter_by(_id=aprove.documento_id).first()
            doc.status = "NAO APROVADO"
            db.session.commit()
        
        # Se todas as aprovações para o documento forem "APROVADO"
        # o status do documento deve ser "APROVADO"
        doc = Documento.query.filter_by(_id=aprove.documento_id).first()
        aproves = Aprovacao.query.filter_by(documento_id=aprove.documento_id).all()
        if all(approve.status == "APROVADO" for approve in aproves):
            doc.status = "APROVADO"
        
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                            "APROVAÇÃO",
                             "ALTERAR",
                             f"DOCUMENTO: {aprove.documento_id} - STATUS: {aprove.status}")
        
    @staticmethod
    def limpa_anexos():
        # Remove all attachments related to the document
        docs = Documento.query.filter_by(uploaded=True).all()
        for doc in docs:
            doc.uploaded = True
            anexos = Anexo.query.filter_by(documento_id=doc._id).all()
            for anexo in anexos:
                db.session.delete(anexo)
            db.session.commit()

    # Cria uma nova versão do documento como correção e atualiza somente os anexos e data
    @staticmethod
    def corrige_documento(doc_id, files):
        doc = Documento.query.filter_by(_id=doc_id).first()
        
        # Cria uma nova versão do documento
        new_doc = Documento(
            titulo=doc.titulo,
            contrato_id=doc.contrato_id,
            empresa_id=doc.empresa_id,
            contrato_nome=doc.contrato_nome,
            categoria_nome=doc.categoria_nome,
            empresa_nome=doc.empresa_nome,
            categoria_id=doc.categoria_id,
            tipo_processo=doc.tipo_processo,
            status="CORRIGIDO", ## Novo documento inicia com status CORRIGIDO para nova aprovação
            data=datetime.now().strftime("%d/%m/%Y %H:%M"),
            versao = float(doc.versao) + 0.1
        )

        db.session.add(new_doc)
        db.session.commit()

        # Cria as aprovações para a nova versão do documento
        aprovacoes = Aprovacao.query.filter_by(documento_id=new_doc._id).all()
        for aprovacao in aprovacoes:
            new_aprovacao = Aprovacao(
                perfil_id=aprovacao.perfil_id,
                perfil_nome=aprovacao.perfil_nome,
                documento_id=new_doc._id,
                data=datetime.now().strftime("%d/%m/%Y %H:%M"),
                status="AGUARDANDO" if aprovacao.status == "NAO APROVADO" else aprovacao.status,
            )
            
            db.session.add(new_aprovacao)
            db.session.commit()
        
        # Cria um novo anexo para cada arquivo enviado para nova versão
        for file in files.getlist("anexo"):
            file.seek(0)  # Reset file pointer to the beginning

            anexo = Anexo(
                filename=file.filename,
                data=compress_file(file),
                documento_id=new_doc._id
            )

            db.session.add(anexo)
            db.session.commit()

    @staticmethod
    def upload_drive():
        if 'google_tokens' not in session:
            return "User not authenticated with Google Drive", 401

        access_token = session['google_tokens']['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        docs = Documento.query.filter_by(uploaded=False).filter_by(status="APROVADO").filter_by(expirado=False).all()
        print(f"Found {len(docs)} documents to upload to Google Drive...")

        for doc in docs:
            # Get the drive folder ID
            pasta_drive = CUBO.query.filter_by(
                categoria_id=doc.categoria_id,
                contrato_id=doc.contrato_id
            ).first().pasta_drive
            
            print(f"Uploading document {doc.titulo} to Google Drive...")

            files = Anexo.query.filter_by(documento_id=doc._id).all()
            print(f"Found {len(files)} files to upload for document {doc.titulo}...")

            for file in files:
                try:
                    print(f"Uploading file {file.filename} to Google Drive...")
                    print(f"File name: {file.filename}")
                    print(f"File size: {len(file.data)} bytes")
                    
                    # Prepare file metadata
                    metadata = {
                        'name': file.filename,
                        'parents': [pasta_drive],
                        'mimeType': 'application/octet-stream'
                    }

                    # Convert BLOB to BytesIO for upload
                    decompressed_data = zlib.decompress(file.data)
                    file_content = BytesIO(decompressed_data)

                    # Prepare multipart request
                    boundary = '---011000010111000001101001'
                    body = []
                    
                    # Add metadata part
                    body.append(f'--{boundary}'.encode())
                    body.append('Content-Type: application/json; charset=UTF-8'.encode())
                    body.append(''.encode())
                    body.append(json.dumps(metadata).encode())
                    
                    # Add file content part
                    body.append(f'--{boundary}'.encode())
                    body.append(f'Content-Type: application/octet-stream'.encode())
                    body.append(''.encode())
                    body.append(decompressed_data)
                    body.append(f'--{boundary}--'.encode())
                    
                    # Join all parts
                    body = b'\r\n'.join(body)

                    # Set content type with boundary
                    headers['Content-Type'] = f'multipart/related; boundary={boundary}'

                    # Upload to Google Drive
                    upload_url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'
                    
                    response = requests.post(
                        upload_url,
                        headers=headers,
                        data=body
                    )

                    if response.status_code == 200:
                        LogController.create(
                            doc.empresa_nome,
                            session["perfil"],
                            "DOCUMENTOS",
                            "UPLOAD DRIVE",
                            f"FILE: {doc.titulo} - DOC ID: {doc._id}"
                        )

                        doc.uploaded = True
                    else:
                        raise Exception(f"Error uploading file {file.filename}: {response.status_code} - {response.text}")

                except Exception as e:
                    raise Exception(f"Failed to upload {file.filename}: {str(e)}")
                
        
        db.session.commit()
        return "ok", 200