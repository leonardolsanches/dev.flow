
import json
import os

def reset_activities_data():
    """Reset activities data to initial state"""
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initial data structure
    initial_data = {
        "activities": [],
        "next_id": 1
    }
    
    # Write to file
    activities_file = 'data/activities.json'
    with open(activities_file, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dados zerados com sucesso!")
    print(f"📁 Arquivo: {activities_file}")
    print(f"📊 Status: Dados resetados para estado inicial")

if __name__ == '__main__':
    # Confirm action
    response = input("⚠️  Tem certeza que deseja zerar todos os dados? (s/N): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        reset_activities_data()
    else:
        print("❌ Operação cancelada.")
