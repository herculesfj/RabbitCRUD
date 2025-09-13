#!/usr/bin/env python3
"""
Monitor em Tempo Real do RabbitCRUD
Dashboard web para visualizar operações do banco de dados em tempo real
"""
import time
import threading
import requests
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)

# Dados em tempo real
realtime_data = {
    'users': [],
    'operations': [],
    'stats': {
        'total_users': 0,
        'total_operations': 0,
        'last_update': None
    }
}

# Template HTML para o dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RabbitCRUD - Monitor em Tempo Real</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .status {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }
        
        .status-item {
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
        }
        
        .status-item.success {
            background: #27ae60;
        }
        
        .status-item.warning {
            background: #f39c12;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .panel h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .user-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .user-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #3498db;
            transition: transform 0.2s;
        }
        
        .user-item:hover {
            transform: translateX(5px);
        }
        
        .user-name {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }
        
        .user-email {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .user-value {
            color: #27ae60;
            font-weight: bold;
            float: right;
        }
        
        .operations {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .operation-item {
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            font-size: 0.9em;
        }
        
        .operation-item.create {
            border-left-color: #27ae60;
        }
        
        .operation-item.update {
            border-left-color: #f39c12;
        }
        
        .operation-item.delete {
            border-left-color: #e74c3c;
        }
        
        .operation-time {
            color: #7f8c8d;
            font-size: 0.8em;
        }
        
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #2980b9;
        }
        
        .btn.danger {
            background: #e74c3c;
        }
        
        .btn.danger:hover {
            background: #c0392b;
        }
        
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 10px;
            font-size: 12px;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="auto-refresh pulse">
        🔄 Atualização automática a cada 2 segundos
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🐰 RabbitCRUD - Monitor em Tempo Real</h1>
            <div class="status">
                <div class="status-item success" id="api-status">API: Conectada</div>
                <div class="status-item" id="user-count">Usuários: 0</div>
                <div class="status-item" id="operation-count">Operações: 0</div>
                <div class="status-item" id="last-update">Última atualização: --</div>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="panel">
                <h2>👥 Usuários no Banco</h2>
                <div class="user-list" id="user-list">
                    <p>Carregando usuários...</p>
                </div>
            </div>
            
            <div class="panel">
                <h2>📊 Operações Recentes</h2>
                <div class="operations" id="operations">
                    <p>Carregando operações...</p>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">🔄 Atualizar Agora</button>
            <button class="btn" onclick="startGenerator()">🚀 Iniciar Gerador</button>
            <button class="btn danger" onclick="stopGenerator()">⏹️ Parar Gerador</button>
            <button class="btn" onclick="clearData()">🗑️ Limpar Dados</button>
        </div>
    </div>

    <script>
        let autoRefresh = true;
        let generatorRunning = false;
        
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('user-count').textContent = `Usuários: ${data.stats.total_users}`;
                    document.getElementById('operation-count').textContent = `Operações: ${data.stats.total_operations}`;
                    document.getElementById('last-update').textContent = `Última atualização: ${data.stats.last_update || '--'}`;
                });
        }
        
        function updateUsers() {
            fetch('/api/users')
                .then(response => response.json())
                .then(data => {
                    const userList = document.getElementById('user-list');
                    if (data.users.length === 0) {
                        userList.innerHTML = '<p>Nenhum usuário encontrado</p>';
                        return;
                    }
                    
                    userList.innerHTML = data.users.map(user => `
                        <div class="user-item">
                            <div class="user-name">${user.name}</div>
                            <div class="user-email">${user.email}</div>
                            <div class="user-value">R$ ${user.value}</div>
                        </div>
                    `).join('');
                });
        }
        
        function updateOperations() {
            fetch('/api/operations')
                .then(response => response.json())
                .then(data => {
                    const operationsList = document.getElementById('operations');
                    if (data.operations.length === 0) {
                        operationsList.innerHTML = '<p>Nenhuma operação registrada</p>';
                        return;
                    }
                    
                    operationsList.innerHTML = data.operations.slice(-20).reverse().map(op => `
                        <div class="operation-item ${op.type}">
                            <strong>${op.type.toUpperCase()}</strong>: ${op.description}
                            <div class="operation-time">${op.timestamp}</div>
                        </div>
                    `).join('');
                });
        }
        
        function refreshData() {
            updateStatus();
            updateUsers();
            updateOperations();
        }
        
        function startGenerator() {
            if (generatorRunning) return;
            
            fetch('/api/start-generator', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        generatorRunning = true;
                        alert('Gerador de dados iniciado!');
                    } else {
                        alert('Erro ao iniciar gerador: ' + data.error);
                    }
                });
        }
        
        function stopGenerator() {
            fetch('/api/stop-generator', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    generatorRunning = false;
                    alert('Gerador de dados parado!');
                });
        }
        
        function clearData() {
            if (confirm('Tem certeza que deseja limpar todos os dados?')) {
                fetch('/api/clear-data', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('Dados limpos com sucesso!');
                        refreshData();
                    });
            }
        }
        
        // Atualização automática a cada 2 segundos
        setInterval(() => {
            if (autoRefresh) {
                refreshData();
            }
        }, 2000);
        
        // Carregar dados iniciais
        refreshData();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    return jsonify(realtime_data['stats'])

