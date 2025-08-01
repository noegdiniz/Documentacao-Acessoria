from io import BytesIO
import json
from collections import defaultdict
import os
from uuid import uuid4

import requests
from app.controllers.FilterController import FilterController
from app.models.tables import Anexo, Aprovacao, Documento, Empresa, Perfil, User, CUBO
from app.controllers.LogController import LogController
from app.ext.db import db

from app.mail.mail import mail

from sqlalchemy import inspect
from datetime import datetime
import zlib
from flask import session, current_app
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
        return Documento.query.get(doc_id)

    @staticmethod
    def get_all_by_user(user_id):
        user = User.query.get(user_id)
        if user:
            return Documento.query.filter_by(perfil=user.perfil).all()
        return []
    
    @staticmethod
    def get_history_docs(titulo):
        filtered_emps = defaultdict(list)
        docs = Documento.query.filter_by(titulo=titulo).order_by(Documento.versao.asc()).all()
        
        cubos_map = {cubo.categoria_ids: cubo for cubo in CUBO.query.all()}

        for doc in docs:
            doc.anexos = Anexo.query.filter_by(documento_id=doc._id).all()
            cubo = cubos_map.get(doc.categoria_id)
            if cubo:
                doc.pasta = cubo.pasta_drive
                doc.perfil_nome = cubo.perfil_nome
            doc.aprovacoes = Aprovacao.query.filter_by(documento_id=doc._id).all()
            filtered_emps[doc.empresa_nome].append(doc)
        return filtered_emps
    
    @staticmethod
    def is_all_uploaded():
        return Documento.query.filter_by(uploaded=False).count() == 0
    
    @staticmethod
    def get_all(emp=None):
        filtered_emps = defaultdict(list)
        subquery = (
            db.session.query(
            Documento.titulo,
            db.func.max(Documento.versao).label("max_versao")
            )
            .group_by(Documento.titulo)
            .subquery()
        )

        docs = (
            db.session.query(Documento)
            .join(
            subquery,
            (Documento.titulo == subquery.c.titulo) &
            (Documento.versao == subquery.c.max_versao)
            )
            .all()
        )
        
        try:
            user_perfil_id = User.query.get(session["id"]).perfil_id
            cubos_for_user = CUBO.query.filter_by(perfil_id=user_perfil_id).all()
            allowed_categories = ''.join([c.categoria_ids for c in cubos_for_user])
        except Exception:
            allowed_categories = ''

        cubos_map = {cubo.categoria_ids: cubo for cubo in CUBO.query.all()}
        
        for doc in docs:
            
            if (str(doc.categoria_id) in allowed_categories) or (not allowed_categories):
                
                if emp == doc.empresa_id or emp is None:
                    
                    doc.anexos = Anexo.query.filter_by(documento_id=doc._id).all()
                    cubo = cubos_map.get(doc.categoria_id)
                    if cubo:
                        doc.pasta = cubo.pasta_drive
                        doc.perfil_nome = cubo.perfil_nome
                    
                    doc.aprovacoes = Aprovacao.query.filter_by(documento_id=doc._id).all()
                    filtered_emps[doc.empresa_nome].append(doc)
        
        return filtered_emps
        
    @staticmethod
    def create(form, files):
        if not files:
            return
        
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        titulo = form["titulo"]
        titulo_final = f"{titulo} - {uuid4().hex[:8].upper()}"
        
        empresa = Empresa.query.filter_by(_id=form["empresa"]).first() 
        
        if not empresa:
            raise ValueError("Empresa não encontrada.")

        doc = Documento(titulo=titulo_final,
                        contrato_id=form["contrato"],
                        empresa_id=form["empresa"],
                        contrato_nome=form["contrato_nome"],
                        categoria_nome=form["categoria_nome"],
                        empresa_nome=empresa.nome,
                        categoria_id=form["categoria"].split("|")[0],
                        data=data,
                        email=form["email"],
                        competencia=form["competencia"],
                        )
        
        db.session.add(doc)
        db.session.flush() # Use flush to get doc._id before commit
        
        cubos = CUBO.query.filter(CUBO.categoria_ids.contains(doc.categoria_id)).all()
        emails = set() # Use a set to avoid duplicate emails

        for cubo in cubos:
            users = User.query.filter_by(perfil_id=cubo.perfil_id).all()
            emails.update([user.email for user in users])

            new_aprovacao = Aprovacao(
                perfil_id=cubo.perfil_id,
                perfil_nome=Perfil.query.get(cubo.perfil_id).nome,
                documento_id=doc._id,
                data=datetime.now().strftime("%d/%m/%Y %H:%M"),
                status="AGUARDANDO"
            )
            
            db.session.add(new_aprovacao)

        if emails:
            subject = f"NOVA DOCUMENTAÇÃO ACESSORIA N°{doc._id} - {doc.empresa_nome}"
            body = f"""
            Um novo documento foi adicionado: {doc.titulo}.\n\n
            Contrato: {doc.contrato_nome}\n
            Categoria: {doc.categoria_nome}\n
            Empresa: {doc.empresa_nome}\n
            Data: {doc.data}\n
            """
            try:
                msg = Message(subject=subject,
                            recipients=list(emails),
                            body=body)
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Erro ao enviar e-mail: {e}")

        for file in files:
            if file and file.filename:
                file.seek(0)
                size_bytes = len(file.read())
                file.seek(0)
                size_mb = size_bytes / (1024 * 1024)
                
                anexo = Anexo(
                    filename=file.filename,
                    data=compress_file(file),
                    documento_id=doc._id,
                    corrigido=False,
                    tamanho=f"{size_mb:.3f} MB"
                )
                db.session.add(anexo)
        
        db.session.commit()
        LogController.create(doc.empresa_nome,
                            session.get("perfil", "N/A"),
                            "DOCUMENTOS",
                            "CRIAR",
                            f"NOME: {doc.titulo} EMAIL: {doc.email}")
    
    @staticmethod
    def delete(doc_id):
        documento = DocsController.get(doc_id)
        if not documento:
            raise ValueError("Documento não encontrado.")

        Aprovacao.query.filter_by(documento_id=documento._id).delete()
        Anexo.query.filter_by(documento_id=documento._id).delete()
        db.session.delete(documento)
        db.session.commit()
        
        LogController.create(session.get("nome", "N/A"),
                             session.get("perfil", "N/A"),
                             "DOCUMENTOS",
                             "DELETAR",
                             f"NOME: {documento.titulo}")
    
    @staticmethod
    def update_status(aprovacao_id, obs, status):
        aprovacao = Aprovacao.query.get(aprovacao_id)
        if not aprovacao:
            raise ValueError("Aprovação não encontrada.")

        aprovacao.status = status
        aprovacao.obs = obs
        db.session.commit()
        
        doc = Documento.query.get(aprovacao.documento_id)
        if not doc:
            raise ValueError("Documento associado não encontrado.")

        all_aprovacoes_for_doc = Aprovacao.query.filter_by(documento_id=doc._id).all()
        
        if status == "NAO APROVADO":
            doc.status = "NAO APROVADO"
            for ap in all_aprovacoes_for_doc:
                if ap._id != aprovacao_id:
                    ap.status = "INATIVO"
        elif all(ap.status == "APROVADO" for ap in all_aprovacoes_for_doc):
            doc.status = "APROVADO"
        else:
            doc.status = "AGUARDANDO"

        db.session.commit()
        
        LogController.create(session.get("nome", "N/A"),
                             session.get("perfil", "N/A"),
                             "APROVAÇÃO",
                             "ALTERAR",
                             f"DOCUMENTO: {doc.titulo} - STATUS: {aprovacao.status}")
        return "ok" if doc.status != "APROVADO" and doc.status != "NAO APROVADO" else "ok|all"

    @staticmethod
    def corrige_documento(doc_id, files, form):
        doc = Documento.query.get(doc_id)
        if not doc:
            raise ValueError("Documento não encontrado.")

        if doc.status == "CORRIGIDO":
            raise ValueError("O documento já está corrigido.")
        
        new_doc = Documento(
            titulo=doc.titulo,
            contrato_id=doc.contrato_id,
            empresa_id=doc.empresa_id,
            contrato_nome=doc.contrato_nome,
            categoria_nome=doc.categoria_nome,
            empresa_nome=doc.empresa_nome,
            categoria_id=doc.categoria_id,
            email=doc.email,
            status="CORRIGIDO",
            data=datetime.now().strftime("%d/%m/%Y %H:%M"),
            versao = float(doc.versao) + 0.1
        )

        db.session.add(new_doc)
        db.session.flush()
        
        aprovacoes_originais = Aprovacao.query.filter_by(documento_id=doc._id).all()
        for aprovacao in aprovacoes_originais:
            new_aprovacao = Aprovacao(
                perfil_id=aprovacao.perfil_id,
                perfil_nome=aprovacao.perfil_nome,
                documento_id=new_doc._id,
                data=datetime.now().strftime("%d/%m/%Y %H:%M"),
                status="AGUARDANDO" if aprovacao.status == "NAO APROVADO" else aprovacao.status,
            )
            
            db.session.add(new_aprovacao)
        
        all_anexos = Anexo.query.filter_by(documento_id=doc._id).all()
        for anexo in all_anexos:
            anexo.documento_id = new_doc._id
            anexo.corrigido = False
        
        db.session.commit()
        
        anexo_ids_to_update = form.getlist("anexo_id")
        files_to_update = files.getlist("anexo")

        for anexo_id, file_obj in zip(anexo_ids_to_update, files_to_update):
            if file_obj and file_obj.filename:
                file_obj.seek(0)
                anexo = Anexo.query.get(anexo_id)
                
                if anexo:
                    anexo.filename = file_obj.filename
                    anexo.data = compress_file(file_obj)
                    anexo.documento_id = new_doc._id
                    anexo.corrigido = True
                    anexo.tamanho = f"{len(anexo.data) / (1024 * 1024):.3f} MB" # type: ignore 
                    
        db.session.commit()
    
    # Create folder structure in Google Drive
    @staticmethod
    def create_folder_if_not_exists(parent_id, folder_name, headers):
        query = f"'{parent_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        search_url = f'https://www.googleapis.com/drive/v3/files?q={query}'
        response = requests.get(search_url, headers=headers)
            
        if response.status_code == 200:
            files = response.json().get('files', [])
            if files:
                return files[0]['id']
            else:
                # Create folder if it doesn't exist
                metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }

                create_response = requests.post(
                    'https://www.googleapis.com/drive/v3/files',
                    headers=headers,
                    json=metadata
                )
                    
                if create_response.status_code == 200:
                    return create_response.json()['id']
                else:
                    raise Exception(f"Error creating folder {folder_name}: {create_response.status_code} - {create_response.text}")
        else:
            raise Exception(f"Error searching for folder {folder_name}: {response.status_code} - {response.text}")

    # Move a pasta da empresa para inativas se a empresa estiver inativa, estrutura de pastas:
    # Pasta drive -> ATIVAS -> Empresa -> Ano -> Contrato -> Mes -> Categoria
    @staticmethod
    def move_folder_to_inactive(empresa_nome, headers, pasta_drive):
        # Primeiro, procura a subpasta "ATIVAS" dentro de pasta_drive
        ativas_id = DocsController.create_folder_if_not_exists(pasta_drive, "ATIVAS", headers=headers)
        
        # Agora, procura a pasta da empresa *dentro* de ATIVAS
        query = f"'{ativas_id}' in parents and name = '{empresa_nome}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        search_url = f'https://www.googleapis.com/drive/v3/files?q={query}'
        response = requests.get(search_url, headers=headers)
        
        if response.status_code == 200:
            files = response.json().get('files', [])
            print(f"Found {len(files)} folders for empresa {empresa_nome} in ATIVAS.")
            print(files)
            
            if files:
                folder_id = files[0]['id']
                
                print(f"Found folder ID: {folder_id} for empresa {empresa_nome}")
                
                # Garante que a subpasta "INATIVAS" existe dentro de pasta_drive
                inativas_id = DocsController.create_folder_if_not_exists(pasta_drive, "INATIVAS", headers=headers)

                # Move a pasta da empresa para INATIVAS (tira de ATIVAS)
                move_url = f'https://www.googleapis.com/drive/v3/files/{folder_id}?addParents={inativas_id}&removeParents={ativas_id}&fields=id,parents'
                move_response = requests.patch(move_url, headers=headers)

                if move_response.status_code not in [200, 201]:
                    raise Exception(f"Erro ao mover pasta {folder_id} para INATIVAS: {move_response.status_code} - {move_response.text}")
            else:
                raise Exception(f"Pasta da empresa '{empresa_nome}' não encontrada dentro de 'ATIVAS'.")
        else:
            raise Exception(f"Erro ao buscar a pasta da empresa '{empresa_nome}': {response.status_code} - {response.text}")

    @staticmethod
    def update_inative_folders(pasta_drive, inativa_folder_name):
        if 'google_tokens' not in session:
            return "User not authenticated with Google Drive", 401
        access_token = session['google_tokens']['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        DocsController.move_folder_to_inactive(inativa_folder_name, headers, pasta_drive)
            
    @staticmethod
    def upload_drive():
        if 'google_tokens' not in session:
            return "User not authenticated with Google Drive", 401
        
        access_token = session['google_tokens']['access_token']
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        docs = Documento.query.filter_by(uploaded=False).filter_by(status="APROVADO").all()
        
        print(f"Found {len(docs)} documents to upload to Google Drive...")
        
        meses = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro"
        }
        
        for doc in docs:
            # Get the drive folder ID
            
            print(User.query.filter_by(_id=session["id"]).first().perfil_id)

            cubo = CUBO.query.filter(
                CUBO.categoria_ids.contains(doc.categoria_id),
                CUBO.perfil_id == User.query.filter_by(_id=session["id"]).first().perfil_id
            ).first()
            
            if not cubo:
                raise Exception(f"No CUBO found for categoria_id {doc.categoria_id} and contrato_id {doc.contrato_id}")

            pasta_drive = cubo.pasta_drive
            
            #Cria pastas: ATIVAS
            pasta_drive_ativas = DocsController.create_folder_if_not_exists(pasta_drive, "ATIVAS", headers=headers)
            empresa_folder_id = DocsController.create_folder_if_not_exists(pasta_drive_ativas, doc.empresa_nome, headers=headers)
            
            # Cria uma pasta para o ano altual e proximo ano
            if doc.competencia:
                ano_folder_id = DocsController.create_folder_if_not_exists(empresa_folder_id, doc.competencia.split("-")[1], headers=headers)

                contrato_folder_id = DocsController.create_folder_if_not_exists(ano_folder_id, doc.contrato_nome, headers=headers)
                
                #cria uma pasta para cada mes do ano
                mes_folder_id = DocsController.create_folder_if_not_exists(contrato_folder_id, meses[doc.competencia.split("-")[0]], headers=headers)
                
                #Pega a lista de documentos da categoria
                categoria_folder_id = DocsController.create_folder_if_not_exists(mes_folder_id, doc.categoria_nome, headers=headers)

            print(f"Uploading document {doc.titulo} to Google Drive...")

            files = Anexo.query.filter_by(documento_id=doc._id).all()

            print(f"Found {len(files)} files to upload for document {doc.titulo}...")
            
            for file in files:
                
                try:
                    print(f"Uploading file {file.filename} to Google Drive...")
                    print(f"File name: {file.filename}")
                    print(f"File size: {len(file.data)} bytes")
                    
                    # Check if the file is already existing in the folder, if so, delete it
                    query = f"'{categoria_folder_id}' in parents and name = '{file.filename}' and trashed = false"
                    search_url = f'https://www.googleapis.com/drive/v3/files?q={query}'
                    response = requests.get(search_url, headers=headers)

                    if response.status_code == 200:
                        files = response.json().get('files', [])
                        
                        if files:
                            # Delete the existing file before uploading the new one
                            for existing_file in files:
                                print(f"Deleting existing file {existing_file['name']}...")
                                
                                delete_url = f'https://www.googleapis.com/drive/v3/files/{existing_file["id"]}'
                                delete_response = requests.delete(delete_url, headers=headers)
                                if delete_response.status_code != 204:
                                    raise Exception(f"Error deleting existing file {file.filename}: {delete_response.status_code} - {delete_response.text}")
                        else:
                            print(f"No existing file found for {file.filename}, proceeding with upload.")
                    else:
                        raise Exception(f"Error searching for existing file {file.filename}: {response.status_code} - {response.text}")

                    # Prepare file metadata
                    metadata = {
                        'name': file.filename,
                        'parents': [categoria_folder_id],
                        'mimeType': 'application/octet-stream'
                    }

                    # Convert BLOB to BytesIO for upload
                    decompressed_data = zlib.decompress(file.data)

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

                        # Gera o link do arquivo e salva no anexo
                        file_id = response.json()['id']
                        file.link = f"https://drive.google.com/file/d/{file_id}/view?usp=drive_link"
                        
                        db.session.commit()
                    else:
                        raise Exception(f"Error uploading file {file.filename}: {response.status_code} - {response.text}")

                except Exception as e:
                    raise Exception(f"Failed to upload {file.filename}: {str(e)}")
        
        db.session.commit()
        return "ok", 200
    
    @staticmethod
    def filter(emp, content):
        filtered_emps = defaultdict(list)
        docs = FilterController.filter(content, Documento)
        
        try:
            user_perfil_id = User.query.get(session["id"]).perfil_id
            cubos_for_user = CUBO.query.filter_by(perfil_id=user_perfil_id).all()
            allowed_categories = {c.categoria_ids for c in cubos_for_user}
        except Exception:
            allowed_categories = set()
        
        cubos_map = {cubo.categoria_ids: cubo for cubo in CUBO.query.all()}
        
        for doc in docs:
            if (doc.categoria_id in allowed_categories) or (not allowed_categories):
                if emp == doc.empresa_id or emp is None:
                    doc.anexos = Anexo.query.filter_by(documento_id=doc._id).all()
                    cubo = cubos_map.get(doc.categoria_id)
                    
                    if cubo:
                        doc.pasta = cubo.pasta_drive
                        doc.perfil_nome = cubo.perfil_nome
                    doc.aprovacoes = Aprovacao.query.filter_by(documento_id=doc._id).all()
                    filtered_emps[doc.empresa_nome].append(doc)
        
        return filtered_emps
