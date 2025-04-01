from flask import Blueprint, redirect, render_template, request, session, url_for, send_file, abort
from app.auth.auth import auth, get_google_provider_cfg, client, GOOGLE_CLIENT_SECRET, GOOGLE_CLIENT_ID
from app.controllers.UserController import UserController
from app.controllers.DocsControlller import DocsController
from app.controllers.EmpresaController import EmpresaController
from app.controllers.CuboController import CuboController
from app.controllers.CategoriaController import CategoriaController
from app.controllers.ContratoController import ContratoController
from app.controllers.PerfilController import PerfilController
from app.controllers.LogController import LogController

from io import BytesIO
import urllib
import random
import requests
import json
import zlib

from app.models.tables import CUBO, Anexo

bp_app = Blueprint("bp", __name__)

##
## Views
##

###                                         ###
## ENDPOINTS PARA LOGIN E CRIAÇÃO DE USUARIO ##
###                                         ###

# Redireciona o usuario para o endpoint de confirmaão de login

@bp_app.route("/")
def index():
    return render_template("login.html")

@bp_app.route("/login")
def login():
    if "id" in session.keys():
        return redirect(url_for("bp.home"))
    else:
        request_uri = auth()
        return redirect(request_uri)

#Pega as informações do usuario e redireciona para o endpoint de criação de usuario
@bp_app.route("/login/get_user_info")
def get_user_info():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    client.access_token
    # Store tokens in session for later use
    session['google_tokens'] = {
        'access_token': client.access_token,
        'refresh_token': client.refresh_token,
        'expires_in': client.expires_in
    }

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = {
        "id":unique_id, "nome":users_name, "email":users_email, "icon":picture
    }

    icon = user["icon"].split("/")[-1]

    # print(url_for("bp.create_user", id=user["id"], email=user["email"], nome=user["nome"], icon=icon))
    # Send user back to homepage
    return redirect(url_for("bp.create_user", _id=user["id"], email=user["email"], nome=user["nome"], icon=icon))

@bp_app.route("/create_user/<_id>/<email>/<nome>/<icon>", methods=["GET"])
def create_user(_id, email, nome, icon):
    if user := UserController.get(_id):
        #Define os cookies de sessao
        session["perfil"] = user.perfil
        session["id"] = user._id
        session["nome"] = user.nome
        session["email"]  = user.email

        return redirect("/home")
    else:
        user = UserController.create(_id=_id, file=f"https://lh3.googleusercontent.com/a/{icon}", nome=nome, email=email)
        
        #Define os cookies de sessao
        session["perfil"] = user.perfil
        session["id"] = user._id
        session["nome"] = user.nome
        session["email"]  = user.email
        
        return redirect( url_for("bp.home"))
    
@bp_app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("bp.index"))

@bp_app.route('/logout_prestadora')
def logout_prestadora():
    session.clear()
    return redirect(url_for("bp.login_prestadora"))

@bp_app.route("/blocked")
def blocked():
    return render_template("blocked.html")

##
## Endpoint da pagina principal
##
@bp_app.route("/home")
def home():
    if "id" in session.keys():
        user = UserController.get(session["id"])

        if not user.perfil:
            return redirect(url_for("bp.blocked"))
        
        #Puxa o objeto de permissão
        perfil_id = UserController.get(session["id"]).perfil_id
        permissao = PerfilController.get(perfil_id)

        return render_template("index.html", user=user, permissao=permissao)
    else:
        return redirect(url_for("bp.index"))

###                                                             ###
## ENDPOINTS PARA UPLOAD DE DOCUMENTAÇAO E VISUALIAÇÃO DE STATUS (PRESTADORA APENAS)##
###                                                             ###

@bp_app.route("/index_prestadora")
def index_prestadora():
    chave = session["chave_empresa"]
    prestadora = EmpresaController.get(chave=chave)
    return render_template("index_prestadora.html", prestadora=prestadora)

##Pagina para upload de arquivos / View
@bp_app.route("/upload_file_view")
def upload_file_view():
    chave = session["chave_empresa"]
    empresa_id = EmpresaController.get(chave=chave)._id

    contratos = ContratoController.get_all(str(empresa_id))
    categorias = CategoriaController.get_all("")

    return render_template("upload_file.html", contratos=contratos, categorias=categorias)

