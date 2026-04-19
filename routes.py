from flask import request, jsonify
import models

def register_routes(app):
    
    # ==================== CUSTOMER ROUTES ====================
    
    @app.route('/api/customers', methods=['GET'])
    def get_customers():
        customers = models.get_all_customers()
        return jsonify(customers)
    
    @app.route('/api/customers/<customer_id>', methods=['GET'])
    def get_customer(customer_id):
        include_history = request.args.get('history', 'false').lower() == 'true'
        
        if include_history:
            customer = models.get_customer_with_history(customer_id)
        else:
            customer = models.get_customer(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(customer)
    
    @app.route('/api/customers', methods=['POST'])
    def create_customer():
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        customer = models.create_customer(data)
        return jsonify(customer), 201
    
    # ==================== TICKET ROUTES ====================
    
    @app.route('/api/tickets', methods=['GET'])
    def get_tickets():
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('customer_id'):
            filters['customer_id'] = request.args.get('customer_id')
        
        tickets = models.get_all_tickets(filters)
        return jsonify(tickets)
    
    @app.route('/api/tickets/<ticket_id>', methods=['GET'])
    def get_ticket(ticket_id):
        ticket = models.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify(ticket)
    
    @app.route('/api/tickets', methods=['POST'])
    def create_ticket():
        data = request.get_json()
        if not data or not data.get('customer_id') or not data.get('title'):
            return jsonify({'error': 'customer_id and title are required'}), 400
        
        ticket = models.create_ticket(data)
        return jsonify(ticket), 201
    
    @app.route('/api/tickets/<ticket_id>', methods=['PUT'])
    def update_ticket(ticket_id):
        data = request.get_json()
        ticket = models.update_ticket(ticket_id, data)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify(ticket)
    
    @app.route('/api/tickets/<ticket_id>/messages', methods=['POST'])
    def add_message(ticket_id):
        data = request.get_json()
        if not data or not data.get('sender') or not data.get('content'):
            return jsonify({'error': 'sender and content are required'}), 400
        
        ticket = models.add_message(ticket_id, data['sender'], data['content'])
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        return jsonify(ticket)
    
    # ==================== HINDSIGHT ROUTES ====================
    
    @app.route('/api/hindsight', methods=['GET'])
    def get_hindsight():
        entries = models.get_all_hindsight()
        return jsonify(entries)
    
    @app.route('/api/hindsight/<issue_type>', methods=['GET'])
    def get_hindsight_by_type(issue_type):
        entry = models.get_hindsight_by_type(issue_type)
        if not entry:
            return jsonify({'error': 'Hindsight entry not found'}), 404
        return jsonify(entry)
    
    @app.route('/api/hindsight/ticket/<ticket_id>', methods=['GET'])
    def get_hindsight_for_ticket(ticket_id):
        """Get relevant hindsight for a ticket based on its content"""
        ticket = models.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Extract keywords from title and description
        text = f"{ticket.get('title', '')} {ticket.get('description', '')}".lower()
        
        # Find matching hindsight
        for keyword, hindsight_type in [
            ('refund', 'refund_policy'),
            ('payment', 'payment_issue'),
            ('login', 'login_issue'),
            ('crash', 'crash_report'),
            ('data', 'data_loss'),
            ('error', 'technical_glitch'),
        ]:
            if keyword in text:
                entry = models.get_hindsight_by_type(hindsight_type)
                if entry:
                    return jsonify(entry)
        
        return jsonify(None)
    
    # ==================== CASCADEFLOW ROUTES ====================
    
    @app.route('/api/cascade/stages', methods=['GET'])
    def get_cascade_stages():
        stages = models.get_cascade_stages()
        return jsonify(stages)
    
    @app.route('/api/tickets/<ticket_id>/cascade', methods=['POST'])
    def advance_cascade(ticket_id):
        ticket = models.advance_cascade_stage(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found or already at final stage'}), 404
        
        return jsonify(ticket)
    
    # ==================== SEARCH ROUTES ====================
    
    @app.route('/api/search', methods=['GET'])
    def search():
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({'customers': [], 'tickets': []})
        
        # Search customers
        customers = models.get_all_customers()
        matching_customers = [c for c in customers if query in c.get('name', '').lower() or query in c.get('email', '').lower()]
        
        # Search tickets
        tickets = models.get_all_tickets()
        matching_tickets = [t for t in tickets if query in t.get('title', '').lower() or query in t.get('description', '').lower()]
        
        return jsonify({
            'customers': matching_customers[:5],
            'tickets': matching_tickets[:5]
        })