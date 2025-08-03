
import json
import os
from datetime import datetime
import pandas as pd

def load_activities_data():
    """Load activities data from JSON file"""
    activities_file = 'data/activities.json'
    
    if not os.path.exists(activities_file):
        print("❌ Arquivo de dados não encontrado!")
        return None
    
    try:
        with open(activities_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('activities', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None

def export_to_excel():
    """Export activities data to Excel file"""
    
    # Load data
    activities = load_activities_data()
    if activities is None:
        return
    
    if not activities:
        print("⚠️  Nenhuma atividade encontrada para exportar.")
        return
    
    # Prepare data for Excel
    excel_data = []
    
    for activity in activities:
        # Handle responsible field (can be string or list)
        responsible = activity.get('responsible', '')
        if isinstance(responsible, list):
            responsible = ', '.join(responsible)
        
        # Parse dates
        try:
            created_at = datetime.fromisoformat(activity.get('created_at', '')).strftime('%d/%m/%Y %H:%M')
        except:
            created_at = activity.get('created_at', '')
        
        try:
            deadline_str = activity.get('deadline', '')
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            else:
                deadline = ''
        except:
            deadline = activity.get('deadline', '')
        
        excel_data.append({
            'ID': activity.get('id', ''),
            'Título': activity.get('title', ''),
            'Descrição': activity.get('description', ''),
            'Responsável': responsible,
            'Status': activity.get('status', ''),
            'Prazo': deadline,
            'Criado por': activity.get('created_by', ''),
            'Data de Criação': created_at,
            'Comentário': activity.get('status_comment', ''),
            'Justificativa': activity.get('justification', ''),
            'Justificativa Aprovada': 'Sim' if activity.get('justification_approved') else 'Não'
        })
    
    # Create DataFrame
    df = pd.DataFrame(excel_data)
    
    # Ensure exports directory exists
    if not os.path.exists('exports'):
        os.makedirs('exports')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exports/atividades_{timestamp}.xlsx'
    
    try:
        # Export to Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Atividades', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Atividades']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                
                adjusted_width = min(max_length + 2, 50)  # Max width of 50
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Style header row
            from openpyxl.styles import Font, PatternFill
            header_font = Font(bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='2F75B5', end_color='2F75B5', fill_type='solid')
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
        
        print(f"✅ Exportação concluída com sucesso!")
        print(f"📁 Arquivo: {filename}")
        print(f"📊 Registros exportados: {len(excel_data)}")
        
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")
        print("💡 Certifique-se de que o pandas e openpyxl estão instalados:")
        print("   pip install pandas openpyxl")

if __name__ == '__main__':
    export_to_excel()
