from flask import Flask, request, jsonify
from datetime import datetime
import pytz
from vedictime import get_panchanga
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "Hindu Calendar Panchanga API is running",
        "endpoints": {
            "/panchanga": "Get panchanga data for a specific date and location"
        }
    })

@app.route('/panchanga', methods=['GET'])
def get_panchanga_data():
    try:
        # Get parameters from request
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        lat = float(request.args.get('lat', '12.9716'))  # Default to Bangalore
        lng = float(request.args.get('lng', '77.5946'))  # Default to Bangalore
        
        # Parse date
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Calculate panchanga
        panchanga = get_panchanga(date, lat, lng)
        
        return jsonify(panchanga)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Use port from environment variable for render.com compatibility
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 