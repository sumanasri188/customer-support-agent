import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager

DB_PATH = 'supportflow.db'

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            frustration_level INTEGER DEFAULT 5,
            browser TEXT,
            os TEXT,
            app_version TEXT,
            known_issues TEXT,
            created_at TEXT
        )
    ''')
    
    # Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            cascade_stage TEXT DEFAULT 'contact',
            solutions_used TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            ticket_id TEXT,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    ''')
    
    # Hindsight entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hindsight (
            id TEXT PRIMARY KEY,
            issue_type TEXT NOT NULL,
            what_went_wrong TEXT,
            correct_approach TEXT,
            times_triggered INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Seed initial data
    seed_data()

def seed_data():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM customers')
        if cursor.fetchone()[0] > 0:
            return
        
        # Seed customers
        customers = [
            ('c1', 'Sarah Chen', 'sarah.chen@techcorp.com', '555-0101', 'TechCorp', 7, 'Chrome 120', 'Windows 11', '2.3.1', '["login_issues", "payment_failed"]'),
            ('c2', 'Marcus Johnson', 'marcus.j@startup.io', '555-0102', 'StartupIO', 3, 'Firefox 121', 'macOS Sonoma', '2.3.0', '[]'),
            ('c3', 'Elena Rodriguez', 'elena@designlab.co', '555-0103', 'DesignLab', 8, 'Safari 17', 'macOS Ventura', '2.2.9', '["sync_error", "crash_reports"]'),
            ('c4', 'James Wilson', 'jwilson@enterprise.com', '555-0104', 'Enterprise Inc', 5, 'Edge 120', 'Windows 10', '2.3.1', '["api_timeout"]'),
            ('c5', 'Aisha Patel', 'aisha@cloudnine.io', '555-0105', 'CloudNine', 9, 'Chrome 120', 'Ubuntu 22.04', '2.3.1', '["data_loss", "permission_denied"]'),
        ]
        
        for c in customers:
            cursor.execute('''
                INSERT INTO customers (id, name, email, phone, company, frustration_level, browser, os, app_version, known_issues, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*c, datetime.now().isoformat()))
        
        # Seed tickets
        tickets = [
            ('t1', 'c1', 'Cannot access dashboard', 'Getting 403 error when trying to access the main dashboard after login.', 'open', 'diagnosis', '["cleared_cache", "checked_permissions"]', datetime.now().isoformat(), datetime.now().isoformat()),
            ('t2', 'c1', 'Payment processing failed', 'Credit card payment keeps failing with timeout error.', 'open', 'solution', '["switched_payment_gateway"]', datetime.now().isoformat(), datetime.now().isoformat()),
            ('t3', 'c2', 'Feature request: Dark mode', 'Would love to have a dark mode option in the settings.', 'resolved', 'followup', '["added_to_roadmap"]', datetime.now().isoformat(), datetime.now().isoformat()),
            ('t4', 'c3', 'App crashes on startup', 'Application crashes immediately after launching on Mac.', 'escalated', 'diagnosis', '["collected_logs"]', datetime.now().isoformat(), datetime.now().isoformat()),
            ('t5', 'c4', 'API rate limiting', 'Getting 429 errors when making bulk API calls.', 'open', 'contact', '[]', datetime.now().isoformat(), datetime.now().isoformat()),
            ('t6', 'c5', 'Lost all project data', 'All my projects disappeared after updating the app!', 'open', 'solution', '["restored_backup"]', datetime.now().isoformat(), datetime.now().isoformat()),
        ]
        
        for t in tickets:
            cursor.execute('''
                INSERT INTO tickets (id, customer_id, title, description, status, cascade_stage, solutions_used, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', t)
        
        # Seed messages
        messages = [
            ('m1', 't1', 'customer', 'I keep getting a 403 error when I try to log into my dashboard.', datetime.now().isoformat()),
            ('m2', 't1', 'agent', 'I apologize for the inconvenience. Let me check your account permissions.', datetime.now().isoformat()),
            ('m3', 't1', 'customer', 'This is really frustrating, I have a deadline today!', datetime.now().isoformat()),
            ('m4', 't4', 'customer', 'The app crashes every time I open it. I need this fixed ASAP!', datetime.now().isoformat()),
            ('m5', 't4', 'agent', 'I understand this is urgent. Can you share your system logs?', datetime.now().isoformat()),
            ('m6', 't4', 'customer', 'I already sent them in the first email. This is the 3rd time I\'m explaining!', datetime.now().isoformat()),
            ('m7', 't6', 'customer', 'ALL MY DATA IS GONE! After the update, nothing works!', datetime.now().isoformat()),
            ('m8', 't6', 'agent', 'I\'m so sorry about this. Let me check what happened with your account.', datetime.now().isoformat()),
        ]
        
        for m in messages:
            cursor.execute('''
                INSERT INTO messages (id, ticket_id, sender, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', m)
        
        # Seed HINDSIGHT entries
        hindsight_entries = [
            ('h1', 'refund_policy', 'Offered full refund for used/opened items', 'Only offer partial refunds (50%) for opened packaging. Full refund only for unopened items.', 12),
            ('h2', 'technical_glitch', 'Sent manual before checking server status', 'Always check server status first, then provide documentation if systems are operational.', 8),
            ('h3', 'login_issue', 'Reset password without verifying identity', 'Always verify customer identity through email or phone before password reset.', 15),
            ('h4', 'payment_issue', 'Suggested different payment method immediately', 'First check payment gateway status and try reprocessing before suggesting alternatives.', 10),
            ('h5', 'data_loss', 'Asked customer to reproduce the issue', 'Never ask customers to reproduce data loss. Immediately check backup systems first.', 6),
            ('h6', 'crash_report', 'Requested more logs before acknowledging', 'Acknowledge the issue first, then collect logs. Don\'t make customer feel unheard.', 9),
        ]
        
        for h in hindsight_entries:
            cursor.execute('''
                INSERT INTO hindsight (id, issue_type, what_went_wrong, correct_approach, times_triggered)
                VALUES (?, ?, ?, ?, ?)
            ''', h)
        
        conn.commit()

# Customer operations
def get_all_customers():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

def get_customer(customer_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_customer_with_history(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        return None
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get past tickets
        cursor.execute('SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
        customer['past_tickets'] = [dict(row) for row in cursor.fetchall()]
        
        # Get solutions that worked
        cursor.execute('''
            SELECT solutions_used FROM tickets 
            WHERE customer_id = ? AND solutions_used != '[]'
        ''', (customer_id,))
        all_solutions = []
        for row in cursor.fetchall():
            import json
            solutions = json.loads(row[0])
            all_solutions.extend(solutions)
        customer['what_worked_before'] = list(set(all_solutions))
        
        # Parse known issues
        import json
        customer['known_issues'] = json.loads(customer.get('known_issues', '[]'))
        
    return customer

def create_customer(data):
    customer_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (id, name, email, phone, company, frustration_level, browser, os, app_version, known_issues, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id, data['name'], data.get('email', ''), data.get('phone', ''),
            data.get('company', ''), data.get('frustration_level', 5),
            data.get('browser', ''), data.get('os', ''), data.get('app_version', ''),
            '[]', datetime.now().isoformat()
        ))
        conn.commit()
    return get_customer(customer_id)

# Ticket operations
def get_all_tickets(filters=None):
    with get_db() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM tickets'
        params = []
        
        if filters:
            conditions = []
            if filters.get('status'):
                conditions.append('status = ?')
                params.append(filters['status'])
            if filters.get('customer_id'):
                conditions.append('customer_id = ?')
                params.append(filters['customer_id'])
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_ticket(ticket_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        ticket = dict(row)
        
        # Get messages
        cursor.execute('SELECT * FROM messages WHERE ticket_id = ? ORDER BY timestamp ASC', (ticket_id,))
        ticket['messages'] = [dict(row) for row in cursor.fetchall()]
        
        # Get customer info
        cursor.execute('SELECT * FROM customers WHERE id = ?', (ticket['customer_id'],))
        customer_row = cursor.fetchone()
        if customer_row:
            ticket['customer'] = dict(customer_row)
        
        # Parse solutions
        import json
        ticket['solutions_used'] = json.loads(ticket.get('solutions_used', '[]'))
        
        return ticket

def create_ticket(data):
    ticket_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tickets (id, customer_id, title, description, status, cascade_stage, solutions_used, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_id, data['customer_id'], data['title'], data.get('description', ''),
            'open', 'contact', '[]', now, now
        ))
        
        # Add initial message if provided
        if data.get('initial_message'):
            msg_id = str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO messages (id, ticket_id, sender, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (msg_id, ticket_id, 'customer', data['initial_message'], now))
        
        conn.commit()
    
    return get_ticket(ticket_id)

def update_ticket(ticket_id, data):
    with get_db() as conn:
        cursor = conn.cursor()
        updates = []
        params = []
        
        if 'status' in data:
            updates.append('status = ?')
            params.append(data['status'])
        if 'cascade_stage' in data:
            updates.append('cascade_stage = ?')
            params.append(data['cascade_stage'])
        if 'solutions_used' in data:
            updates.append('solutions_used = ?')
            params.append(json.dumps(data['solutions_used']))
        
        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        
        params.append(ticket_id)
        
        cursor.execute(f'UPDATE tickets SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()
    
    return get_ticket(ticket_id)

def add_message(ticket_id, sender, content):
    msg_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (id, ticket_id, sender, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (msg_id, ticket_id, sender, content, timestamp))
        
        # Update ticket timestamp
        cursor.execute('UPDATE tickets SET updated_at = ? WHERE id = ?', (timestamp, ticket_id))
        
        conn.commit()
    
    return get_ticket(ticket_id)

# HINDSIGHT operations
def get_all_hindsight():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hindsight ORDER BY times_triggered DESC')
        return [dict(row) for row in cursor.fetchall()]

def get_hindsight_by_type(issue_type):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hindsight WHERE issue_type = ?', (issue_type,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_hindsight_for_ticket(issue_type):
    """Get relevant hindsight based on ticket issue type"""
    # Map ticket keywords to hindsight types
    type_mapping = {
        'refund': 'refund_policy',
        'payment': 'payment_issue',
        'login': 'login_issue',
        'crash': 'crash_report',
        'data': 'data_loss',
        'error': 'technical_glitch',
    }
    
    matched_type = type_mapping.get(issue_type.lower(), None)
    if matched_type:
        return get_hindsight_by_type(matched_type)
    return None

# CASCADEFLOW operations
def get_cascade_stages():
    return [
        {'id': 'contact', 'name': 'Initial Contact', 'description': 'Gather basic information and acknowledge the issue'},
        {'id': 'diagnosis', 'name': 'Diagnosis', 'description': 'Investigate the root cause of the issue'},
        {'id': 'solution', 'name': 'Solution', 'description': 'Implement and verify the fix'},
        {'id': 'followup', 'name': 'Follow-up', 'description': 'Confirm resolution and gather feedback'},
    ]

def advance_cascade_stage(ticket_id):
    """Advance ticket to next cascade stage"""
    ticket = get_ticket(ticket_id)
    if not ticket:
        return None
    
    stages = ['contact', 'diagnosis', 'solution', 'followup']
    current_idx = stages.index(ticket['cascade_stage']) if ticket['cascade_stage'] in stages else 0
    
    if current_idx < len(stages) - 1:
        next_stage = stages[current_idx + 1]
        return update_ticket(ticket_id, {'cascade_stage': next_stage})
    
    return ticket