
import os
import zipfile
from datetime import datetime
import shutil

def get_project_files():
    """Get all files in the project that should be backed up"""
    
    # Get project root directory (parent of scripts)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_dir = os.getcwd()
    
    # Change to project root
    os.chdir(project_root)
    
    # Files and directories to exclude
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.gitignore',
        'node_modules',
        '.env',
        'venv',
        '.venv',
        'attached_assets'  # Exclude attached assets as they're not essential
    ]
    
    files_to_backup = []
    
    try:
        # Walk through all files in project
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from dirs list
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                # Skip excluded files
                if not any(pattern in file for pattern in exclude_patterns):
                    file_path = os.path.join(root, file)
                    # Normalize path separators and remove leading ./
                    clean_path = file_path.replace('\\', '/').lstrip('./')
                    files_to_backup.append(clean_path)
        
        # Return to original directory
        os.chdir(original_dir)
        return sorted(files_to_backup)
        
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        os.chdir(original_dir)
        return []

def create_full_backup():
    """Create a comprehensive ZIP backup of the application"""
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_dir = os.getcwd()
    
    # Change to project root
    os.chdir(project_root)
    
    # Ensure backups directory exists
    backups_dir = os.path.join('scripts', 'backups')
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'scripts/backups/app_full_backup_{timestamp}.zip'
    
    # Get list of files to backup
    files_to_backup = get_project_files()
    
    if not files_to_backup:
        print("❌ Nenhum arquivo encontrado para backup!")
        os.chdir(original_dir)
        return None
    
    print(f"📋 Encontrados {len(files_to_backup)} arquivos para backup:")
    for file in files_to_backup[:10]:  # Show first 10 files
        print(f"   📄 {file}")
    
    if len(files_to_backup) > 10:
        print(f"   ... e mais {len(files_to_backup) - 10} arquivos")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    zipf.write(file_path, file_path)
                    print(f"✅ Adicionado: {file_path}")
        
        # Get file size
        file_size = os.path.getsize(zip_filename)
        size_mb = file_size / (1024 * 1024)
        size_kb = file_size / 1024
        
        print(f"\n🎉 Backup completo criado com sucesso!")
        print(f"📁 Arquivo: {zip_filename}")
        if size_mb >= 1:
            print(f"📊 Tamanho: {size_mb:.2f} MB")
        else:
            print(f"📊 Tamanho: {size_kb:.2f} KB")
        print(f"🗂️  Contém {len(files_to_backup)} arquivos do projeto")
        
        # Return to original directory
        os.chdir(original_dir)
        return zip_filename
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        os.chdir(original_dir)
        return None

def list_backup_contents(zip_filename):
    """List contents of a backup ZIP file"""
    if not os.path.exists(zip_filename):
        print(f"❌ Arquivo não encontrado: {zip_filename}")
        return
    
    try:
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            files = zipf.namelist()
            print(f"\n📋 Conteúdo do backup ({len(files)} arquivos):")
            
            # Group files by type/directory
            directories = {}
            for file in sorted(files):
                dir_name = os.path.dirname(file) or 'root'
                if dir_name not in directories:
                    directories[dir_name] = []
                directories[dir_name].append(os.path.basename(file))
            
            for dir_name, dir_files in directories.items():
                print(f"\n   📁 {dir_name}/")
                for file in dir_files:
                    print(f"      📄 {file}")
                    
    except Exception as e:
        print(f"❌ Erro ao listar conteúdo: {e}")

if __name__ == '__main__':
    print("🗃️  Criando backup completo do aplicativo...")
    print("=" * 60)
    
    backup_file = create_full_backup()
    
    if backup_file:
        # Ask if user wants to see contents
        response = input("\n📋 Deseja ver o conteúdo detalhado do backup? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            list_backup_contents(backup_file)
        
        print(f"\n💡 Para restaurar o backup, extraia o arquivo:")
        print(f"   unzip {backup_file}")
