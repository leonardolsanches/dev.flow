
# Scripts de Manutenção do Sistema

Este diretório contém scripts utilitários para manutenção e gerenciamento do sistema de gestão de atividades.

## Scripts Disponíveis

### 🗃️ create_backup.py
Cria backup completo do aplicativo em formato ZIP.

**Uso:**
```bash
python create_backup.py
```

**Características:**
- Inclui todos os arquivos essenciais do aplicativo
- Exclui arquivos temporários e desnecessários
- Gera nome de arquivo com timestamp
- Mostra conteúdo do backup opcionalmente
- Permite extrair backup para verificação

**Arquivos incluídos:**
- Código fonte (*.py)
- Templates HTML
- Arquivos estáticos (CSS, JS, imagens)
- Dados da aplicação
- Configurações (.replit, pyproject.toml)

**Arquivos excluídos:**
- Cache Python (__pycache__)
- Diretórios de versionamento (.git)
- Assets anexados (attached_assets)
- Backups anteriores
- Ambientes virtuais

### 🧹 cleanup_unused.py
Remove arquivos e diretórios não utilizados do projeto.

**Uso:**
```bash
python cleanup_unused.py
```

**Remove:**
- Cache Python (__pycache__)
- Assets não utilizados (attached_assets)
- Arquivos de controle de versão
- Dependências de Node.js
- Ambientes virtuais
- Backups antigos (opcional)

### 🛠️ maintenance.py
Script principal que executa limpeza e backup em sequência.

**Uso:**
```bash
python maintenance.py
```

**Processo:**
1. Executa limpeza de arquivos não utilizados
2. Cria backup completo do aplicativo
3. Exibe relatório de manutenção

### 📊 export_to_excel.py
Exporta dados das atividades para planilha Excel.

**Uso:**
```bash
python export_to_excel.py
```

### 🗑️ reset_data.py
Reseta todos os dados para estado inicial.

**Uso:**
```bash
python reset_data.py
```

## Estrutura de Backups

Os backups são salvos no diretório `scripts/backups/` com o formato:
```
app_backup_YYYYMMDD_HHMMSS.zip
```

Exemplo: `app_backup_20250803_233206.zip`

## Manutenção Recomendada

1. **Diária:** Execute `maintenance.py` para limpeza e backup
2. **Semanal:** Verifique o tamanho dos backups e remova os mais antigos se necessário
3. **Mensal:** Execute `export_to_excel.py` para relatórios

## Permissões Necessárias

Todos os scripts devem ser executados do diretório `scripts/` e requerem:
- Permissão de leitura/escrita no diretório do projeto
- Permissão para criar/remover arquivos e diretórios

## Solução de Problemas

### Backup vazio (0 MB)
- Verifique se está executando do diretório correto
- Confirme que há arquivos para incluir no backup
- Verifique permissões de arquivo

### Erro de permissão
- Certifique-se de ter permissões adequadas
- Execute a partir do diretório correto do projeto

### Arquivos não encontrados
- Verifique se está no diretório `scripts/`
- Confirme que os caminhos dos arquivos estão corretos
