from app.ext.db import db
from sqlalchemy import event

###                     ###
## Declaração das models ##
###                     ###

class Funcionario(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)

    cpf = db.Column(db.String, nullable=False) #CPF do funcionario

# Status do funcionario (Pode mudar sem precisar de nova integração)
class StatusFuncionario(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_contratual = db.Column(db.String, nullable=False) #Status contratual do funcionario (ativo, inativo, desligado, etc...)

    funcao = db.Column(db.String, nullable=False) #Função do funcionario
    cargo = db.Column(db.String, nullable=False) #Cargo do funcionario
    
    versao = db.Column(db.String, nullable=False, default="1.0") #Versao do status do funcionario
    data = db.Column(db.String, nullable=False) #Data do status do funcionario

# Integração do funcionario (Criado a cada nova integração agendada)
# A cada nova integração, cria um novo registro na tabela
class Integracao(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    unidade_atividade = db.Column(db.String, nullable=False) #Unidade de atividade do funcionario
    unidade_integracao = db.Column(db.String, nullable=False) #Unidade de integração do funcionario
    
    data_integracao = db.Column(db.String, nullable=False) #Data de integração do funcionario
    data_aso = db.Column(db.String, nullable=False) #Data do ultimo ASO

    funcionario_id = db.Column(db.Integer, nullable=False) #ID do funcionario atrelado a integração
    funcionario_nome = db.Column(db.String, nullable=False) #Nome do funcionario atrelado a integração

    empresa_id = db.Column(db.Integer, nullable=False) #ID da empresa do funcionario
    empresa_nome = db.Column(db.String, nullable=False) #Nome da empresa do funcionario

    contrato_id = db.Column(db.Integer, nullable=False) #ID do contrato do funcionario
    contrato_nome = db.Column(db.String, nullable=False) #Nome do contrato do funcionario

    versao = db.Column(db.String, nullable=False, default="1.0") #Versao da integração do funcionario

# Anexo do documento
class Anexo(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False)

    #ID DO DOCUMENTO ATRELADO AO ANEXO
    documento_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False) #Arquivo do anexo
    link = db.Column(db.String, nullable=False, default="") #Link do anexo no drive

# Empresa subcontratada
class Subcont(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    cnpj = db.Column(db.String, nullable=False) #CNPJ do subcontratado
    contrato_id = db.Column(db.Integer, nullable=False) #ID do contrato do subcontratado
    empresa_id = db.Column(db.Integer, nullable=False) #ID da empresa do subcontratado

# Tipo de Processo
class TipoProcesso(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False) #Nome do tipo de processo

# Tipo de Documentação
class Categoria(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)

    tipo_de_processo_id = db.Column(db.Integer, nullable=False)
    tipo_de_processo_nome = db.Column(db.String, nullable=False)

    # Documento pedidos para cada categoria (usado para o checklist de documentos) ex: folha de pagamento, etc...
    documentos_pedidos = db.Column(db.String, nullable=False) # Lista de documentos necessarios separados por virgula

# Contrato
class Contrato(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    empresa_id = db.Column(db.Integer, nullable=False)
    empresa_nome = db.Column(db.String, nullable=False)

class Documento(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)

    #ID DO CONTRADO ATRELADO AO DOCUMENTO
    contrato_id = db.Column(db.Integer, nullable=False)
    contrato_nome = db.Column(db.String, nullable=False)
    
    # ID DA EMPRESA OU SUBCONTRATADA DO DOCUMENTO
    # Se o documento for de uma empresa, o ID será o da empresa
    # Se o documento for de um subcontratado, o ID será o da subcontratada
    empresa_id = db.Column(db.Integer, nullable=False)
    empresa_nome = db.Column(db.String, nullable=False)

    #ID DA CATEGORIA ATRELADA AO DOCUMENTO
    categoria_id =  db.Column(db.String, nullable=False)
    categoria_nome = db.Column(db.String, nullable=False)
    
    #CONTROLA O STATUS GERAL DO DOCUMENTO
    status = db.Column(db.String, nullable=False, default="AGUARDANDO") #APROVADO / AGUARDANDO / NAO APROVADO / CORRIGIDO

    uploaded = db.Column(db.Boolean, nullable=False, default=False) #Se o documento foi enviado para o drive ou não

    # PARA CADA NOVA VERSAO DO DOCUMENTO, CRIA UM NOVO REGISTRO NA TABELA
    # E OS ANEXO É ATRELADO A ESSE NOVO REGISTRO
    versao = db.Column(db.String, nullable=False, default="1.0") #Versao do documento
    
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
    cnpj = db.Column(db.String, nullable=False) #CNPJ da empresa

    ## Chave unica de 6 digitos para identificação da empresa
    chave = db.Column(db.String, nullable=False)

class Aprovacao(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    perfil_id = db.Column(db.Integer, nullable=False)
    perfil_nome = db.Column(db.String, nullable=False)

    #ID DO DOCUMENTO ATRELADO A APROVAÇÃO
    documento_id = db.Column(db.Integer, nullable=False)
    
    obs = db.Column(db.String, nullable=False, default="") #Caso reprovado dizer o motivo

    data = db.Column(db.String, nullable=False) #Data de aprovação do perfil/departamento
    status = db.Column(db.String, nullable=False, default="AGUARDANDO") #APROVADO / AGUARDANDO / NAO APROVADO

class CUBO(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria_ids = db.Column(db.String, nullable=False)
    categoria_nomes = db.Column(db.String, nullable=False)
    
    perfil_id = db.Column(db.String, nullable=False) #IDs dos perfis separados por vírgula
    perfil_nome = db.Column(db.String, nullable=False) #Nomes dos perfis separados por vírgula
    
    pasta_drive = db.Column(db.String, nullable=False)

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

    # Permissoes de TIPO_PROCESSO
    can_create_tipo_processo = db.Column(db.Boolean, nullable=False, default=False)
    can_edit_tipo_processo = db.Column(db.Boolean, nullable=False, default=False)
    can_delete_tipo_processo = db.Column(db.Boolean, nullable=False, default=False)
    can_update_tipo_processo = db.Column(db.Boolean, nullable=False, default=False)
    can_view_tipo_processo = db.Column(db.Boolean, nullable=False, default=False)
    
# Helper function to make strings uppercase
def uppercase_string(mapper, connection, target):
    for column in target.__table__.columns:
        if isinstance(column.type, db.String) and getattr(target, column.name) and column.name != "pasta_drive":
            setattr(target, column.name, getattr(target, column.name).upper())

class Log(db.Model):
    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    menu = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_perfil = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    info = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)

# Attach the listener to all models that have string columns
for model in [Documento, User, Empresa, CUBO, Contrato, Categoria, Perfil, Aprovacao, Log]:
    # Listen for the 'before_insert' and 'before_update' events
    event.listen(model, 'before_insert', uppercase_string)
    event.listen(model, 'before_update', uppercase_string)
    