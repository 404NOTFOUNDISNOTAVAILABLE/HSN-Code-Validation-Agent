from flask import Flask, request, jsonify, render_template
from app.agent import HSNValidationAgent
from app.config import HOST, PORT, DEBUG

app = Flask(__name__)
agent = HSNValidationAgent()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    """API endpoint for validating HSN codes"""
    data = request.json
    
    # Check if input is provided
    if not data or 'hsn_codes' not in data:
        return jsonify({
            'success': False,
            'error': 'No HSN codes provided'
        }), 400
    
    # Process the input using the agent
    result = agent.process_input(data)
    
    # Format the response
    response = agent.format_response(result)
    
    return jsonify(response)

@app.route('/validate/form', methods=['POST'])
def validate_form():
    """Form-based endpoint for web interface"""
    hsn_codes = request.form.get('hsn_codes', '')
    include_hierarchy = request.form.get('include_hierarchy') == 'on'
    
    # Process the input using the agent
    input_data = {
        'hsn_codes': hsn_codes,
        'include_hierarchy': include_hierarchy
    }
    
    result = agent.process_input(input_data)
    response = agent.format_response(result)
    
    # Render results template
    return render_template('results.html', response=response)

@app.route('/api/intent', methods=['POST'])
def handle_intent():
    """API endpoint for handling intents (for conversational interfaces)"""
    data = request.json
    
    if not data or 'intent' not in data:
        return jsonify({
            'success': False,
            'error': 'No intent provided'
        }), 400
    
    intent = data['intent']
    entities = data.get('entities', {})
    
    # Handle the intent using the agent
    result = agent.handle_intent(intent, entities)
    response = agent.format_response(result)
    
    return jsonify(response)

if __name__ == '__main__':
    print(f"HSN Validation Agent starting on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)