from app.models.tables import Perfil
from app.ext.db import db
from app.controllers.LogController import LogController
from app.controllers.FilterController import FilterController

from flask import session

class PerfilController:
    @staticmethod
    def create(form):
        user = Perfil(nome = form["nome"])
        db.session.add(user)
        db.session.commit()
        
        #Salva o Log da ação
        LogController.create(session["nome"],
                             session["perfil"],
                             "PERFIL",
                             "CRIAR",
                             f"NOME: {user.nome}")
    
    @staticmethod
    def update(form):
        perfil = PerfilController.get(form["_id"])
        perfil.nome = form["nome"]

        modified_permissions = []

        # Update and track changes for dados
        if perfil.can_create_dados != (form.get("criar-dados") == '1'):
            perfil.can_create_dados = form.get("criar-dados") == '1'
            modified_permissions.append(f"criar-dados: {perfil.can_create_dados}")
        
        if perfil.can_edit_dados != (form.get("edit-dados") == '1'):
            perfil.can_edit_dados = form.get("edit-dados") == '1'
            modified_permissions.append(f"edit-dados: {perfil.can_edit_dados}")
        
        if perfil.can_delete_dados != (form.get("delete-dados") == '1'):
            perfil.can_delete_dados = form.get("delete-dados") == '1'
            modified_permissions.append(f"delete-dados: {perfil.can_delete_dados}")
        
        if perfil.can_view_dados != (form.get("view-dados") == '1'):
            perfil.can_view_dados = form.get("view-dados") == '1'
            modified_permissions.append(f"view-dados: {perfil.can_view_dados}")

        # Update and track changes for contratos
        if perfil.can_create_contratos != (form.get("criar-contrato") == '1'):
            perfil.can_create_contratos = form.get("criar-contrato") == '1'
            modified_permissions.append(f"criar-contrato: {perfil.can_create_contratos}")
        
        if perfil.can_edit_contratos != (form.get("edit-contrato") == '1'):
            perfil.can_edit_contratos = form.get("edit-contrato") == '1'
            modified_permissions.append(f"edit-contrato: {perfil.can_edit_contratos}")

        if perfil.can_delete_contratos != (form.get("delete-contrato") == '1'):
            perfil.can_delete_contratos = form.get("delete-contrato") == '1'
            modified_permissions.append(f"delete-contrato: {perfil.can_delete_contratos}")

        if perfil.can_view_contratos != (form.get("view-contrato") == '1'):
            perfil.can_view_contratos = form.get("view-contrato") == '1'
            modified_permissions.append(f"view-contrato: {perfil.can_view_contratos}")

        # Update and track changes for categorias
        if perfil.can_create_categorias != (form.get("criar-categoria") == '1'):
            perfil.can_create_categorias = form.get("criar-categoria") == '1'
            modified_permissions.append(f"criar-categoria: {perfil.can_create_categorias}")

        if perfil.can_edit_categorias != (form.get("edit-categoria") == '1'):
            perfil.can_edit_categorias = form.get("edit-categoria") == '1'
            modified_permissions.append(f"edit-categoria: {perfil.can_edit_categorias}")

        if perfil.can_delete_categorias != (form.get("delete-categoria") == '1'):
            perfil.can_delete_categorias = form.get("delete-categoria") == '1'
            modified_permissions.append(f"delete-categoria: {perfil.can_delete_categorias}")

        if perfil.can_view_categorias != (form.get("view-categoria") == '1'):
            perfil.can_view_categorias = form.get("view-categoria") == '1'
            modified_permissions.append(f"view-categoria: {perfil.can_view_categorias}")

        # Update and track changes for docs
        if perfil.can_aprove_docs != (form.get("aprove_docs") == '1'):
            perfil.can_aprove_docs = form.get("aprove_docs") == '1'
            modified_permissions.append(f"aprove-docs: {perfil.can_aprove_docs}")

        if perfil.can_delete_docs != (form.get("delete-docs") == '1'):
            perfil.can_delete_docs = form.get("delete-docs") == '1'
            modified_permissions.append(f"delete-docs: {perfil.can_delete_docs}")

        if perfil.can_view_docs != (form.get("view-docs") == '1'):
            perfil.can_view_docs = form.get("view-docs") == '1'
            modified_permissions.append(f"view-docs: {perfil.can_view_docs}")

        # Update and track changes for empresas
        if perfil.can_create_empresas != (form.get("criar-empresa") == '1'):
            perfil.can_create_empresas = form.get("criar-empresa") == '1'
            modified_permissions.append(f"criar-empresa: {perfil.can_create_empresas}")

        if perfil.can_edit_empresas != (form.get("edit-empresa") == '1'):
            perfil.can_edit_empresas = form.get("edit-empresa") == '1'
            modified_permissions.append(f"edit-empresa: {perfil.can_edit_empresas}")

        if perfil.can_delete_empresas != (form.get("delete-empresa") == '1'):
            perfil.can_delete_empresas = form.get("delete-empresa") == '1'
            modified_permissions.append(f"delete-empresa: {perfil.can_delete_empresas}")

        if perfil.can_view_empresas != (form.get("view-empresa") == '1'):
            perfil.can_view_empresas = form.get("view-empresa") == '1'
            modified_permissions.append(f"view-empresa: {perfil.can_view_empresas}")

        # Update and track changes for perfis
        if perfil.can_create_perfis != (form.get("criar-perfil") == '1'):
            perfil.can_create_perfis = form.get("criar-perfil") == '1'
            modified_permissions.append(f"criar-perfil: {perfil.can_create_perfis}")

        if perfil.can_edit_perfis != (form.get("edit-perfil") == '1'):
            perfil.can_edit_perfis = form.get("edit-perfil") == '1'
            modified_permissions.append(f"edit-perfil: {perfil.can_edit_perfis}")

        if perfil.can_delete_perfis != (form.get("delete-perfil") == '1'):
            perfil.can_delete_perfis = form.get("delete-perfil") == '1'
            modified_permissions.append(f"delete-perfil: {perfil.can_delete_perfis}")

        if perfil.can_view_perfis != (form.get("view-perfil") == '1'):
            perfil.can_view_perfis = form.get("view-perfil") == '1'
            modified_permissions.append(f"view-perfil: {perfil.can_view_perfis}")

        # Update and track changes for users
        if perfil.can_edit_users != (form.get("edit-users") == '1'):
            perfil.can_edit_users = form.get("edit-users") == '1'
            modified_permissions.append(f"edit-users: {perfil.can_edit_users}")

        if perfil.can_delete_users != (form.get("delete-users") == '1'):
            perfil.can_delete_users = form.get("delete-users") == '1'
            modified_permissions.append(f"delete-users: {perfil.can_delete_users}")

        if perfil.can_view_users != (form.get("view-users") == '1'):
            perfil.can_view_users = form.get("view-users") == '1'
            modified_permissions.append(f"view-users: {perfil.can_view_users}")

        # Save the log with only modified permissions
        if modified_permissions:
            db.session.commit()
            
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "PERFIL",
                                 "ALTERAR",
                                 ' | '.join(modified_permissions))
    
    @staticmethod
    def get(id):
        perfil = Perfil.query.get(id)
        return perfil
    
    @staticmethod
    def get_all(filter):    
        filtered_data = FilterController.filter(filter, Perfil)
        
        return filtered_data
    
    @staticmethod
    def delete(id):
        perfil = Perfil.query.get(id)
        if perfil:

            #Salva o Log da ação
            LogController.create(session["nome"],
                                 session["perfil"],
                                 "PERFIL",
                                 "DELETAR",
                                 f"NOME: {perfil.nome}")
            
            db.session.delete(perfil)
            db.session.commit()
            return True
        return False
