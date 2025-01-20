import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app.controllers.CuboController import CuboController
from app.models.tables import CUBO
from app.ext.db import db

# FILE: app/controllers/test_CuboController.py


class TestCuboController(unittest.TestCase):

    @patch('app.controllers.CuboController.db.session.add')
    @patch('app.controllers.CuboController.db.session.commit')
    @patch('app.controllers.CuboController.LogController.create')
    @patch('flask.session', {'nome': 'test_user', 'perfil': 'admin'})
    def test_create_success(self, mock_log_create, mock_db_commit, mock_db_add):
        cubo_form = {
            "categoria": 1,
            "categoria_nome": "Categoria Teste",
            "contrato": 1,
            "contrato_nome": "Contrato Teste",
            "prazo": "2023-12-31",
            "perfil": 1,
            "perfil_nome": "Perfil Teste",
            "drive": "drive_test"
        }

        CuboController.create(cubo_form)

        mock_db_add.assert_called_once()
        mock_db_commit.assert_called_once()
        mock_log_create.assert_called_once_with(
            'test_user', 'admin', 'DADOS', 'CRIAR', 
            'PERFIL: Perfil Teste | CATEGORIA: Categoria Teste'
        )

    @patch('app.controllers.CuboController.db.session.add')
    @patch('app.controllers.CuboController.db.session.commit')
    @patch('app.controllers.CuboController.LogController.create')
    @patch('flask.session', {'nome': 'test_user', 'perfil': 'admin'})
    def test_create_missing_fields(self, mock_log_create, mock_db_commit, mock_db_add):
        cubo_form = {
            "categoria": 1,
            "categoria_nome": "Categoria Teste",
            "contrato": 1,
            "contrato_nome": "Contrato Teste",
            "prazo": "2023-12-31",
            "perfil": 1,
            "perfil_nome": "Perfil Teste"
            # Missing "drive"
        }

        with self.assertRaises(KeyError):
            CuboController.create(cubo_form)

        mock_db_add.assert_not_called()
        mock_db_commit.assert_not_called()
        mock_log_create.assert_not_called()

    @patch('app.controllers.CuboController.db.session.add')
    @patch('app.controllers.CuboController.db.session.commit')
    @patch('app.controllers.CuboController.LogController.create')
    @patch('flask.session', {'nome': 'test_user', 'perfil': 'admin'})
    def test_create_invalid_data(self, mock_log_create, mock_db_commit, mock_db_add):
        cubo_form = {
            "categoria": "invalid",  # Invalid data type
            "categoria_nome": "Categoria Teste",
            "contrato": 1,
            "contrato_nome": "Contrato Teste",
            "prazo": "2023-12-31",
            "perfil": 1,
            "perfil_nome": "Perfil Teste",
            "drive": "drive_test"
        }

        with self.assertRaises(ValueError):
            CuboController.create(cubo_form)

        mock_db_add.assert_not_called()
        mock_db_commit.assert_not_called()
        mock_log_create.assert_not_called()

if __name__ == '__main__':
    unittest.main()