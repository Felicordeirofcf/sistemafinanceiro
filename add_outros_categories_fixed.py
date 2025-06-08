#!/usr/bin/env python3
"""
Script para adicionar categorias 'Outros' para receitas e despesas
e criar uma rota para dados do calendário
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import db_session, init_db
from models.category import Category
from models.user import User

def add_outros_categories():
    """Adiciona categorias 'Outros' para todos os usuários que não as possuem"""
    
    # Inicializa o banco de dados
    init_db()
    
    # Busca todos os usuários
    users = db_session.query(User).all()
    
    if not users:
        print("Nenhum usuário encontrado no banco de dados")
        return
    
    for user in users:
        print(f"Processando usuário {user.id} ({user.email})...")
        
        # Verifica se já existe categoria 'Outros' para receitas
        outros_receita = db_session.query(Category).filter_by(
            user_id=user.id, 
            nome='Outros', 
            tipo='receita'
        ).first()
        
        if not outros_receita:
            print(f"  Criando categoria 'Outros' para receitas...")
            outros_receita = Category(
                user_id=user.id,
                nome='Outros',
                tipo='receita',
                cor='#95a5a6',
                icone='fa-question-circle'
            )
            db_session.add(outros_receita)
        else:
            print(f"  Categoria 'Outros' para receitas já existe")
        
        # Verifica se já existe categoria 'Outros' para despesas
        outros_despesa = db_session.query(Category).filter_by(
            user_id=user.id, 
            nome='Outros', 
            tipo='despesa'
        ).first()
        
        if not outros_despesa:
            print(f"  Criando categoria 'Outros' para despesas...")
            outros_despesa = Category(
                user_id=user.id,
                nome='Outros',
                tipo='despesa',
                cor='#95a5a6',
                icone='fa-question-circle'
            )
            db_session.add(outros_despesa)
        else:
            print(f"  Categoria 'Outros' para despesas já existe")
    
    # Salva as alterações
    db_session.commit()
    print("Categorias 'Outros' adicionadas com sucesso!")
    
    # Lista todas as categorias para verificação
    print("\nCategorias por usuário:")
    for user in users:
        categorias = db_session.query(Category).filter_by(user_id=user.id).all()
        print(f"Usuário {user.id} ({user.email}):")
        for cat in categorias:
            print(f"  - {cat.nome} ({cat.tipo})")

if __name__ == "__main__":
    add_outros_categories()

