from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from vedictime import VedicDateTime, get_panchanga

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/panchanga')
def get_panchanga_api():
    try:
        date = request.args.get('date')
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        vdt = VedicDateTime(date_obj, lat, lng)
        sunrise, sunset = vdt.get_sunrise_sunset()
        
        return jsonify({
            "sunrise": sunrise.isoformat(),
            "sunset": sunset.isoformat(),
            "tithi": vdt.get_tithi(),
            "nakshatra": vdt.get_nakshatra(),
            "yoga": vdt.get_yoga(),
            "karana": vdt.get_karana(),
            "masa": vdt.get_masa(),
            "samvatsara": vdt.get_samvatsara(),
            "ayana": vdt.get_ayana(),
            "rutu": vdt.get_rutu(),
            "solar_masa": vdt.get_solar_masa()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 