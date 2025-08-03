
#!/usr/bin/env python3
"""
Script de Manutenção - Limpeza e Backup
Executa limpeza de arquivos não utilizados e cria backup do aplicativo
"""

import os
import sys
import subprocess
from datetime import datetime

def run_script(script_name, description):
    """Execute a Python script and return success status"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              cwd=os.path.dirname(__file__),
                              capture_output=False, 
                              text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar {script_name}: {e}")
        return False

def main():
    """Main maintenance routine"""
    print("🛠️  SCRIPT DE MANUTENÇÃO DO SISTEMA")
    print("=" * 50)
    print("Este script irá:")
    print("1. 🧹 Limpar arquivos não utilizados")
    print("2. 🗃️  Criar backup completo do aplicativo")
    print("=" * 50)
    
    # Confirm execution
    response = input("\n⚠️  Deseja continuar com a manutenção? (s/N): ")
    if response.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Manutenção cancelada.")
        return
    
    start_time = datetime.now()
    success_count = 0
    
    # Step 1: Cleanup
    if run_script('cleanup_unused.py', 'Executando Limpeza de Arquivos'):
        success_count += 1
        print("✅ Limpeza concluída com sucesso!")
    else:
        print("❌ Erro na limpeza de arquivos!")
    
    # Step 2: Backup
    if run_script('create_backup.py', 'Criando Backup do Aplicativo'):
        success_count += 1
        print("✅ Backup concluído com sucesso!")
    else:
        print("❌ Erro na criação do backup!")
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*50}")
    print(f"🎯 MANUTENÇÃO CONCLUÍDA")
    print(f"{'='*50}")
    print(f"⏱️  Tempo decorrido: {duration.total_seconds():.2f} segundos")
    print(f"✅ Operações bem-sucedidas: {success_count}/2")
    
    if success_count == 2:
        print("🎉 Manutenção realizada com sucesso!")
    else:
        print("⚠️  Algumas operações falharam. Verifique os logs acima.")

if __name__ == '__main__':
    main()
