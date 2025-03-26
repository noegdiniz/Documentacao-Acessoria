from app.ext.db import db
from sqlalchemy import event

###                     ###
## Declaração das models ##
###                     ###

class Documento(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)

    #PDF DO DOCUMENTO
    anexo = db.Column(db.LargeBinary, nullable=False)

    status =  db.Column(db.String, nullable=False, default="AGUARDANDO") #APROVADO / AGUARDANDO / NAO APROVADO

    obs = db.Column(db.String, nullable=False, default="") #Caso reprovado dizer o motivo

    #ID DO CONTRADO ATRELADO AO DOCUMENTO
    contrato_id = db.Column(db.Integer, nullable=False)
    
    empresa_id = db.Column(db.Integer, nullable=False)
    empresa_nome = db.Column(db.String, nullable=False)

    contrato_nome = db.Column(db.String, nullable=False)
    categoria_nome = db.Column(db.String, nullable=False)
    
    #ID DA CATEGORIA ATRELADA AO DOCUMENTO
    categoria_id =  db.Column(db.String, nullable=False)

    #CONTROLA SE O DOCUMENTO ESTA OU NAO EXPIRADO COM BASE NO PRAZO DO CUBO
    expirado = db.Column(db.Boolean, nullable=False, default=False)

class User(db.Model):
    #ID do usuario usa o mesmo da conta do gmail na hora do login
    _id = db.Column(db.String, primary_key=True)

    nome = db.Column(db.String, nullable=False)
    perfil = db.Column(db.String, nullable=False, default="") #rh,com,admin | padrao vazio definido pelo administrador
    perfil_id = db.Column(db.Integer)

    #Imagem da conta google do usuario
    file = db.Column(db.String, nullable=False)
    
    email = db.Column(db.String, nullable=False)

class Empresa(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    
    ##Chave unica de 6 digitos para identificação da empresa
    chave = db.Column(db.String, nullable=False)
    
class CUBO(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria_id = db.Column(db.Integer, nullable=False)
    categoria_nome = db.Column(db.String, nullable=False)
    contrato_id = db.Column(db.Integer, nullable=False)
    contrato_nome = db.Column(db.String, nullable=False)
    
    prazo = db.Column(db.String, nullable=False)
    perfil_id = db.Column(db.String, nullable=False)
    perfil_nome = db.Column(db.String, nullable=False)
    
    pasta_drive = db.Column(db.String, nullable=False)

class Contrato(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    empresa_id = db.Column(db.Integer, nullable=False)
    empresa_nome = db.Column(db.String, nullable=False)

class Categoria(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)

class Perfil(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    
    # Permissoes de DADOS
    can_create_dados = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_dados = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_dados = db.Column(db.Boolean, nullable=False, default=False)
    can_view_dados = db.Column(db.Boolean, nullable=False, default=False)

    ## Permissoes de CONTRATOS
    can_create_contratos = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_contratos = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_contratos = db.Column(db.Boolean, nullable=False, default=False)
    can_view_contratos = db.Column(db.Boolean, nullable=False, default=False)

    ## Permissoes de CATEGORIAS
    can_create_categorias = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_categorias = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_categorias = db.Column(db.Boolean, nullable=False, default=False)
    can_view_categorias = db.Column(db.Boolean, nullable=False, default=False)

    ## Permissoes de DOCUMENTAÇÃO
    can_aprove_docs = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_docs = db.Column(db.Boolean, nullable=False, default=False)
    can_view_docs = db.Column(db.Boolean, nullable=False, default=False)
    
    ## Permissoes de EMPRESAS 
    can_create_empresas = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_empresas = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_empresas = db.Column(db.Boolean, nullable=False, default=False)
    can_view_empresas = db.Column(db.Boolean, nullable=False, default=False)

    ## Permissoes de PERFIS
    can_create_perfis = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_perfis = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_perfis = db.Column(db.Boolean, nullable=False, default=False)
    can_view_perfis =db.Column(db.Boolean, nullable=False, default=False)

    # Permissoes de USERS (Criado com o Google)
    can_edit_users = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_users = db.Column(db.Boolean, nullable=False, default=False)
    can_view_users = db.Column(db.Boolean, nullable=False, default=False)

# Helper function to make strings uppercase
def uppercase_string(mapper, connection, target):
    for column in target.__table__.columns:
        if isinstance(column.type, db.String) and getattr(target, column.name):
            setattr(target, column.name, getattr(target, column.name).upper())

# Attach the listener to all models that have string columns
for model in [Documento, User, Empresa, CUBO, Contrato, Categoria, Perfil]:
    event.listen(model, 'before_insert', uppercase_string)
    event.listen(model, 'before_update', uppercase_string)

class Log(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_perfil = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    info = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    