@app.route('/api/users')
def get_users():
    try:
        response = requests.get('http://localhost:5000/api/users', timeout=5)
        if response.status_code == 200:
            users = response.json()
            realtime_data['users'] = users
            realtime_data['stats']['total_users'] = len(users)
            realtime_data['stats']['last_update'] = datetime.now().strftime('%H:%M:%S')
            return jsonify({'users': users})
        else:
            return jsonify({'users': [], 'error': 'API não disponível'})
    except Exception as e:
        return jsonify({'users': [], 'error': str(e)})

@app.route('/api/operations')
def get_operations():
    return jsonify({'operations': realtime_data['operations']})

@app.route('/api/start-generator', methods=['POST'])
def start_generator():
    try:
        # Iniciar gerador em thread separada
        thread = threading.Thread(target=run_data_generator)
        thread.daemon = True
        thread.start()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop-generator', methods=['POST'])
def stop_generator():
    global generator_running
    generator_running = False
    return jsonify({'success': True})

@app.route('/api/clear-data', methods=['POST'])
def clear_data():
    try:
        # Limpar dados via API
        response = requests.delete('http://localhost:5000/api/clear-all', timeout=5)
        if response.status_code == 200:
            add_operation('clear', 'Todos os dados foram limpos')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Erro ao limpar dados'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def add_operation(op_type, description):
    """Adiciona uma operação à lista de operações"""
    operation = {
        'type': op_type,
        'description': description,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    realtime_data['operations'].append(operation)
    realtime_data['stats']['total_operations'] += 1
    
    # Manter apenas as últimas 100 operações
    if len(realtime_data['operations']) > 100:
        realtime_data['operations'] = realtime_data['operations'][-100:]

def run_data_generator():
    """Executa o gerador de dados"""
    global generator_running
    generator_running = True
    
    import random
    from faker import Faker
    fake = Faker('pt_BR')
    
    while generator_running:
        try:
            # Operação aleatória
            op = random.choices(['create', 'update', 'delete'], weights=[0.6, 0.25, 0.15])[0]
            
            if op == 'create':
                payload = {
                    'name': fake.first_name() + ' ' + fake.last_name(),
                    'email': fake.email(),
                    'value': random.randint(1, 1000)
                }
                response = requests.post('http://localhost:5000/api/users', json=payload, timeout=5)
                if response.status_code in (200, 201):
                    add_operation('create', f"Usuário criado: {payload['name']}")
                else:
                    add_operation('create', f"Erro ao criar usuário: {response.status_code}")
                    
            elif op == 'update' and realtime_data['users']:
                user = random.choice(realtime_data['users'])
                payload = {'value': random.randint(100, 1000)}
                response = requests.put(f"http://localhost:5000/api/users/{user['name']}", json=payload, timeout=5)
                if response.status_code == 200:
                    add_operation('update', f"Usuário atualizado: {user['name']}")
                else:
                    add_operation('update', f"Erro ao atualizar {user['name']}: {response.status_code}")
                    
            elif op == 'delete' and realtime_data['users']:
                user = random.choice(realtime_data['users'])
                response = requests.delete(f"http://localhost:5000/api/users/{user['name']}", timeout=5)
                if response.status_code == 200:
                    add_operation('delete', f"Usuário deletado: {user['name']}")
                else:
                    add_operation('delete', f"Erro ao deletar {user['name']}: {response.status_code}")
            
            # Atualizar lista de usuários
            try:
                response = requests.get('http://localhost:5000/api/users', timeout=5)
                if response.status_code == 200:
                    realtime_data['users'] = response.json()
                    realtime_data['stats']['total_users'] = len(realtime_data['users'])
            except:
                pass
                
            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            add_operation('error', f"Erro no gerador: {str(e)}")
            time.sleep(5)

if __name__ == '__main__':
    print("🚀 Iniciando Monitor em Tempo Real...")
    print("📊 Dashboard disponível em: http://localhost:8000")
    print("⏹️  Pressione Ctrl+C para parar")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
