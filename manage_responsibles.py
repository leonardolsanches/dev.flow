
import os
import json
from datetime import datetime

ACTIVITIES_FILE = 'data/activities.json'
RESPONSIBLES_FILE = 'data/responsibles.json'

def load_data():
    """Carrega os dados das atividades"""
    try:
        with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"activities": [], "next_id": 1}

def save_data(data):
    """Salva os dados das atividades"""
    with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_responsibles():
    """Carrega a lista de responsáveis"""
    try:
        with open(RESPONSIBLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Lista padrão inicial
        return {
            "managers": ['Aline', 'Fábio', 'Marcos', 'Waldir', 'Mario', 'Washington', 'Wollinger'],
            "director": "Washington"
        }

def save_responsibles(data):
    """Salva a lista de responsáveis"""
    with open(RESPONSIBLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_responsible(name):
    """Adiciona um novo responsável"""
    if not name or not name.strip():
        print("❌ Nome inválido!")
        return False
    
    name = name.strip()
    responsibles = load_responsibles()
    
    if name in responsibles['managers']:
        print(f"⚠️  {name} já existe na lista de responsáveis!")
        return False
    
    responsibles['managers'].append(name)
    responsibles['managers'].sort()
    save_responsibles(responsibles)
    
    print(f"✅ {name} adicionado com sucesso!")
    return True

def remove_responsible(name):
    """Remove um responsável (apenas se não tiver atividades)"""
    responsibles = load_responsibles()
    
    if name not in responsibles['managers']:
        print(f"❌ {name} não encontrado na lista!")
        return False
    
    if name == responsibles['director']:
        print(f"❌ Não é possível remover o diretor!")
        return False
    
    # Verificar se tem atividades
    data = load_data()
    has_activities = False
    
    for activity in data['activities']:
        if isinstance(activity.get('responsible'), list):
            if name in activity['responsible']:
                has_activities = True
                break
        elif activity.get('responsible') == name:
            has_activities = True
            break
    
    if has_activities:
        print(f"⚠️  {name} possui atividades atribuídas e não pode ser removido!")
        print("   Primeiro, reatribua as atividades para outro responsável.")
        return False
    
    responsibles['managers'].remove(name)
    save_responsibles(responsibles)
    
    print(f"✅ {name} removido com sucesso!")
    return True

def list_responsibles():
    """Lista todos os responsáveis"""
    responsibles = load_responsibles()
    
    print("\n" + "="*50)
    print("📋 LISTA DE RESPONSÁVEIS")
    print("="*50)
    print(f"👑 Diretor: {responsibles['director']}")
    print("\n👥 Gestores:")
    for i, manager in enumerate(responsibles['managers'], 1):
        marker = "👑" if manager == responsibles['director'] else "  "
        print(f"{marker} {i}. {manager}")
    print("="*50)

def main():
    """Menu principal"""
    while True:
        print("\n" + "="*50)
        print("🔧 MANUTENÇÃO DE RESPONSÁVEIS")
        print("="*50)
        print("1. 📋 Listar responsáveis")
        print("2. ➕ Adicionar responsável")
        print("3. ➖ Remover responsável")
        print("4. 🚪 Sair")
        print("="*50)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            list_responsibles()
        
        elif choice == '2':
            name = input("\nDigite o nome do novo responsável: ").strip()
            add_responsible(name)
        
        elif choice == '3':
            list_responsibles()
            name = input("\nDigite o nome do responsável a remover: ").strip()
            remove_responsible(name)
        
        elif choice == '4':
            print("\n👋 Saindo...")
            break
        
        else:
            print("\n❌ Opção inválida!")

if __name__ == '__main__':
    main()
