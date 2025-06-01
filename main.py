from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from vedictime import VedicDateTime

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/panchanga')
def get_panchanga_api():
    try:
        # Get query parameters
        date = request.args.get('date')
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        # Parse date and create VedicDateTime instance
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        vdt = VedicDateTime(date_obj, lat, lng)
        
        # Get sunrise and sunset times
        sunrise, sunset = vdt.get_sunrise_sunset()
        
        # Calculate all panchanga elements
        tithi = vdt.get_tithi()
        nakshatra = vdt.get_nakshatra()
        
        return jsonify({
            "sunrise": sunrise.isoformat(),
            "sunset": sunset.isoformat(),
            "tithi": {
                "number": tithi["number"],
                "name": tithi["name"],
                "paksha": tithi["name"].split()[0],
                "start_time": sunrise.isoformat(),
                "end_time": tithi["ends_at"].isoformat() if "ends_at" in tithi else None
            },
            "nakshatra": {
                "number": nakshatra["number"],
                "name": nakshatra["name"],
                "start_time": sunrise.isoformat(),
                "end_time": nakshatra["ends_at"].isoformat() if "ends_at" in nakshatra else None
            },
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

@app.route('/notification-dates')
def get_notification_dates():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        types = request.args.get('types')  # comma-separated string or None
        if not (start_date and end_date and lat and lng):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Parse types
        valid_types = {"amavasya", "ekadashi", "purnima"}
        if types:
            requested_types = set(t.strip().lower() for t in types.split(",")) & valid_types
        else:
            requested_types = valid_types
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Prepare result
        result = {t: [] for t in requested_types}
        current = start_dt
        while current <= end_dt:
            vdt = VedicDateTime(current, lat, lng)
            tithi = vdt.get_tithi()
            tithi_name = tithi["name"].lower()
            if "amavasya" in requested_types and "amavasya" in tithi_name:
                result["amavasya"].append(current.strftime("%Y-%m-%d"))
            if "ekadashi" in requested_types and "ekadashi" in tithi_name:
                result["ekadashi"].append(current.strftime("%Y-%m-%d"))
            if "purnima" in requested_types and "purnima" in tithi_name:
                result["purnima"].append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 