##Pagina para upload de arquivos / Action
@bp_app.route("/upload_file_action", methods=["POST"])
def upload_file_action():
    form = request.form
    file = request.files
    
    chave = session["chave_empresa"]
    empresa_id = EmpresaController.get(chave=chave)._id
    categoria_nome = CategoriaController.get(form["categoria"]).nome
    contrato_nome = ContratoController.get(form["contrato"]).nome

    form = dict(form)
    form["empresa"] = empresa_id
    form["categoria_nome"] = categoria_nome
    form["contrato_nome"] = contrato_nome

    DocsController.create(form, file)
    return "OK"

##Pagina para visualização de status de documentos enviados
@bp_app.route("/status_files/", defaults={'filter': ""})
@bp_app.route("/status_files/<filter>")
def status_files(filter):
    chave = session["chave_empresa"]
    empresa_id = EmpresaController.get(chave=chave)._id

    documentos_empresa = list(DocsController.filter(empresa_id, filter).items())

    return render_template("status_documentos.html", docs_emp=documentos_empresa)

# Enpoint para altenticação da prestadora
@bp_app.route("/auth_prestadora", methods=["POST"])
def auth_prestadora():
    form = request.form
    chave = form["chave"]
    nome = form["nome"].upper()
    
    empresa = EmpresaController.auth(nome, chave)

    if empresa:
        session["chave_empresa"] = chave
        return "ok"
    else:
        return "erro"
    

#Pagina para servir os anexos(Documentos) na pagina de documentos 
@bp_app.route('/anexo/<id>')
def serve_anexo(id):
    # Query the Documento by _id
    anexo = Anexo.query.filter_by(_id=id).first()
    
    
    if anexo is None:
        # If no document is found, return a 404 error
        abort(404, description="Documento não encontrado")
    try:
        # Decompress the PDF before serving
        decompressed_data = zlib.decompress(anexo.data)

    except zlib.error:
        abort(500, description="Erro ao descompactar o documento")

    # Create a file-like object from the decompressed binary data
    # Save the decompressed data to a temporary Excel file
    temp_file = BytesIO(decompressed_data)

    # If 'download=1' is in the query params, force the download
    return send_file(temp_file, download_name=f"{anexo.filename}.pdf")
    

#Pagina de login da prestadora
@bp_app.route("/login_prestadora")
def login_prestadora():
    return render_template("login_prestadora.html")

##Gera uma nova chave aleatoria para login da prestadora 
@bp_app.route("/gen_key")
def generate_key():
    return str(random.randint(100000, 999999))

##Adiciona uma nova prestadora no banco
@bp_app.route("/create_empresa/<nome>/<chave>/")
@bp_app.route("/create_empresa/<nome>/<chave>/<_id>")
def create_empresa(nome, chave, _id=None):
    try:
        if _id:
            EmpresaController.update(nome, chave, _id)
        else:
            EmpresaController.create(nome, chave)
        
        return "ok"
    except Exception as e:
        return f"erro {e}"

##Exclui uma prestadora do banco
@bp_app.route("/exclui_empresa/<_id>")
def exclui_empresa(_id):
    try:
        EmpresaController.delete(_id=_id)
        return "ok"
    except Exception as e:
        return f"erro {e}"

## Lista as empresas para criação e edição
@bp_app.route("/list_empresas/", defaults={'filter': ""})
@bp_app.route("/list_empresas/<filter>")
def list_empresas(filter):
    empresas = EmpresaController.get_all(filter)

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("list_empresas.html", empresas=empresas, permissao=permissao)

## Lista as empresas para filtro e visualização
@bp_app.route("/filter_prestadoras/", defaults={'content': None})
@bp_app.route("/filter_prestadoras/<path:content>")
def list_prestadoras_filter(content):
    ##Faz o decode do argumento para filtrar
    content = urllib.parse.unquote(content) if content else None
    
    docs = DocsController.filter(None, content)
    
    docs = docs.items()

    return render_template("list_prestadoras_filter.html", docs=docs)

##Lista os documentos filtrados (quando clicado na empresa)
@bp_app.route('/filter_docs/<int:empresa_id>/', defaults={'content': None})
@bp_app.route('/filter_docs/<int:empresa_id>/<path:content>')
def list_docs_filter(empresa_id, content):    
    ##Faz o decode do argumento para filtrar
    content = urllib.parse.unquote(content) if content else None

    # Checa se precisa retornar o historico do documento
    if "hist" in content:
        titulo = content.aplit(",")[1]
        docs = DocsController.get_history_docs(titulo)
    else:
        docs = DocsController.filter(empresa_id, content)
    
    docs = docs.items()

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)
    
    return render_template("list_docs_filter.html", docs_emp=docs, permissao=permissao)

