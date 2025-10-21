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

# List of managers and director
MANAGERS = ['Aline', 'Fábio', 'Marcos', 'Waldir', 'Mario', 'Washington']
DIRECTOR = 'Washington'
ACTION_STATUSES = ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada', 'Não Aplicável']

# Status emojis for visual dashboard
STATUS_EMOJIS = {
    'Pendente': {'emoji': '😡', 'color': 'danger', 'bg': '#fdeaeb'},
    'Em Andamento': {'emoji': '😨', 'color': 'warning', 'bg': '#fff3cd'},
    'Concluída': {'emoji': '😊', 'color': 'success', 'bg': '#d1f2eb'},
    'Cancelada': {'emoji': '⚫', 'color': 'secondary', 'bg': '#e9ecef'}
}

def load_data():
    """Load activities data from JSON file"""
    try:
        with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"activities": [], "next_id": 1}

def save_data(data):
    """Save activities data to JSON file"""
    with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

@app.route('/')
def index():
    """Main page showing activities list"""
    data = load_data()
    current_user = session.get('current_user', 'Aline')  # Default user for demo
    
    # Filter activities based on user role
    if current_user == DIRECTOR:
        activities = data['activities']
    else:
        # Show only activities assigned to current user
        activities = []
        for act in data['activities']:
            resp = act['responsible']
            # Check if responsible is a list or string
            if isinstance(resp, list):
                if current_user in resp:
                    activities.append(act)
            else:
                if current_user == resp:
                    activities.append(act)
    
    return render_template('index.html', 
                         activities=activities, 
                         current_user=current_user,
                         managers=MANAGERS)

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
    current_user = session.get('current_user', 'Washington')
    if current_user != DIRECTOR:
        flash('Acesso negado. Apenas o diretor pode acessar o dashboard.')
        return redirect(url_for('index'))
    
    data = load_data()
    activities = data['activities']
    
    # Filter pending justifications
    pending_justifications = [
        act for act in activities 
        if act.get('status') == 'Pendente' and act.get('justification') and not act.get('justification_approved')
    ]
    
    return render_template('dashboard.html', 
                         activities=activities,
                         pending_justifications=pending_justifications,
                         current_user=current_user,
                         managers=MANAGERS,
                         status_emojis=STATUS_EMOJIS)

@app.route('/dashboard_visual')
def dashboard_visual():
    """Visual dashboard with actions matrix"""
    current_user = session.get('current_user', 'Washington')
    if current_user != DIRECTOR:
        flash('Acesso negado. Apenas o diretor pode acessar o dashboard.')
        return redirect(url_for('index'))
    
    data = load_data()
    activities = data['activities']
    
    return render_template('dashboard_visual.html', 
                         activities=activities,
                         managers=MANAGERS,
                         current_user=current_user)

@app.route('/add_activity', methods=['GET', 'POST'])
def add_activity():
    """Add new activity"""
    current_user = session.get('current_user', 'Aline')
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline = request.form.get('deadline', '').strip()
        responsible = request.form.getlist('responsible')  # Get list of responsibles
        
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
        new_activity = {
            'id': data['next_id'],
            'title': title,
            'description': description,
            'deadline': deadline,
            'responsible': responsible,
            'status': 'Pendente',
            'created_by': current_user,
            'created_at': datetime.now().isoformat(),
            'status_comment': '',
            'justification': '',
            'justification_approved': False,
            'history': []
        }
        
        add_to_history(new_activity, 'Criada', current_user)
        
        data['activities'].append(new_activity)
        data['next_id'] += 1
        save_data(data)
        
        flash('Atividade criada com sucesso!')
        return redirect(url_for('index'))
    
    return render_template('add_activity.html', managers=MANAGERS, current_user=current_user)

@app.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    """Show activity details and allow status updates"""
    current_user = session.get('current_user', 'Aline')
    data = load_data()
    
    activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
    if not activity:
        flash('Atividade não encontrada.')
        return redirect(url_for('index'))
    
    # Check permission
    responsible = activity['responsible']
    is_responsible = False
    if isinstance(responsible, list):
        is_responsible = current_user in responsible
    else:
        is_responsible = current_user == responsible
    
    if current_user != DIRECTOR and not is_responsible:
        flash('Você não tem permissão para visualizar esta atividade.')
        return redirect(url_for('index'))
    
    return render_template('activity_detail.html', 
                         activity=activity, 
                         current_user=current_user,
                         statuses=ACTION_STATUSES)

