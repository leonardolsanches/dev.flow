# Overview

This is a Flask-based activity management system designed for team coordination and task tracking. The application allows managers to create, assign, and monitor activities with deadlines, while providing a director-level dashboard for oversight. The system features role-based access control with different views for managers and directors, activity status tracking with comments, and a responsive web interface built with Bootstrap.

**Current Status:** Fully functional mobile-first application with hierarchical approval system and visual dashboard. All core features implemented including multiple responsible assignment, emoji-based status visualization, mobile-optimized grid layout, and comprehensive activity management.

**Recent Updates (Aug 2025):**
- ✓ Implemented multiple responsibles per activity (list-based assignment)
- ✓ Created visual dashboard with emoji status indicators (😊 😨 😡 ⚫)
- ✓ Redesigned grid layout: activities as rows, managers as columns
- ✓ Added mobile-first responsive design with rotation suggestions
- ✓ Enhanced legend with color coding and text explanations
- ✓ Sticky columns for better navigation on mobile devices

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **UI Framework**: Bootstrap 5.3.0 with Font Awesome 6.4.0 icons for consistent styling
- **Client-side**: Vanilla JavaScript for form validation, word counters, and interactive features
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

## Backend Architecture
- **Web Framework**: Flask with session-based authentication
- **Application Structure**: Single-file application (app.py) with modular route handling
- **User Management**: Simple role-based system with predefined managers and director roles
- **Session Management**: Flask sessions with configurable secret key from environment variables

## Data Storage
- **Database**: JSON file-based storage (activities.json) for simplicity
- **Data Structure**: Hierarchical JSON with activities array and auto-incrementing IDs
- **File System**: Local data directory for persistent storage
- **Backup Strategy**: File-based system allows for easy backup and version control

## Authentication & Authorization
- **Authentication Method**: Session-based user identification without passwords
- **Role System**: Two-tier system (Managers and Director) with different permissions
- **Access Control**: Route-level restrictions based on user roles
- **Session Security**: Configurable session secret with environment variable support

## Business Logic
- **Activity Management**: CRUD operations for activities with status tracking
- **Status Workflow**: Four-state system (Pendente, Em Andamento, Concluída, Cancelada)
- **Comment System**: Five-word limit for status comments to encourage conciseness
- **History Tracking**: Activity history logging for audit trails
- **Deadline Management**: Date-based deadline tracking with visual indicators

## API Design
- **Route Structure**: RESTful-style routes for activity operations
- **Data Format**: JSON for AJAX requests and form submissions
- **Error Handling**: Flash messages for user feedback
- **Validation**: Server-side validation for all user inputs

# External Dependencies

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework from CDN for responsive design and components
- **Font Awesome 6.4.0**: Icon library from CDN for consistent iconography
- **jQuery**: Not explicitly used, relying on vanilla JavaScript and Bootstrap's built-in components

## Backend Dependencies
- **Flask**: Core web framework for Python
- **Werkzeug**: WSGI utilities including ProxyFix for deployment behind proxies
- **Python Standard Library**: JSON, OS, datetime, and logging modules for core functionality

## Infrastructure
- **File System**: Local storage for JSON data files
- **Environment Variables**: Configuration through environment variables for deployment flexibility
- **Static Assets**: Local CSS and JavaScript files served by Flask
- **Session Storage**: Server-side session management through Flask's built-in session handling

## Development Tools
- **Debug Mode**: Flask debug mode for development
- **Logging**: Python logging module for application monitoring
- **Port Configuration**: Configurable port (default 5000) for different environments