# Atualiza o documento e cria uma nova versao, recria os anexos
@bp_app.route("/update_documento/<id>", methods=["POST"])
def update_documento(doc_id):
    try:
        files = request.files
        DocsController.corrige_documento(doc_id, files)
        
        return "ok"
    except Exception as e:
        return f"erro {e}"
        
#Deleta um documento (Somente admin)
@bp_app.route("/exclui_documento/<id>")
def delete_documento(id):
    try:
        DocsController.delete(id)
        return "ok"
    except Exception as e:
        return f"erro {e}"

##
## Sub-pagina menu do CUBO de dados
##
@bp_app.route("/cubo_menu")
def cubo_menu():
    categorias = CategoriaController.get_all("")
    contratos = ContratoController.get_all("")
    perfis = PerfilController.get_all("")

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("menu_cubo.html",categorias=categorias,
                           contratos=contratos,
                           perfis=perfis,
                           permissao=permissao)

##Cria template de documentação
@bp_app.route("/create_cubo", methods = ["POST"])
def create_cubo():
    form = dict(request.form)
    
    form["categoria_nome"] = CategoriaController.get(form["categoria"]).nome
    form["contrato_nome"] = ContratoController.get(form["contrato"]).nome
    
    try:
        if form["_id"]:
            CuboController.update(form)
        else:
            CuboController.create(form)
        
        return "ok"
        
    except Exception as e:
        return (f"erro:{e}")

##Deleta tamplate de documentaçao
@bp_app.route("/delete_cubo/<_id>")
def delete_cubo(_id):
    try:
        CuboController.delete(_id)
        return "ok"
    except Exception as e:
        return (f"erro:{e}")

## Lista os templates das documentaçoes
@bp_app.route("/list_cubo/", defaults={"filter": ""})
@bp_app.route("/list_cubo/<filter>")
def list_cubo(filter):
    cubos = CuboController.get_all(filter)

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("list_cubo.html", cubos=cubos, permissao=permissao)

##
## Sub-pagina menu de CONTRATOS
##
@bp_app.route("/contrato_menu")
def contrato_menu():
    empresas = EmpresaController.get_all("")
    
    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("menu_contrato.html", empresas=empresas, permissao=permissao)

##Cria contrato das prestadoras
@bp_app.route("/create_contrato", methods = ["POST"])
def create_contrato():
    form = dict(request.form)
    
    try:
        if form["_id"]:
            ContratoController.update(form)
        else:
            form = dict(form)
            form["empresa_nome"] = EmpresaController.get(_id=form["empresa"]).nome
            ContratoController.create(form)
        
        return "ok"
        
    except Exception as e:
        return (f"erro:{e}")

##Deleta contratos das prestadoras
@bp_app.route("/delete_contrato/<_id>")
def delete_contrato(_id):
    try:
        ContratoController.delete(_id)
        return "ok"
    except Exception as e:
        return (f"erro:{e}")

##Lista contratos das prestadoras
@bp_app.route("/list_contratos/", defaults={"filter": ""})
@bp_app.route("/list_contratos/<filter>")
def list_contratos(filter):
    contratos = ContratoController.get_all(filter)

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("list_contratos.html", contratos=contratos, permissao=permissao)

##
## Sub-pagina menu de CATEGORIAS
##
@bp_app.route("/categorias_menu")
def categorias_menu():
    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("menu_categorias.html", permissao=permissao)

##Cria categoria de documentos
@bp_app.route("/create_categoria", methods=["POST"])
def create_categoria():
    form = request.form
    
    try:
        if form["_id"]:
            CategoriaController.update(form)
        else:
            CategoriaController.create(form)
        
        return "ok"
        
    except Exception as e:
        return (f"erro:{e}")


##Deleta cateogoria de documentos
@bp_app.route("/delete_categoria/<id>")
def delete_categoria(id):
    try:
        CategoriaController.delete(id)
        return "ok"
    except Exception as e:
        return (f"erro:{e}")

##Lista categorias de documentos
@bp_app.route("/list_categorias/", defaults={"filter": ""})
@bp_app.route("/list_categorias/<filter>")
def list_categorias(filter):
    categorias = CategoriaController.get_all(filter)

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("list_categorias.html", categorias=categorias, permissao=permissao)

