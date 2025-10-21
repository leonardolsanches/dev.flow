
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize JSON file if it doesn't exist
ACTIVITIES_FILE = 'data/activities.json'
if not os.path.exists(ACTIVITIES_FILE):
    with open(ACTIVITIES_FILE, 'w') as f:
        json.dump({"activities": [], "next_id": 1}, f)

# Import responsibles management
RESPONSIBLES_FILE = 'data/responsibles.json'

def load_responsibles():
    """Carrega a lista de responsáveis do arquivo"""
    try:
        with open(RESPONSIBLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Lista padrão inicial - será criada automaticamente
        default = {
            "managers": ['Aline', 'Fábio', 'Marcos', 'Waldir', 'Mario', 'Washington', 'Wollinger'],
            "director": "Washington"
        }
        # Criar o arquivo com valores padrão
        with open(RESPONSIBLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

# Carregar responsáveis do arquivo
_responsibles_data = load_responsibles()
MANAGERS = _responsibles_data['managers']
DIRECTOR = _responsibles_data['director']
ACTION_STATUSES = ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada', 'Não Aplicável']

# Status emojis for visual dashboard
STATUS_EMOJIS = {
    'Pendente': {'emoji': '😡', 'color': 'danger', 'bg': '#fdeaeb'},
    'Em Andamento': {'emoji': '😨', 'color': 'warning', 'bg': '#fff3cd'},
    'Concluída': {'emoji': '😊', 'color': 'success', 'bg': '#d1f2eb'},
    'Cancelada': {'emoji': '⚫', 'color': 'secondary', 'bg': '#e9ecef'},
    'Não Aplicável': {'emoji': '⚪', 'color': 'light', 'bg': '#f8f9fa'}
}

def load_data():
    """Load activities data from JSON file"""
    try:
        with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading data: {e}")
        return {"activities": [], "next_id": 1}

def save_data(data):
    """Save activities data to JSON file"""
    try:
        with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        raise

def validate_comment(comment):
    """Validate that comment has maximum 5 words"""
    if not comment:
        return True
    words = comment.strip().split()
    return len(words) <= 5

def add_to_history(activity, action, user, comment=""):
    """Add an entry to activity history"""
    if 'history' not in activity:
        activity['history'] = []
    
    activity['history'].append({
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'user': user,
        'comment': comment
    })

def reload_responsibles():
    """Recarrega a lista de responsáveis do arquivo"""
    global MANAGERS, DIRECTOR
    _responsibles_data = load_responsibles()
    MANAGERS = _responsibles_data['managers']
    DIRECTOR = _responsibles_data['director']

def get_activity_overall_status(activity):
    """Calculate overall activity status based on individual statuses"""
    if 'responsible_status' not in activity or not activity['responsible_status']:
        return 'Pendente'
    
    statuses = [s.get('status', 'Pendente') for s in activity['responsible_status'].values()]
    
    if not statuses:
        return 'Pendente'
    
    # If all completed, activity is completed
    if all(s == 'Concluída' for s in statuses):
        return 'Concluída'
    
    # If all cancelled or NA, activity is cancelled
    if all(s in ['Cancelada', 'Não Aplicável'] for s in statuses):
        return 'Cancelada'
    
    # If any in progress, activity is in progress
    if any(s == 'Em Andamento' for s in statuses):
        return 'Em Andamento'
    
    # Otherwise, pending
    return 'Pendente'

@app.route('/')
def index():
    """Main page showing activities list"""
    try:
        reload_responsibles()  # Recarregar responsáveis
        data = load_data()
        current_user = session.get('current_user', 'Aline')
        
        # Filter activities based on user role
        if current_user == DIRECTOR:
            activities = data['activities']
        else:
            # Show only activities assigned to current user
            activities = [act for act in data['activities'] 
                         if current_user in act.get('responsible', [])]
        
        # Calculate overall status for each activity
        for activity in activities:
            activity['overall_status'] = get_activity_overall_status(activity)
        
        return render_template('index.html', 
                             activities=activities, 
                             current_user=current_user,
                             managers=MANAGERS)
    except Exception as e:
        logging.error(f"Error in index: {e}")
        flash('Erro ao carregar atividades.')
        return render_template('index.html', activities=[], current_user='Aline', managers=MANAGERS)

@app.route('/set_user/<username>')
def set_user(username):
    """Set current user (for demo purposes)"""
    if username in MANAGERS:
        session['current_user'] = username
        flash(f'Usuário alterado para {username}')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Director dashboard for approval management"""
    try:
        reload_responsibles()  # Recarregar responsáveis
        current_user = session.get('current_user', 'Washington')
        if current_user != DIRECTOR:
            flash('Acesso negado. Apenas o diretor pode acessar o dashboard.')
            return redirect(url_for('index'))
        
        data = load_data()
        activities = data.get('activities', [])
        
        # Initialize responsible_status for activities that don't have it
        for activity in activities:
            if 'responsible_status' not in activity:
                activity['responsible_status'] = {}
                responsible_list = activity.get('responsible', [])
                if isinstance(responsible_list, str):
                    responsible_list = [responsible_list]
                for person in responsible_list:
                    activity['responsible_status'][person] = {
                        'status': 'Pendente',
                        'comment': '',
                        'justification': '',
                        'justification_approved': False
                    }
            
            # Calculate overall status for each activity
            activity['overall_status'] = get_activity_overall_status(activity)
            
            # Ensure responsible is always a list for template
            if isinstance(activity.get('responsible'), str):
                activity['responsible'] = [activity['responsible']]
        
        # Filter pending justifications
        pending_justifications = []
        for act in activities:
            if 'responsible_status' in act:
                for person, status_info in act['responsible_status'].items():
                    if (status_info.get('status') == 'Pendente' and 
                        status_info.get('justification') and 
                        not status_info.get('justification_approved')):
                        pending_justifications.append({
                            'activity': act,
                            'person': person,
                            'status_info': status_info
                        })
        
        return render_template('dashboard.html', 
                             activities=activities,
                             pending_justifications=pending_justifications,
                             current_user=current_user,
                             managers=MANAGERS,
                             status_emojis=STATUS_EMOJIS)
    except Exception as e:
        logging.error(f"Error in dashboard: {e}", exc_info=True)
        flash('Erro ao carregar dashboard.')
        return render_template('dashboard.html', 
                             activities=[],
                             pending_justifications=[],
                             current_user=current_user,
                             managers=MANAGERS,
                             status_emojis=STATUS_EMOJIS)

@app.route('/add_activity', methods=['GET', 'POST'])
def add_activity():
    """Add new activity"""
    reload_responsibles()  # Recarregar responsáveis
    current_user = session.get('current_user', 'Aline')
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            deadline = request.form.get('deadline', '').strip()
            responsible = request.form.getlist('responsible')
            
            # Validation
            if not all([title, description, deadline]) or not responsible:
                flash('Todos os campos são obrigatórios.')
                return render_template('add_activity.html', managers=MANAGERS, current_user=current_user)
            
            # Validate all responsibles
            for resp in responsible:
                if resp not in MANAGERS:
                    flash('Responsável inválido.')
                    return render_template('add_activity.html', managers=MANAGERS, current_user=current_user)
            
            # Load data and add new activity
            data = load_data()
            
            # Initialize individual status for each responsible
            responsible_status = {}
            for person in responsible:
                responsible_status[person] = {
                    'status': 'Pendente',
                    'comment': '',
                    'justification': '',
                    'justification_approved': False
                }
            
            new_activity = {
                'id': data['next_id'],
                'title': title,
                'description': description,
                'deadline': deadline,
                'responsible': responsible,
                'responsible_status': responsible_status,
                'created_by': current_user,
                'created_at': datetime.now().isoformat(),
                'history': []
            }
            
            add_to_history(new_activity, 'Criada', current_user)
            
            data['activities'].append(new_activity)
            data['next_id'] += 1
            save_data(data)
            
            flash('Atividade criada com sucesso!')
            return redirect(url_for('index'))
        except Exception as e:
            logging.error(f"Error adding activity: {e}")
            flash('Erro ao criar atividade.')
            return render_template('add_activity.html', managers=MANAGERS, current_user=current_user)
    
    return render_template('add_activity.html', managers=MANAGERS, current_user=current_user)

@app.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    """Show activity details and allow status updates"""
    try:
        current_user = session.get('current_user', 'Aline')
        data = load_data()
        
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(url_for('index'))
        
        # Check permission
        if current_user != DIRECTOR and current_user not in activity.get('responsible', []):
            flash('Você não tem permissão para visualizar esta atividade.')
            return redirect(url_for('index'))
        
        activity['overall_status'] = get_activity_overall_status(activity)
        
        return render_template('activity_detail.html', 
                             activity=activity, 
                             current_user=current_user,
                             statuses=ACTION_STATUSES,
                             status_emojis=STATUS_EMOJIS)
    except Exception as e:
        logging.error(f"Error in activity_detail: {e}")
        flash('Erro ao carregar atividade.')
        return redirect(url_for('index'))

@app.route('/update_status/<int:activity_id>', methods=['POST'])
def update_status(activity_id):
    """Update activity status for current user"""
    try:
        current_user = session.get('current_user', 'Aline')
        data = load_data()
        
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(url_for('index'))
        
        # Check permission
        if current_user != DIRECTOR and current_user not in activity.get('responsible', []):
            flash('Você não tem permissão para atualizar esta atividade.')
            return redirect(url_for('index'))
        
        new_status = request.form.get('status')
        status_comment = request.form.get('status_comment', '').strip()
        justification = request.form.get('justification', '').strip()
        
        # Validate status
        if new_status not in ACTION_STATUSES:
            flash('Status inválido.')
            return redirect(url_for('activity_detail', activity_id=activity_id))
        
        # Validate comment length (5 words max)
        if status_comment and not validate_comment(status_comment):
            flash('Comentário deve ter no máximo 5 palavras.')
            return redirect(url_for('activity_detail', activity_id=activity_id))
        
        # Check if justification is required for pending status
        if new_status == 'Pendente' and not justification:
            flash('Justificativa é obrigatória para status pendente.')
            return redirect(url_for('activity_detail', activity_id=activity_id))
        
        # Initialize responsible_status if not exists
        if 'responsible_status' not in activity:
            activity['responsible_status'] = {}
            for person in activity.get('responsible', []):
                activity['responsible_status'][person] = {
                    'status': 'Pendente',
                    'comment': '',
                    'justification': '',
                    'justification_approved': False
                }
        
        # Update status for current user
        old_status = activity['responsible_status'].get(current_user, {}).get('status', 'Pendente')
        
        activity['responsible_status'][current_user] = {
            'status': new_status,
            'comment': status_comment,
            'justification': justification if new_status == 'Pendente' else '',
            'justification_approved': False
        }
        
        # Add to history
        action = f'{current_user}: Status alterado de "{old_status}" para "{new_status}"'
        add_to_history(activity, action, current_user, status_comment)
        
        save_data(data)
        flash('Status atualizado com sucesso!')
        return redirect(url_for('activity_detail', activity_id=activity_id))
    except Exception as e:
        logging.error(f"Error updating status: {e}")
        flash('Erro ao atualizar status.')
        return redirect(url_for('index'))

@app.route('/approve_justification/<int:activity_id>/<person>', methods=['POST'])
def approve_justification(activity_id, person):
    """Approve or reject justification (Director only)"""
    try:
        current_user = session.get('current_user', 'Washington')
        
        if current_user != DIRECTOR:
            flash('Apenas o diretor pode aprovar justificativas.')
            return redirect(url_for('index'))
        
        data = load_data()
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(url_for('dashboard'))
        
        action = request.form.get('action')
        director_comment = request.form.get('director_comment', '').strip()
        
        if person not in activity.get('responsible_status', {}):
            flash('Pessoa não encontrada na atividade.')
            return redirect(url_for('dashboard'))
        
        if action == 'approve':
            activity['responsible_status'][person]['justification_approved'] = True
            add_to_history(activity, f'Justificativa de {person} aprovada', current_user, director_comment)
            flash(f'Justificativa de {person} aprovada!')
        elif action == 'reject':
            activity['responsible_status'][person]['justification_approved'] = False
            activity['responsible_status'][person]['status'] = 'Em Andamento'
            add_to_history(activity, f'Justificativa de {person} rejeitada', current_user, director_comment)
            flash(f'Justificativa de {person} rejeitada. Status alterado para Em Andamento.')
        
        save_data(data)
        return redirect(url_for('dashboard'))
    except Exception as e:
        logging.error(f"Error approving justification: {e}")
        flash('Erro ao processar justificativa.')
        return redirect(url_for('dashboard'))

@app.route('/quick_update_status/<int:activity_id>/<person>', methods=['POST'])
def quick_update_status(activity_id, person):
    """Quick update activity status from dashboard"""
    try:
        current_user = session.get('current_user', 'Washington')
        data = load_data()
        
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(url_for('dashboard'))
        
        # Check permission
        if current_user != DIRECTOR and current_user != person:
            flash('Você não tem permissão para atualizar este status.')
            return redirect(url_for('dashboard'))
        
        new_status = request.form.get('status')
        status_comment = request.form.get('status_comment', '').strip()
        justification = request.form.get('justification', '').strip()
        
        # Validate status
        if new_status not in ACTION_STATUSES:
            flash('Status inválido.')
            return redirect(url_for('dashboard'))
        
        # Validate comment length
        if status_comment and not validate_comment(status_comment):
            flash('Comentário deve ter no máximo 5 palavras.')
            return redirect(url_for('dashboard'))
        
        # Check justification for pending status
        if new_status == 'Pendente' and not justification:
            flash('Justificativa é obrigatória para status pendente.')
            return redirect(url_for('dashboard'))
        
        # Initialize responsible_status if not exists
        if 'responsible_status' not in activity:
            activity['responsible_status'] = {}
            for p in activity.get('responsible', []):
                activity['responsible_status'][p] = {
                    'status': 'Pendente',
                    'comment': '',
                    'justification': '',
                    'justification_approved': False
                }
        
        # Update status for person
        old_status = activity['responsible_status'].get(person, {}).get('status', 'Pendente')
        
        activity['responsible_status'][person] = {
            'status': new_status,
            'comment': status_comment,
            'justification': justification if new_status == 'Pendente' else '',
            'justification_approved': False
        }
        
        # Add to history
        action = f'{person}: Status alterado de "{old_status}" para "{new_status}"'
        add_to_history(activity, action, current_user, status_comment)
        
        save_data(data)
        flash('Status atualizado com sucesso!')
        return redirect(url_for('dashboard'))
    except Exception as e:
        logging.error(f"Error in quick_update_status: {e}")
        flash('Erro ao atualizar status.')
        return redirect(url_for('dashboard'))

@app.route('/edit_activity/<int:activity_id>', methods=['POST'])
def edit_activity(activity_id):
    """Edit activity details"""
    try:
        current_user = session.get('current_user', 'Washington')
        
        if current_user != DIRECTOR:
            flash('Apenas o diretor pode editar atividades.')
            return redirect(url_for('dashboard'))
        
        data = load_data()
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(url_for('dashboard'))
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline', '').strip()
        responsible = request.form.getlist('responsible')
        
        # Validation
        if not all([title, description, deadline]) or not responsible:
            flash('Todos os campos são obrigatórios.')
            return redirect(url_for('dashboard'))
        
        # Validate all responsibles
        for resp in responsible:
            if resp not in MANAGERS:
                flash('Responsável inválido.')
                return redirect(url_for('dashboard'))
        
        # Update activity
        old_responsible = activity.get('responsible', [])
        activity['title'] = title
        activity['description'] = description
        activity['deadline'] = deadline
        activity['responsible'] = responsible
        
        # Update responsible_status if responsibles changed
        if set(old_responsible) != set(responsible):
            if 'responsible_status' not in activity:
                activity['responsible_status'] = {}
            
            # Add new responsibles
            for person in responsible:
                if person not in activity['responsible_status']:
                    activity['responsible_status'][person] = {
                        'status': 'Pendente',
                        'comment': '',
                        'justification': '',
                        'justification_approved': False
                    }
            
            # Remove old responsibles
            for person in old_responsible:
                if person not in responsible:
                    activity['responsible_status'].pop(person, None)
        
        add_to_history(activity, 'Atividade editada', current_user)
        
        save_data(data)
        flash('Atividade atualizada com sucesso!')
        return redirect(url_for('dashboard'))
    except Exception as e:
        logging.error(f"Error editing activity: {e}")
        flash('Erro ao editar atividade.')
        return redirect(url_for('dashboard'))

@app.route('/delete_activity/<int:activity_id>', methods=['POST'])
def delete_activity(activity_id):
    """Delete activity (Director only)"""
    try:
        current_user = session.get('current_user', 'Washington')
        
        if current_user != DIRECTOR:
            flash('Apenas o diretor pode excluir atividades.')
            return redirect(url_for('index'))
        
        # Get the referrer to redirect back
        referrer = request.referrer or url_for('index')
        
        data = load_data()
        activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
        if not activity:
            flash('Atividade não encontrada.')
            return redirect(referrer)
        
        data['activities'] = [act for act in data['activities'] if act['id'] != activity_id]
        save_data(data)
        
        flash('Atividade excluída com sucesso!')
        return redirect(referrer)
    except Exception as e:
        logging.error(f"Error deleting activity: {e}")
        flash('Erro ao excluir atividade.')
        return redirect(request.referrer or url_for('index'))

@app.route('/manage_responsibles', methods=['GET', 'POST'])
def manage_responsibles():
    """Manage responsibles (Director only)"""
    try:
        current_user = session.get('current_user', 'Washington')
        
        if current_user != DIRECTOR:
            flash('Apenas o diretor pode gerenciar responsáveis.')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            name = request.form.get('name', '').strip()
            
            if action == 'add':
                if not name:
                    flash('Nome inválido!')
                    return redirect(url_for('manage_responsibles'))
                
                responsibles = load_responsibles()
                
                if name in responsibles['managers']:
                    flash(f'{name} já existe na lista de responsáveis!')
                    return redirect(url_for('manage_responsibles'))
                
                responsibles['managers'].append(name)
                responsibles['managers'].sort()
                save_responsibles(responsibles)
                
                # Reload responsibles globally
                reload_responsibles()
                
                flash(f'{name} adicionado com sucesso!')
                return redirect(url_for('manage_responsibles'))
            
            elif action == 'remove':
                if not name:
                    flash('Nome inválido!')
                    return redirect(url_for('manage_responsibles'))
                
                responsibles = load_responsibles()
                
                if name not in responsibles['managers']:
                    flash(f'{name} não encontrado na lista!')
                    return redirect(url_for('manage_responsibles'))
                
                if name == responsibles['director']:
                    flash('Não é possível remover o diretor!')
                    return redirect(url_for('manage_responsibles'))
                
                # Check if has activities
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
                    flash(f'{name} possui atividades atribuídas e não pode ser removido!')
                    return redirect(url_for('manage_responsibles'))
                
                responsibles['managers'].remove(name)
                save_responsibles(responsibles)
                
                # Reload responsibles globally
                reload_responsibles()
                
                flash(f'{name} removido com sucesso!')
                return redirect(url_for('manage_responsibles'))
        
        # GET request - show form
        reload_responsibles()
        
        # Count activities per responsible
        data = load_data()
        activity_counts = {}
        for manager in MANAGERS:
            count = 0
            for activity in data['activities']:
                if isinstance(activity.get('responsible'), list):
                    if manager in activity['responsible']:
                        count += 1
                elif activity.get('responsible') == manager:
                    count += 1
            activity_counts[manager] = count
        
        return render_template('manage_responsibles.html',
                             current_user=current_user,
                             managers=MANAGERS,
                             director=DIRECTOR,
                             activity_counts=activity_counts)
    except Exception as e:
        logging.error(f"Error managing responsibles: {e}")
        flash('Erro ao gerenciar responsáveis.')
        return redirect(url_for('index'))

def save_responsibles(data):
    """Salva a lista de responsáveis no arquivo"""
    with open(RESPONSIBLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
