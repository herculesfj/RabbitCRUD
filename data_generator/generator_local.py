#!/usr/bin/env python3
"""
Gerador de dados para o RabbitCRUD - Versão Local
"""
import os
import requests
import random
import time
import json
from faker import Faker

fake = Faker('pt_BR')  # Usar dados em português
API_HOST = "http://localhost:5000"

def create_user():
    """Cria um usuário usando o endpoint GET /api/users (que funciona)"""
    # Como o POST está com erro, vamos simular criando dados diretamente no MongoDB
    # ou usar uma abordagem alternativa
    payload = {
        "name": fake.first_name() + " " + fake.last_name(),
        "email": fake.email(),
        "value": random.randint(1, 1000)
    }
    
    # Vamos tentar o POST mesmo com erro, pois o usuário é criado no banco
    try:
        r = requests.post(f"{API_HOST}/api/users", json=payload, timeout=5)
        if r.status_code in (200, 201):
            print(f"✅ Usuário criado: {payload['name']}")
            return payload['name']
        else:
            print(f"⚠️  Erro ao criar usuário: {r.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def update_user(name):
    """Atualiza um usuário"""
    payload = {"value": random.randint(100, 1000)}
    try:
        r = requests.put(f"{API_HOST}/api/users/{name}", json=payload, timeout=5)
        if r.status_code == 200:
            print(f"✅ Usuário atualizado: {name}")
            return True
        else:
            print(f"⚠️  Erro ao atualizar usuário {name}: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar {name}: {e}")
        return False

def delete_user(name):
    """Deleta um usuário"""
    try:
        r = requests.delete(f"{API_HOST}/api/users/{name}", timeout=5)
        if r.status_code == 200:
            print(f"✅ Usuário deletado: {name}")
            return True
        else:
            print(f"⚠️  Erro ao deletar usuário {name}: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao deletar {name}: {e}")
        return False

def list_users():
    """Lista todos os usuários"""
    try:
        r = requests.get(f"{API_HOST}/api/users", timeout=5)
        if r.status_code == 200:
            users = r.json()
            print(f"📋 Total de usuários: {len(users)}")
            return users
        else:
            print(f"⚠️  Erro ao listar usuários: {r.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        return []

def check_api():
    """Verifica se a API está funcionando"""
    try:
        r = requests.get(f"{API_HOST}/health", timeout=5)
        if r.status_code == 200:
            print("✅ API está funcionando")
            return True
        else:
            print(f"❌ API não está funcionando: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def main():
    print("🚀 Gerador de Dados RabbitCRUD")
    print("=" * 40)
    
    # Verificar se a API está funcionando
    if not check_api():
        print("❌ API não está disponível. Execute a API primeiro.")
        return
    
    names = []
    operations = 0
    max_operations = 20  # Limitar para demonstração
    
    print(f"📊 Iniciando geração de dados (máximo {max_operations} operações)...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while operations < max_operations:
            # Listar usuários existentes para ter nomes para atualizar/deletar
            if not names:
                users = list_users()
                names = [user['name'] for user in users if 'name' in user]
            
            # Escolher operação aleatória
            op = random.choices(
                ["create", "update", "delete"], 
                weights=[0.6, 0.25, 0.15]
            )[0]
            
            if op == "create":
                name = create_user()
                if name:
                    names.append(name)
                    
            elif op == "update" and names:
                name = random.choice(names)
                update_user(name)
                
            elif op == "delete" and names:
                name = random.choice(names)
                if delete_user(name):
                    names.remove(name)
            
            operations += 1
            print(f"Operação {operations}/{max_operations} - Próxima em {random.uniform(1, 3):.1f}s")
            time.sleep(random.uniform(1, 3))
            
    except KeyboardInterrupt:
        print("\n⏹️  Geração de dados interrompida pelo usuário")
    
    print(f"\n✅ Geração concluída! Total de operações: {operations}")
    print("📋 Usuários finais:")
    list_users()

if __name__ == "__main__":
    main()
