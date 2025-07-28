from app.models.tables import Relatorio
from app.ext.db import db

class RelatoriosController:

    @staticmethod
    def criar_relatorio(titulo, dados):
        try:
            relatorio = Relatorio(titulo=titulo, dados=dados)
            db.session.add(relatorio)
            db.session.commit()

            return relatorio
        except Exception as e:
            raise Exception(f"Erro ao criar relatório: {str(e)}")

    @staticmethod
    def DataToPDF(relatorio):
        try:
            # Implementar a lógica para converter os dados do relatório em PDF
            pass
        except Exception as e:
            raise Exception(f"Erro ao gerar PDF: {str(e)}")
    
    @staticmethod
    def DataToExcel(relatorio):
        try:
            # Implementar a lógica para converter os dados do relatório em Excel
            pass
        except Exception as e:
            raise Exception(f"Erro ao gerar Excel: {str(e)}")
        
    @staticmethod
    def gerar_relatorio(_id):
        try:
            relatorio = Relatorio.query.filter_by(id=_id).first()
            if not relatorio:
                raise ValueError("Relatório não encontrado.")
            # Trasformar os dados do relatorio em query sql e retornar o resultado

        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
    
    def exportar_relatorio(_id, formato):
        try:
            relatorio = Relatorio.query.filter_by(id=_id).first()
            if formato == 'PDF':
                relatorio_pdf = RelatoriosController.DataToPDF(relatorio)
            
            elif formato == 'Excel':
                relatorio_excel = RelatoriosController.DataToExcel(relatorio)
            else:
                raise ValueError("Formato inválido. Use 'PDF' ou 'Excel'.")
            
            return relatorio_pdf if formato == 'PDF' else relatorio_excel
        except Exception as e:
            raise Exception(f"Erro ao exportar relatório: {str(e)}")
        
    def visualizar_relatorio(self, relatorio):
        try:
            return self.relatorio_service.visualizar_relatorio(relatorio)
        except Exception as e:
            raise Exception(f"Erro ao visualizar relatório: {str(e)}")
    