@app.route('/update_status/<int:activity_id>', methods=['POST'])
def update_status(activity_id):
    """Update activity status"""
    current_user = session.get('current_user', 'Aline')
    data = load_data()
    
    activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
    if not activity:
        flash('Atividade não encontrada.')
        return redirect(url_for('index'))
    
    # Check permission
    responsible = activity['responsible']
    is_responsible = False
    if isinstance(responsible, list):
        is_responsible = current_user in responsible
    else:
        is_responsible = current_user == responsible
    
    if current_user != DIRECTOR and not is_responsible:
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
    
    # Update activity
    old_status = activity.get('status', '')
    activity['status'] = new_status
    activity['status_comment'] = status_comment
    
    if new_status == 'Pendente' and justification:
        activity['justification'] = justification
        activity['justification_approved'] = False
    
    # Add to history
    action = f'Status alterado de "{old_status}" para "{new_status}"'
    add_to_history(activity, action, current_user, status_comment)
    
    save_data(data)
    flash('Status atualizado com sucesso!')
    return redirect(url_for('activity_detail', activity_id=activity_id))

@app.route('/approve_justification/<int:activity_id>', methods=['POST'])
def approve_justification(activity_id):
    """Approve or reject justification (Director only)"""
    current_user = session.get('current_user', 'Washington')
    
    if current_user != DIRECTOR:
        flash('Apenas o diretor pode aprovar justificativas.')
        return redirect(url_for('index'))
    
    data = load_data()
    activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
    if not activity:
        flash('Atividade não encontrada.')
        return redirect(url_for('dashboard'))
    
    action = request.form.get('action')  # 'approve' or 'reject'
    director_comment = request.form.get('director_comment', '').strip()
    
    if action == 'approve':
        activity['justification_approved'] = True
        add_to_history(activity, 'Justificativa aprovada', current_user, director_comment)
        flash('Justificativa aprovada!')
    elif action == 'reject':
        activity['justification_approved'] = False
        activity['status'] = 'Em Andamento'  # Reset status
        add_to_history(activity, 'Justificativa rejeitada', current_user, director_comment)
        flash('Justificativa rejeitada. Status alterado para Em Andamento.')
    
    save_data(data)
    return redirect(url_for('dashboard'))

@app.route('/quick_update_status/<int:activity_id>', methods=['POST'])
def quick_update_status(activity_id):
    """Quick update activity status from dashboard"""
    current_user = session.get('current_user', 'Washington')
    data = load_data()
    
    activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
    if not activity:
        flash('Atividade não encontrada.')
        return redirect(url_for('dashboard'))
    
    # Check permission
    responsible = activity['responsible']
    is_responsible = False
    if isinstance(responsible, list):
        is_responsible = current_user in responsible
    else:
        is_responsible = current_user == responsible
    
    if current_user != DIRECTOR and not is_responsible:
        flash('Você não tem permissão para atualizar esta atividade.')
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
    
    # Update activity
    old_status = activity.get('status', '')
    activity['status'] = new_status
    activity['status_comment'] = status_comment
    
    if new_status == 'Pendente' and justification:
        activity['justification'] = justification
        activity['justification_approved'] = False
    
    # Add to history
    action = f'Status alterado de "{old_status}" para "{new_status}"'
    add_to_history(activity, action, current_user, status_comment)
    
    save_data(data)
    flash('Status atualizado com sucesso!')
    return redirect(url_for('dashboard'))

@app.route('/edit_activity/<int:activity_id>', methods=['POST'])
def edit_activity(activity_id):
    """Edit activity details"""
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
    responsible = request.form.getlist('responsible')  # Get list of responsibles
    
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
    old_values = {
        'title': activity.get('title'),
        'description': activity.get('description'),
        'deadline': activity.get('deadline'),
        'responsible': activity.get('responsible')
    }
    
    activity['title'] = title
    activity['description'] = description
    activity['deadline'] = deadline
    activity['responsible'] = responsible
    
    # Add to history
    changes = []
    if old_values['title'] != title:
        changes.append(f'título: "{old_values["title"]}" → "{title}"')
    if old_values['description'] != description:
        changes.append('descrição alterada')
    if old_values['deadline'] != deadline:
        changes.append(f'deadline: {old_values["deadline"]} → {deadline}')
    if old_values['responsible'] != responsible:
        changes.append(f'responsável: {old_values["responsible"]} → {responsible}')
    
    if changes:
        action = 'Atividade editada: ' + ', '.join(changes)
        add_to_history(activity, action, current_user)
    
    save_data(data)
    flash('Atividade atualizada com sucesso!')
    return redirect(url_for('dashboard'))

@app.route('/delete_activity/<int:activity_id>', methods=['POST'])
def delete_activity(activity_id):
    """Delete activity (Director only)"""
    current_user = session.get('current_user', 'Washington')
    
    if current_user != DIRECTOR:
        flash('Apenas o diretor pode excluir atividades.')
        return redirect(url_for('index'))
    
    data = load_data()
    activity = next((act for act in data['activities'] if act['id'] == activity_id), None)
    if not activity:
        flash('Atividade não encontrada.')
        return redirect(url_for('dashboard'))
    
    data['activities'] = [act for act in data['activities'] if act['id'] != activity_id]
    save_data(data)
    
    flash('Atividade excluída com sucesso!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
