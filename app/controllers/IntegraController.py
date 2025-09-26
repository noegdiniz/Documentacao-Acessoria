from datetime import datetime, timedelta
from flask import session
from app.controllers.LogController import LogController
from app.ext.filter import gerar_proxima_versao
from app.models.tables import AnexosFuncionario, Contrato, Funcionario, StatusFuncionario, Subcont, Empresa
from app.ext.db import db
from sqlalchemy import cast, Numeric

class IntegraController:
    @staticmethod
    def get_funcionarios_excel(data_inicio=None, data_fim=None, empresa_id=None, unidade_integracao=None):
        query = StatusFuncionario.query
        if empresa_id:
            query = query.filter(StatusFuncionario.empresa_id == empresa_id)
        if data_inicio:
            query = query.filter(StatusFuncionario.data_integracao >= data_inicio)
        if data_fim:
            query = query.filter(StatusFuncionario.data_integracao <= data_fim)
        if unidade_integracao:
            query = query.filter(StatusFuncionario.unidade_integracao == unidade_integracao)
            
        # Busca apenas o último status (maior versão) de cada funcionário
        subquery = db.session.query(
            StatusFuncionario.funcionario_id,
            db.func.max(cast(StatusFuncionario.versao, Numeric)).label("max_versao")
        ).group_by(StatusFuncionario.funcionario_id).subquery()

        query = query.join(
            subquery,
            (StatusFuncionario.funcionario_id == subquery.c.funcionario_id) &
            (cast(StatusFuncionario.versao, Numeric) == subquery.c.max_versao)
        )
        
        results = query.order_by(StatusFuncionario.data_integracao.desc()).all()
        funcionarios = []
        for status in results:
            empresa_cnpj = Empresa.query.filter_by(_id=status.empresa_id).first().cnpj if status.empresa_id else ""
            
            funcionarios.append({
                "nome": status.funcionario_nome,
                "funcao": status.funcao,
                "cargo": status.cargo,
                "setor": status.setor,
                "status": status.status_contratual,
                "status_integracao": status.status_integracao,
                "empresa_nome": status.empresa_nome,
                "data_integracao": status.data_integracao.strftime('%d/%m/%Y') if status.data_integracao else "",
                "contrato": status.contrato_nome,
                "empresa_cnpj": empresa_cnpj
            })
        return funcionarios

    @staticmethod
    def get_integracoes_pdf(data_inicio=None, data_fim=None, empresa_id=None, unidade_integracao=None):
        query = StatusFuncionario.query.filter(StatusFuncionario.status_integracao.in_(["AGENDADO"]))
        if empresa_id:
            query = query.filter(StatusFuncionario.empresa_id == empresa_id)
        if data_inicio:
            query = query.filter(StatusFuncionario.data_integracao >= data_inicio)
        if data_fim:
            query = query.filter(StatusFuncionario.data_integracao <= data_fim)
        if unidade_integracao:
            query = query.filter(StatusFuncionario.unidade_integracao == unidade_integracao)
        
        results = query.order_by(StatusFuncionario.data_integracao.desc()).all()
        integracoes = []
        for status in results:
            integracoes.append({
                "nome": status.funcionario_nome,
                "funcao": status.funcao,
                "setor": status.setor,
                "data_integracao": status.data_integracao.strftime('%d/%m/%Y') if status.data_integracao else "",
                "empresa_nome": status.empresa_nome,
            })
            
        return integracoes

    @staticmethod
    def aprova(funcionario):
        try:
            # --- CORREÇÃO APLICADA AQUI ---
            status = StatusFuncionario.query.filter_by(
                funcionario_id=funcionario._id, tipo="INTEGRACAO"
            ).order_by(
                cast(StatusFuncionario.versao, Numeric).desc()
            ).first()

            perfil = session.get("perfil")
            perfil = str(perfil)
            
            if status and status.status_integracao == "AGENDADO" and ("SEGURANCA" in perfil):
                status.status_integracao = "REALIZADO"
                status.status_contratual = "ATIVO"
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
                status_contratual="INATIVO",
                status_integracao="AGUARDANDO",
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

        # --- CORREÇÃO APLICADA AQUI ---
        status_funcionario = StatusFuncionario.query.filter_by(
            funcionario_id=form["_id"]
        ).order_by(
            cast(StatusFuncionario.versao, Numeric).desc()
        ).first()
        
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
            tipo=form["tipo"].upper(),
            data=datetime.now(),
            versao=gerar_proxima_versao(status_funcionario.versao)
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

        current_status = StatusFuncionario.query.filter_by(
            funcionario_id=form["_id"]
        ).order_by(
            cast(StatusFuncionario.versao, Numeric).desc()
        ).first()

        if not current_status:
            return "erro: Status atual do funcionário não encontrado."

        # Retorna erro se já houver uma integração agendada ou realizada
        if current_status.status_integracao in ["AGENDADO", "REALIZADO"]:
            return "Erro: Já existe uma integração agendada ou realizada para este funcionário."
        
        # Não é posssivel agendar integração para funcionário com status contratual INATIVO
        print(f"Current status contratual: {current_status.status_contratual}")
        if current_status.status_contratual == "INATIVO":
            return "Erro: Não é possível agendar integração para funcionário com status contratual INATIVO."
        
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

        # Atualiza apenas o último status
        current_status.status_contratual = "INATIVO"
        current_status.status_integracao = "AGENDADO"
        current_status.unidade_atividade = form["unidade_atividade"]
        current_status.unidade_integracao = form["unidade_integracao"]
        current_status.data_aso = datetime.strptime(form.get("data_aso"), "%d/%m/%Y").date() if form.get("data_aso") else None
        current_status.contrato_id = form["contrato"]
        current_status.contrato_nome = contrato.nome
        current_status.data = datetime.now()
        current_status.data_integracao = date_obj if "date_obj" in locals() else None
        current_status.tipo = form["tipo"].upper()

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
            print(f"Excluindo {len(status_records)} status associados ao funcionário.")
            
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
            
            print(f"Excluindo funcionário: {nome_funcionario} e seus {len(status_records)} status associados.")
            
            db.session.commit()
            return "ok"
        
        except Exception as e:
            db.session.rollback()
            return f"Erro ao excluir funcionário: {str(e)}"
    
    @staticmethod
    def get_funcionario(funcionario_id):
        funcionario = Funcionario.query.get(funcionario_id)
        if funcionario:
            # --- CORREÇÃO APLICADA AQUI ---
            funcionario.status_funcionario = StatusFuncionario.query.filter_by(
                funcionario_id=funcionario_id
            ).order_by(
                cast(StatusFuncionario.versao, Numeric).desc()
            ).first()
        return funcionario
    
    @staticmethod
    def get_all_funcionario(empresa_id=None):
        
        if empresa_id:
            funcionario_list = Funcionario.query.join(StatusFuncionario, Funcionario._id == StatusFuncionario.funcionario_id)
            funcionario_list = funcionario_list.filter(StatusFuncionario.empresa_id == empresa_id).all()
        else:
            funcionario_list = Funcionario.query.all()
            

        for funcionario in funcionario_list:
            
            # --- CORREÇÃO APLICADA AQUI ---
            # Nota: .all() foi mantido pois parece ser a intenção original de carregar todo o histórico.
            # A ordenação agora está correta.
            funcionario.status_funcionario = StatusFuncionario.query.filter_by(
                funcionario_id=funcionario._id
            ).order_by(
                cast(StatusFuncionario.versao, Numeric).asc()
            ).all()
            
        return funcionario_list
    
    @staticmethod
    def update_integracoes():
        try:
            # Busca apenas o último status (maior versão) de cada funcionário
            subquery = (
                db.session.query(
                    StatusFuncionario.funcionario_id,
                    db.func.max(cast(StatusFuncionario.versao, Numeric)).label("max_versao")
                )
                .filter(StatusFuncionario.status_integracao.in_(["AGUARDANDO", "AGENDADO", "REALIZADO"]))
                .group_by(StatusFuncionario.funcionario_id)
                .subquery()
            )

            funcionarios_status = (
                StatusFuncionario.query
                .join(
                    subquery,
                    (StatusFuncionario.funcionario_id == subquery.c.funcionario_id) &
                    (cast(StatusFuncionario.versao, Numeric) == subquery.c.max_versao)
                )
                .filter(StatusFuncionario.status_integracao.in_(["AGUARDANDO", "AGENDADO", "REALIZADO"]))
                .all()
            )
            
            for status in funcionarios_status:
                if status.status_integracao == "AGENDADO" and status.data_integracao and datetime.now().date() > status.data_integracao:
                    print(f"Atualizando status para EXPIRADO para funcionário_id: {status.funcionario_id}, data_integracao: {status.data_integracao}")
                    status.status_integracao = "EXPIRADO"
                    
                elif status.status_integracao == "REALIZADO" and status.data_integracao and (datetime.now().date() - status.data_integracao).days >= 365: # Exemplo: expira após 1 ano
                    status.status_integracao = "EXPIRADO"
            
                # Atualiza status para "CANCELADO" se a empresa estiver inativa
                empresa = Empresa.query.get(status.empresa_id)
                if empresa:
                    if empresa.status == "INATIVA" and status.status_integracao in ["AGUARDANDO", "AGENDADO"]:
                        status.status_integracao = "CANCELADO"
                        status.status_contratual = "INATIVO"
            
            # Limpda todos os anexos de funcionários com upload_date ha mais de 30 dias
            thirty_days_ago = datetime.now() - timedelta(days=30)
            old_anexos = AnexosFuncionario.query.filter(AnexosFuncionario.upload_date < thirty_days_ago).all()
            for anexo in old_anexos:
                db.session.delete(anexo)
                
            db.session.commit()
            return "ok"
        
        except Exception as e:
            db.session.rollback()
            return f"Erro ao atualizar integrações: {str(e)}"
        