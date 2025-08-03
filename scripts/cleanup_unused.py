
import os
import shutil

def cleanup_unused_files():
    """Remove unused files and directories"""
    
    # Directories to remove if they exist
    unused_dirs = [
        'attached_assets',  # Assets não utilizados
        '__pycache__',      # Cache do Python
        '.git',             # Git (se existir)
        'node_modules',     # Node modules (se existir)
        'venv',             # Virtual env (se existir)
        '.venv',            # Virtual env alternativo
        'exports',          # Pasta de exports antigos
        'backups'           # Backups antigos (opcional)
    ]
    
    # Files to remove if they exist
    unused_files = [
        '.gitignore',
        'README.md',
        'requirements.txt',  # Usando pyproject.toml agora
        'package.json',
        'package-lock.json',
        'yarn.lock'
    ]
    
    removed_items = []
    
    print("🧹 Iniciando limpeza de arquivos não utilizados...")
    
    # Remove directories
    for dir_name in unused_dirs:
        if os.path.exists(dir_name):
            try:
                if dir_name == 'backups':
                    # Ask confirmation for backups
                    response = input(f"⚠️  Remover pasta '{dir_name}'? (s/N): ")
                    if response.lower() not in ['s', 'sim', 'y', 'yes']:
                        continue
                
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                    removed_items.append(f"📁 Pasta: {dir_name}")
                    print(f"✅ Removida pasta: {dir_name}")
                else:
                    os.remove(dir_name)
                    removed_items.append(f"📄 Arquivo: {dir_name}")
                    print(f"✅ Removido arquivo: {dir_name}")
            except Exception as e:
                print(f"❌ Erro ao remover {dir_name}: {e}")
    
    # Remove files
    for file_name in unused_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            try:
                os.remove(file_name)
                removed_items.append(f"📄 Arquivo: {file_name}")
                print(f"✅ Removido arquivo: {file_name}")
            except Exception as e:
                print(f"❌ Erro ao remover {file_name}: {e}")
    
    # Clean Python cache in subdirectories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                removed_items.append(f"📁 Cache: {pycache_path}")
                print(f"✅ Removido cache: {pycache_path}")
            except Exception as e:
                print(f"❌ Erro ao remover cache {pycache_path}: {e}")
    
    # Summary
    print(f"\n🎯 Limpeza concluída!")
    if removed_items:
        print(f"📊 Itens removidos ({len(removed_items)}):")
        for item in removed_items:
            print(f"   {item}")
    else:
        print("📊 Nenhum arquivo não utilizado encontrado.")
    
    return len(removed_items)

def show_disk_usage():
    """Show current directory disk usage"""
    try:
        import subprocess
        result = subprocess.run(['du', '-sh', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            size = result.stdout.strip().split()[0]
            print(f"💾 Tamanho atual do projeto: {size}")
    except:
        print("💾 Não foi possível calcular o tamanho do projeto")

if __name__ == '__main__':
    print("🧹 Script de Limpeza de Arquivos Não Utilizados")
    print("=" * 50)
    
    # Show current size
    show_disk_usage()
    
    # Confirm action
    response = input("\n⚠️  Deseja continuar com a limpeza? (s/N): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        removed_count = cleanup_unused_files()
        
        # Show new size
        if removed_count > 0:
            print("\n" + "=" * 50)
            show_disk_usage()
    else:
        print("❌ Limpeza cancelada.")
