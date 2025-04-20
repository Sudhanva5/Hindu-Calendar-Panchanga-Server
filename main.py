from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from vedictime import VedicDateTime

app = FastAPI(
    title="Panchanga API",
    description="API for Hindu Panchanga calculations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your iOS app's domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/panchanga")
async def get_panchanga(date: str, lat: float, lng: float):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        vdt = VedicDateTime(date_obj, lat, lng)
        
        return {
            "sunrise": vdt.get_sunrise().isoformat(),
            "sunset": vdt.get_sunset().isoformat(),
            "tithi": vdt.get_tithi(),
            "nakshatra": vdt.get_nakshatra(),
            "yoga": vdt.get_yoga(),
            "karana": vdt.get_karana(),
            "masa": vdt.get_masa(),
            "samvatsara": vdt.get_samvatsara(),
            "ayana": vdt.get_ayana(),
            "ritu": vdt.get_rutu(),
            "solar_masa": vdt.get_solar_masa()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 