##
## Sub-pagina menu de PERFIS
##

@bp_app.route("/perfil_menu")
def perfil_menu():
    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("menu_perfil.html", permissao=permissao)

##Cria um perfil
@bp_app.route("/create_perfil", methods=["POST"])
def create_perfil():
    form = request.form

    try:
        if form["_id"]:
            # If an _id is provided, retrieve the existing Perfil and update it
            PerfilController.update(form)

        # If no _id is provided, create a new Perfil
        else:
            PerfilController.create(form)
        
        return "ok"
        
    except Exception as e:
        return f"erro:{e}"

## Deleta perfil
@bp_app.route("/delete_perfil/<id>")
def delete_perfil(id):
    try:
        PerfilController.delete(id)
        return "ok"
    except Exception as e:
        return (f"erro:{e}")

##Lista perfis
@bp_app.route("/list_perfil/", defaults={"filter": ""})
@bp_app.route("/list_perfil/<filter>")
def list_perfil(filter):
    perfis = PerfilController.get_all(filter)

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)

    return render_template("list_perfil.html", perfis=perfis, permissao=permissao)

##
## Sub-pagina menu de USERS
##
@bp_app.route("/users_menu")
def users_menu():
    return render_template("menu_user.html")

## Atualiza os perfis dos usuarios
@bp_app.route("/update_user/<user_id>/<perfil_id>")
def update_user(user_id, perfil_id):
    try:
        if user_id and perfil_id:
            UserController.update(user_id,perfil_id)
            return "ok"
        
    except Exception as e:
        return (f"erro:{e}")

## Deleta usuarios
@bp_app.route("/delete_user/<id>")
def delete_user(id):
    try:
        UserController.delete(id)
        return "ok"
    except Exception as e:
        return (f"erro:{e}")

## Lista os usuarios
@bp_app.route("/list_users/", defaults={"filter": ""})
@bp_app.route("/list_users/<filter>")
def list_users(filter):
    users = UserController.get_all(filter)
    perfis = PerfilController.get_all("")

    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)
    
    return render_template("list_user.html", users=users, perfis=perfis,
                           permissao=permissao)

##
## PAGINAS DOS MENUS PRINCIPAIS
##

## Pagina Adm de LOGS (sub-pagina)
@bp_app.route("/adm_logs")
def adm_logs():
    return render_template("adm_logs.html")

##Lista os Logs
@bp_app.route("/list_logs/", defaults={'filter': ""})
@bp_app.route("/list_logs/<filter>")
def list_logs(filter):
    logs = LogController.get_all(filter)
    return render_template("list_logs.html", logs=logs)

## Pagina Adm do cubo de dados PRINCIPAL (sub-pagina)
@bp_app.route("/adm_cubo")
def adm_cubo():
    #Puxa o objeto de permissão
    perfil_id = UserController.get(session["id"]).perfil_id
    permissao = PerfilController.get(perfil_id)
    
    return render_template("adm_cubo.html", permissao=permissao)

## Pagina Adm de empresas (sub-pagina)
@bp_app.route("/adm_empresas")
def adm_empresas():
    return render_template("adm_empresas.html")

## Pagina Adm de documentações (sub-pagina)
@bp_app.route("/adm_documentos")
def adm_documentos():
    permissao = PerfilController.get(UserController.get(session["id"]).perfil_id)
    uploaded = DocsController.is_all_uploaded()

    return render_template("adm_documentos.html", permissao=permissao, uploaded=uploaded)

###                                                    ###
## ENDPOINTS PARA ATUALIZAÇÃO DE STATUS DE DOCUMENTAÇÃO ##
###                                                    ###

##Atualiza status das aprovaçoes da documentação
@bp_app.route("/update_status/<_id>/<string:status>/", defaults={'obs': ""})
@bp_app.route("/update_status/<_id>/<string:status>/<obs>")
def update_status(_id,status,obs):
    try:
    
        DocsController.update_status(_id, obs, status)
        return "ok"
    
    except Exception as e:
        return(f"erro:{e}")

def configure(app):
    app.register_blueprint(bp_app)

## Limpa os anexos depois de fazer o upload para o Google drive
@bp_app.route("/upload_gdrive/")
def upload_gdrive():
    try:
        DocsController.upload_drive()
        #DocsController.limpa_anexos()

        return "ok"
    except Exception as e:
        return(f"erro:{e}")
    