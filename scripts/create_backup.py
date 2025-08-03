import os
import zipfile
from datetime import datetime
import shutil

def create_app_backup():
    """Create a ZIP backup of the entire application"""

    # Get project root directory (parent of scripts)
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
    zip_filename = f'scripts/backups/app_backup_{timestamp}.zip'

    # Files and directories to include
    include_paths = [
        'app.py',
        'main.py',
        'pyproject.toml',
        'uv.lock',
        '.replit',
        'replit.md',
        'data/',
        'static/',
        'templates/',
        'scripts/'
    ]

    # Files and directories to exclude
    exclude_patterns = [
        '__pycache__',
        '.git',
        'node_modules',
        '.env',
        'venv',
        '.venv',
        'backups',
        'attached_assets'  # Removido da lista de exclusão se quiser incluir
    ]

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through all files in current directory and subdirectories
            for root, dirs, files in os.walk('.'):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

                # Skip if current directory should be excluded
                if any(pattern in root for pattern in exclude_patterns):
                    continue

                for file in files:
                    # Skip excluded files
                    if any(pattern in file for pattern in exclude_patterns):
                        continue

                    # Skip hidden files and specific extensions
                    if file.startswith('.') and file not in ['.replit']:
                        continue

                    file_path = os.path.join(root, file)
                    # Create relative path for the zip
                    arcname = os.path.relpath(file_path, '.')
                    arcname = arcname.replace('\\', '/')  # Normalize path separators

                    try:
                        zipf.write(file_path, arcname)
                        print(f"📁 Adicionado: {arcname}")
                    except Exception as e:
                        print(f"⚠️  Erro ao adicionar {file_path}: {e}")

        # Get file size
        file_size = os.path.getsize(zip_filename)
        size_mb = file_size / (1024 * 1024)

        print(f"\n✅ Backup criado com sucesso!")
        print(f"📁 Arquivo: {zip_filename}")
        print(f"📊 Tamanho: {size_mb:.2f} MB")
        print(f"🗂️  Contém todos os arquivos essenciais do aplicativo")

        return zip_filename

    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None
    finally:
        os.chdir(original_dir)

def list_backup_contents(zip_filename):
    """List contents of a backup ZIP file"""
    if not os.path.exists(zip_filename):
        print(f"❌ Arquivo não encontrado: {zip_filename}")
        return

    try:
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            files = zipf.namelist()
            print(f"\n📋 Conteúdo do backup ({len(files)} arquivos):")
            for file in sorted(files):
                print(f"   {file}")
    except Exception as e:
        print(f"❌ Erro ao listar conteúdo: {e}")

def extract_backup(zip_filename, extract_to='extracted_backup'):
    """Extract backup to a directory"""
    if not os.path.exists(zip_filename):
        print(f"❌ Arquivo não encontrado: {zip_filename}")
        return

    try:
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            zipf.extractall(extract_to)
            print(f"✅ Backup extraído para: {extract_to}")
    except Exception as e:
        print(f"❌ Erro ao extrair backup: {e}")

if __name__ == '__main__':
    print("🗃️  Criando backup do aplicativo...")
    backup_file = create_app_backup()

    if backup_file:
        # Ask if user wants to see contents
        response = input("\n📋 Deseja ver o conteúdo do backup? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            list_backup_contents(backup_file)

        # Ask if user wants to extract for verification
        response = input("\n🗂️  Deseja extrair o backup para verificação? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            extract_backup(backup_file)