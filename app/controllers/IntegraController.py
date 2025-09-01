from datetime import datetime
from flask import session
from app.controllers.LogController import LogController
from app.models.tables import Contrato, Funcionario, StatusFuncionario, Subcont, Empresa
from app.ext.db import db

class IntegraController:

    @staticmethod
    def aprova(funcionario):
        try:
            status = StatusFuncionario.query.filter_by(funcionario_id=funcionario._id, tipo="INTEGRACAO").order_by(StatusFuncionario.versao.desc()).first()

            perfil = session.get("perfil")
            
            perfil = str(perfil)
            
            print(("RH" in perfil or "SEGURANCA" in perfil))
            print(status.status_integracao == "AGUARDANDO")
            print(bool(status))
            
            if status and status.status_integracao == "AGUARDANDO" and ("RH" in perfil or "SEGURANCA" in perfil):
                status.aprov_rh = "APROVADO" if "RH" in perfil else status.aprov_rh
                status.aprov_seg = "APROVADO" if "SEGURANCA" in perfil else status.aprov_seg
                
                if status.aprov_rh == "APROVADO" and status.aprov_seg == "APROVADO":
                    status.status_integracao = "AGENDADO"
            else:
                return "Sem permissao!"
            
            db.session.commit()
            return f"ok|{perfil}"
        
        except Exception as e:
            return f"erro:{str(e)}"
    
    @staticmethod
    def reprova(funcionario):
        
        try:
            status = StatusFuncionario.query.filter_by(funcionario_id=funcionario._id, tipo="INTEGRACAO").order_by(StatusFuncionario.versao.desc()).first()
            
            perfil = session.get("perfil")
            
            if status and status.status_integracao == "AGUARDANDO" and ("RH" in perfil or "SEGURANCA" in perfil):
                status.status_integracao = "REPROVADO"
                status.aprov_rh = "REPROVADO" if "RH" in perfil else status.aprov_rh
                status.aprov_seg = "REPROVADO" if "SEGURANCA" in perfil else status.aprov_seg
                
            else:
                return "Sem permissao!"
            
            db.session.commit()
            return f"ok|{perfil}"
        
        except Exception as e:
            return f"erro:{str(e)}"

    @staticmethod
    def create_subcontratado(form):
        try:
            empresa = Empresa.query.filter_by(chave=form["chave_empresa"]).first()
            if not empresa:
                raise ValueError("Empresa não encontrada.")
            
            new_subcontratado = Subcont(
                nome=form["nome"],
                cnpj=form["cnpj"],
                empresa_id=empresa._id,
                contrato_id=form["contrato_id"],
            )

            db.session.add(new_subcontratado)
            db.session.commit()
            return "ok"
        except Exception as e:
            return f"Erro ao criar subcontratado: {e}"

    @staticmethod
    def update_subcontratado(form):
        subcontratado = Subcont.query.get(form["_id"])
        if not subcontratado:
            raise ValueError("Subcontratado não encontrado.")

        for key, value in form.items():
            if hasattr(subcontratado, key):
                setattr(subcontratado, key, value)
        db.session.commit()
        return "ok"

    @staticmethod
    def delete_subcontratado(subcontratado_id):
        subcontratado = Subcont.query.get(subcontratado_id)
        if subcontratado:
            LogController.create(session.get("nome", "N/A"),
                                 session.get("perfil", "N/A"),
                                 "SUBCONTRATADOS",
                                 "EXCLUIR",
                                 f"NOME: {subcontratado.nome}")
            
            db.session.delete(subcontratado)
            db.session.commit()
            return "ok"
        return "Subcontratado não encontrado."
            
    @staticmethod
    def get_subcontratado(subcontratado_id):
        return Subcont.query.get(subcontratado_id)
    
    @staticmethod
    def get_all_subcontratados():
        return Subcont.query.all()
    
    @staticmethod
    def create_funcionario(form):
        try:
            required_fields = ["nome", "funcao", "cargo", "setor", "empresa_id", "tipo"]
            for field in required_fields:
                if field not in form or not form[field]:
                    return f"Campo obrigatório não preenchido: {field}"

            empresa = Empresa.query.get(form["empresa_id"])
            if not empresa:
                return "Empresa não encontrada"

            new_funcionario = Funcionario(
                nome=form["nome"]
            )

            db.session.add(new_funcionario)
            db.session.flush()

            status_funcionario = StatusFuncionario(
                status_contratual="ATIVO",
                status_integracao="PENDENTE",
                funcionario_id=new_funcionario._id,
                funcionario_nome=new_funcionario.nome,
                funcao=form["funcao"],
                cargo=form["cargo"],
                setor=form["setor"],
                empresa_id=form["empresa_id"],
                empresa_nome=empresa.nome,
                versao="1.0",
                data=datetime.now(),
                tipo=form["tipo"].upper(),
            )

            db.session.add(status_funcionario)
            
            LogController.create(
                session.get("nome", "N/A"),
                session.get("perfil", "N/A"),
                "FUNCIONARIOS",
                "CREATE",
                f"Created new funcionário: {new_funcionario.nome} for empresa: {empresa.nome}"
            )

            db.session.commit()
            return "ok"
            
        except Exception as e:
            db.session.rollback()
            return f"Erro ao criar funcionário: {str(e)}"
    
    @staticmethod
    def update_funcionario(form):
        funcionario = Funcionario.query.get(form["_id"])
        if not funcionario:
            return "Funcionário não encontrado."

        status_funcionario = StatusFuncionario.query.filter_by(funcionario_id=form["_id"]).order_by(StatusFuncionario.versao.desc()).first()
        if not status_funcionario:
            return "Status do funcionário não encontrado."

        has_changes = (
            funcionario.nome != form["nome"] or
            status_funcionario.funcao != form["funcao"] or
            status_funcionario.cargo != form["cargo"] or
            status_funcionario.setor != form["setor"] or
            str(status_funcionario.empresa_id) != form["empresa_id"] or
            status_funcionario.tipo != form["tipo"].upper() or
            status_funcionario.status_contratual != form["status"].upper()
        )
        
        if not has_changes:
            return "Nenhuma alteração detectada."
        
        new_status_funcionario = StatusFuncionario(
            status_contratual=form["status"],
            status_integracao=status_funcionario.status_integracao,
            funcionario_id=funcionario._id,
            funcionario_nome=form["nome"],
            unidade_atividade=form.get("unidade_atividade", ""),
            unidade_integracao=form.get("unidade_integracao", ""),
            data_aso=form.get("data_aso"),
            contrato_id=form.get("contrato_id"),
            contrato_nome=form.get("contrato_nome"),
            funcao=form["funcao"],
            cargo=form["cargo"],
            setor=form["setor"],
            empresa_id=form["empresa_id"],
            empresa_nome=form.get("empresa_nome", status_funcionario.empresa_nome),
            tipo=form["tipo"],
            data=datetime.now(),
            versao=float(status_funcionario.versao) + 0.1
        )

        funcionario.nome = form["nome"]

        db.session.add(new_status_funcionario)
        db.session.commit()
        return "ok"
    
    @staticmethod
    def create_integra(form):
        funcionario = Funcionario.query.get(form["_id"])
        if not funcionario:
            return "erro: Funcionário não encontrado"

        current_status = StatusFuncionario.query.filter_by(funcionario_id=form["_id"]).order_by(StatusFuncionario.versao.desc()).first()
        if not current_status:
            return "erro: Status atual do funcionário não encontrado."

        existing_integration = StatusFuncionario.query.filter(
            StatusFuncionario.funcionario_id == form["_id"],
            StatusFuncionario.status_integracao.in_(["AGENDADO", "AGUARDANDO"])
        ).first()
        
        if existing_integration and existing_integration.status_integracao == "AGUARDANDO":
            return "Já existe uma integração agendada ou aguardando para este funcionário"
        
        if form.get("data_integracao"):
            try:
                date_obj = datetime.strptime(form["data_integracao"], "%d/%m/%Y").date()
                today = datetime.now().date()
                
                is_after_today = date_obj > today
                is_tuesday_or_thursday = date_obj.weekday() in [1, 3]
                
                if (not is_after_today) or (not is_tuesday_or_thursday):
                    return "A data da integração deve ser terça ou quinta e posterior a data atual!"
            except ValueError:
                return "Formato de data inválido para data_integracao. Use DD/MM/AAAA."
            
        contrato = Contrato.query.get(form["contrato"])
        if not contrato:
            return "Contrato não encontrado."
        
        status_integracao = StatusFuncionario(
            status_contratual="ATIVO",
            status_integracao="AGUARDANDO",
            funcionario_id=funcionario._id,
            funcionario_nome=funcionario.nome,
            unidade_atividade=form["unidade_atividade"],
            unidade_integracao=form["unidade_integracao"],
            data_aso=form.get("data_aso"),
            contrato_id=form["contrato"],
            contrato_nome=contrato.nome,
            funcao=current_status.funcao,
            cargo=current_status.cargo,
            setor=current_status.setor,
            empresa_id=current_status.empresa_id,
            empresa_nome=current_status.empresa_nome,
            tipo=form["tipo"],
            data=datetime.now(),
            data_integracao=date_obj if "date_obj" in locals() else None,
            versao=float(current_status.versao) + 0.1
        )
        
        db.session.add(status_integracao)
        db.session.commit()
        return "ok"
    
    @staticmethod
    def delete_funcionario(funcionario_id):
        
        try:
            funcionario = Funcionario.query.get(funcionario_id)
            
            if not funcionario:
                return "Funcionário não encontrado"
            
            status_records = StatusFuncionario.query.filter_by(funcionario_id=funcionario_id).all()
            
            print(f"Número de status encontrados: {len(status_records)}")
            
            for status in status_records:
                if status.status_integracao in ["PENDENTE", "AGENDADO", "AGUARDANDO"]:
                    return "Não é possível excluir funcionário com integração pendente ou agendada"
            
            for status in status_records:
                db.session.delete(status)
                
            
            nome_funcionario = funcionario.nome
            
            db.session.delete(funcionario)
            
            LogController.create(
                session.get("nome", "N/A"),
                session.get("perfil", "N/A"),
                "FUNCIONARIOS",
                "DELETE",
                f"Deleted funcionário: {nome_funcionario}"
            )
            
            db.session.commit()
            return "ok"
        
        except Exception as e:
            db.session.rollback()
            return f"Erro ao excluir funcionário: {str(e)}"
    
    @staticmethod
    def get_funcionario(funcionario_id):
        funcionario = Funcionario.query.get(funcionario_id)
        if funcionario:
            funcionario.status_funcionario = StatusFuncionario.query.filter_by(funcionario_id=funcionario_id).order_by(StatusFuncionario.versao.desc()).first()
        return funcionario
    
    @staticmethod
    def get_all_funcionario():
        funcionario_list = Funcionario.query.all()
        for funcionario in funcionario_list:
            funcionario.status_funcionario = StatusFuncionario.query.filter_by(funcionario_id=funcionario._id).order_by(StatusFuncionario.versao.desc()).all()
        return funcionario_list
    
    @staticmethod
    def update_integracoes():
        try:
            funcionarios_status = StatusFuncionario.query.filter(StatusFuncionario.status_integracao.in_(["AGUARDANDO", "AGENDADO", "REALIZADO"])).all()
            
            for status in funcionarios_status:
                if status.status_integracao == "AGENDADO" and status.data_integracao and status.data_integracao <= datetime.now().date():
                    status.status_integracao = "REALIZADO"
                elif status.status_integracao == "AGUARDANDO" and status.data_integracao and status.data_integracao < datetime.now().date():
                    status.status_integracao = "EXPIRADO"
                elif status.status_integracao == "REALIZADO" and status.data_integracao and (datetime.now().date() - status.data_integracao).days > 365: # Exemplo: expira após 1 ano
                    status.status_integracao = "EXPIRADO"
            
            db.session.commit()
            return "ok"
        
        except Exception as e:
            db.session.rollback()
            return f"Erro ao atualizar integrações: {str(e)}"
    
    @staticmethod
    def create_agendamento(form):
        # Implementar lógica de criação de agendamento
        pass
    
    @staticmethod
    def update_agendamento(form):
        # Implementar lógica de atualização de agendamento
        pass
    
    @staticmethod
    def get_all_agendamento(filter=None):
        # Implementar lógica para obter todos os agendamentos
        return []
    